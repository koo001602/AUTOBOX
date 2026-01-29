"""
OCR 학습 데이터 생성기
운송장 이미지 템플릿을 기반으로 텍스트만 변경한 합성 이미지와 JSON 라벨 데이터를 생성합니다.

설정 조절: label_editor.py를 실행하여 GUI에서 영역을 조절한 후 저장하면
자동으로 label_config.json에서 설정을 불러옵니다.
"""

import json
import random
import argparse
import multiprocessing as mp
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
from functools import partial

from PIL import Image, ImageDraw, ImageFont, ImageFilter
from faker import Faker
from tqdm import tqdm


# 한국어 Faker 인스턴스
fake = Faker('ko_KR')

# 설정 파일 경로
CONFIG_FILE = Path(__file__).parent / "label_config.json"
EFFECT_CONFIG_FILE = Path(__file__).parent / "effect_config.json"


def load_effect_config():
    """효과 설정 로드"""
    default = {
        'apply_effect': True,
        'effect_ratios': {'none': 100},  # 효과별 비율
        'effect_strength': 5,
        'random_strength': False,
    }
    if EFFECT_CONFIG_FILE.exists():
        try:
            with open(EFFECT_CONFIG_FILE, 'r') as f:
                return {**default, **json.load(f)}
        except:
            pass
    return default


def select_effect_by_ratio(effect_ratios: dict) -> str:
    """비율에 따라 효과 선택"""
    if not effect_ratios:
        return 'none'
    
    # 비율을 누적 확률로 변환
    total = sum(effect_ratios.values())
    if total == 0:
        return 'none'
    
    rand_val = random.random() * total
    cumulative = 0
    
    for effect, ratio in effect_ratios.items():
        cumulative += ratio
        if rand_val <= cumulative:
            return effect
    
    return list(effect_ratios.keys())[-1]


def apply_single_effect(image: Image.Image, effect_type: str, strength: int) -> Image.Image:
    """단일 효과 적용"""
    if effect_type == 'none':
        return image
    elif effect_type == 'blur':
        return image.filter(ImageFilter.GaussianBlur(radius=strength))
    elif effect_type == 'mosaic':
        small = image.resize((image.width // (strength + 1), image.height // (strength + 1)), 
                            Image.Resampling.BILINEAR)
        return small.resize(image.size, Image.Resampling.NEAREST)
    elif effect_type == 'noise':
        img_copy = image.copy()
        pixels = img_copy.load()
        for i in range(img_copy.width):
            for j in range(img_copy.height):
                if random.random() < strength / 100:
                    r, g, b = pixels[i, j][:3]
                    noise = random.randint(-strength * 5, strength * 5)
                    pixels[i, j] = (
                        max(0, min(255, r + noise)),
                        max(0, min(255, g + noise)),
                        max(0, min(255, b + noise))
                    )
        return img_copy
    elif effect_type == 'combined':
        # 복합 효과: blur + noise
        img = image.filter(ImageFilter.GaussianBlur(radius=strength // 2 + 1))
        pixels = img.load()
        for i in range(img.width):
            for j in range(img.height):
                if random.random() < strength / 150:
                    r, g, b = pixels[i, j][:3]
                    noise = random.randint(-strength * 3, strength * 3)
                    pixels[i, j] = (
                        max(0, min(255, r + noise)),
                        max(0, min(255, g + noise)),
                        max(0, min(255, b + noise))
                    )
        return img
    
    return image


def apply_image_effect(image: Image.Image, effect_config: dict, selected_effect: str = None) -> tuple:
    """이미지에 효과 적용
    
    Returns:
        tuple: (처리된 이미지, 적용된 효과명)
    """
    if not effect_config.get('apply_effect', False):
        return image, 'none'
    
    # 효과 선택 (이미 선택된 효과가 있으면 사용, 없으면 비율에 따라 선택)
    if selected_effect is None:
        effect_ratios = effect_config.get('effect_ratios', {'none': 100})
        selected_effect = select_effect_by_ratio(effect_ratios)
    
    strength = effect_config.get('effect_strength', 5)
    
    # 랜덤 강도
    if effect_config.get('random_strength', False):
        strength = random.randint(1, strength)
    
    result_image = apply_single_effect(image, selected_effect, strength)
    return result_image, selected_effect


@dataclass
class ShippingLabelField:
    """운송장 필드 정의"""
    name: str                    # 필드명
    bbox: tuple                  # (x1, y1, x2, y2) 바운딩 박스
    font_size: int               # 폰트 크기 (auto_fit=False일 때 사용)
    font_color: tuple = (0, 0, 0)  # RGB 색상 (기본: 검정)
    font_bold: bool = False      # 굵은 폰트 여부
    auto_fit: bool = True        # True: bbox에 맞게 자동 조절, False: font_size 값 그대로 사용


def load_field_config():
    """설정 파일에서 필드 설정 로드"""
    # 기본 설정
    default_fields = {
        'tracking_number': {'text': [35, 115, 440, 210], 'font_size': 75, 'auto_fit': True},
        'region_code': {'text': [905, 90, 1265, 220], 'font_size': 110, 'auto_fit': True},
        'recipient_name': {'text': [60, 270, 580, 365], 'font_size': 80, 'auto_fit': True},
        'recipient_address': {'text': [20, 380, 1260, 490], 'font_size': 68, 'auto_fit': True},
        'sender_name': {'text': [80, 520, 580, 615], 'font_size': 68, 'auto_fit': True},
        'sender_address': {'text': [20, 660, 1260, 760], 'font_size': 68, 'auto_fit': True},
    }
    
    # 설정 파일이 있으면 로드
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                for key in default_fields:
                    if key in config:
                        default_fields[key]['text'] = config[key].get('text', default_fields[key]['text'])
                        default_fields[key]['font_size'] = config[key].get('font_size', default_fields[key]['font_size'])
                        default_fields[key]['auto_fit'] = config[key].get('auto_fit', default_fields[key]['auto_fit'])
            print(f"설정 파일 로드됨: {CONFIG_FILE}")
        except Exception as e:
            print(f"설정 파일 로드 실패, 기본값 사용: {e}")
    
    # ShippingLabelField 객체로 변환
    fields = {}
    for key, data in default_fields.items():
        fields[key] = ShippingLabelField(
            name=key,
            bbox=tuple(data['text']),
            font_size=data['font_size'],
            font_color=(30, 30, 30),
            font_bold=True,
            auto_fit=data['auto_fit']
        )
    
    return fields


def load_mask_config():
    """설정 파일에서 마스킹 영역 로드"""
    # 기본 설정
    default_masks = {
        'tracking_number': [25, 65, 460, 230],
        'region_code': [890, 60, 1280, 240],
        'recipient_name': [50, 235, 600, 380],
        'recipient_address': [10, 330, 1275, 510],
        'sender_name': [70, 475, 600, 630],
        'sender_address': [10, 580, 1275, 860],
    }
    
    # 설정 파일이 있으면 로드
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                for key in default_masks:
                    if key in config and 'mask' in config[key]:
                        default_masks[key] = config[key]['mask']
        except:
            pass
    
    return default_masks


# 설정 파일에서 로드
SHIPPING_LABEL_FIELDS = load_field_config()
MASK_REGIONS = load_mask_config()

# 한국 주요 도시 목록 (지역 코드용)
KOREAN_CITIES = [
    # 광역시/특별시
    '서울', '부산', '대구', '인천', '광주', '대전', '울산', '세종',
    # 경기도
    '수원', '성남', '고양', '용인', '안산', '안양', '남양주', '화성', '평택', '의정부', 
    '시흥', '파주', '김포', '광명', '광주', '군포', '오산', '이천', '안성', '양주',
    '포천', '여주', '동두천', '과천', '구리', '하남', '양평', '가평', '연천',
    # 강원도
    '춘천', '원주', '강릉', '동해', '태백', '속초', '삼척', '홍천', '횡성', '영월',
    '평창', '정선', '철원', '화천', '양구', '인제', '고성', '양양',
    # 충청북도
    '청주', '충주', '제천', '보은', '옥천', '영동', '증평', '진천', '괴산', '음성', '단양',
    # 충청남도
    '천안', '공주', '보령', '아산', '서산', '논산', '계룡', '당진', '금산', '부여',
    '서천', '청양', '홍성', '예산', '태안',
    # 전라북도
    '전주', '군산', '익산', '정읍', '남원', '김제', '완주', '진안', '무주', '장수',
    '임실', '순창', '고창', '부안',
    # 전라남도
    '목포', '여수', '순천', '나주', '광양', '담양', '곡성', '구례', '고흥', '보성',
    '화순', '장흥', '강진', '해남', '영암', '무안', '함평', '영광', '장성', '완도',
    '진도', '신안',
    # 경상북도
    '포항', '경주', '김천', '안동', '구미', '영주', '영천', '상주', '문경', '경산',
    '군위', '의성', '청송', '영양', '영덕', '청도', '고령', '성주', '칠곡', '예천',
    '봉화', '울진', '울릉',
    # 경상남도
    '창원', '진주', '통영', '사천', '김해', '밀양', '거제', '양산', '의령', '함안',
    '창녕', '고성', '남해', '하동', '산청', '함양', '거창', '합천',
    # 제주
    '제주', '서귀포'
]

# 한국 도/시 목록
KOREAN_PROVINCES = [
    '서울특별시', '부산광역시', '대구광역시', '인천광역시', '광주광역시',
    '대전광역시', '울산광역시', '세종특별자치시', '경기도', '강원도',
    '충청북도', '충청남도', '전라북도', '전라남도', '경상북도', '경상남도', '제주특별자치도'
]

# 구/군 목록 (전국)
KOREAN_DISTRICTS = {
    '서울특별시': ['강남구', '강동구', '강북구', '강서구', '관악구', '광진구', '구로구', '금천구', '노원구', '도봉구', '동대문구', '동작구', '마포구', '서대문구', '서초구', '성동구', '성북구', '송파구', '양천구', '영등포구', '용산구', '은평구', '종로구', '중구', '중랑구'],
    '부산광역시': ['강서구', '금정구', '기장군', '남구', '동구', '동래구', '부산진구', '북구', '사상구', '사하구', '서구', '수영구', '연제구', '영도구', '중구', '해운대구'],
    '대구광역시': ['남구', '달서구', '달성군', '동구', '북구', '서구', '수성구', '중구', '군위군'],
    '인천광역시': ['강화군', '계양구', '남동구', '동구', '미추홀구', '부평구', '서구', '연수구', '옹진군', '중구'],
    '광주광역시': ['광산구', '남구', '동구', '북구', '서구'],
    '대전광역시': ['대덕구', '동구', '서구', '유성구', '중구'],
    '울산광역시': ['남구', '동구', '북구', '울주군', '중구'],
    '세종특별자치시': ['세종시'],
    '경기도': ['수원시 장안구', '수원시 권선구', '수원시 팔달구', '수원시 영통구', '성남시 수정구', '성남시 중원구', '성남시 분당구', '의정부시', '안양시 만안구', '안양시 동안구', '부천시', '광명시', '평택시', '동두천시', '안산시 상록구', '안산시 단원구', '고양시 덕양구', '고양시 일산동구', '고양시 일산서구', '과천시', '구리시', '남양주시', '오산시', '시흥시', '군포시', '의왕시', '하남시', '용인시 처인구', '용인시 기흥구', '용인시 수지구', '파주시', '이천시', '안성시', '김포시', '화성시', '광주시', '양주시', '포천시', '여주시', '연천군', '가평군', '양평군'],
    '강원도': ['춘천시', '원주시', '강릉시', '동해시', '태백시', '속초시', '삼척시', '홍천군', '횡성군', '영월군', '평창군', '정선군', '철원군', '화천군', '양구군', '인제군', '고성군', '양양군'],
    '충청북도': ['청주시 상당구', '청주시 서원구', '청주시 흥덕구', '청주시 청원구', '충주시', '제천시', '보은군', '옥천군', '영동군', '증평군', '진천군', '괴산군', '음성군', '단양군'],
    '충청남도': ['천안시 동남구', '천안시 서북구', '공주시', '보령시', '아산시', '서산시', '논산시', '계룡시', '당진시', '금산군', '부여군', '서천군', '청양군', '홍성군', '예산군', '태안군'],
    '전라북도': ['전주시 완산구', '전주시 덕진구', '군산시', '익산시', '정읍시', '남원시', '김제시', '완주군', '진안군', '무주군', '장수군', '임실군', '순창군', '고창군', '부안군'],
    '전라남도': ['목포시', '여수시', '순천시', '나주시', '광양시', '담양군', '곡성군', '구례군', '고흥군', '보성군', '화순군', '장흥군', '강진군', '해남군', '영암군', '무안군', '함평군', '영광군', '장성군', '완도군', '진도군', '신안군'],
    '경상북도': ['포항시 남구', '포항시 북구', '경주시', '김천시', '안동시', '구미시', '영주시', '영천시', '상주시', '문경시', '경산시', '의성군', '청송군', '영양군', '영덕군', '청도군', '고령군', '성주군', '칠곡군', '예천군', '봉화군', '울진군', '울릉군'],
    '경상남도': ['창원시 의창구', '창원시 성산구', '창원시 마산합포구', '창원시 마산회원구', '창원시 진해구', '진주시', '통영시', '사천시', '김해시', '밀양시', '거제시', '양산시', '의령군', '함안군', '창녕군', '고성군', '남해군', '하동군', '산청군', '함양군', '거창군', '합천군'],
    '제주특별자치도': ['제주시', '서귀포시'],
}

# 도로명 접두사 샘플 (더 다양한 조합을 위해)
ROAD_PREFIXES = [
    # 방향/위치
    '중앙', '동', '서', '남', '북', '상', '하', '신', '구', '내', '외',
    # 자연
    '산', '강', '천', '해', '호수', '숲', '들', '바다', '언덕', '골짜기', '계곡',
    '솔', '소나무', '은행나무', '버드나무', '단풍', '벚꽃', '매화', '장미', '백합',
    '청산', '녹수', '백운', '청계', '명수', '석계', '한강', '낙동', '금강', '영산',
    # 동물
    '학', '봉황', '용', '호랑이', '사슴', '두루미', '백로', '까치', '비둘기',
    # 역사/문화
    '문화', '예술', '학문', '교육', '역사', '전통', '민속', '유산', '고궁', '서원',
    '충효', '인의', '예지', '신의', '효도', '우정', '사랑', '희망', '평화', '통일',
    # 발전/번영
    '번영', '발전', '진흥', '융성', '창조', '혁신', '미래', '첨단', '산업', '기술',
    '과학', '정보', '디지털', '스마트', '그린', '에코',
    # 생활
    '행복', '건강', '장수', '복지', '안전', '편의', '생활', '주민', '시민', '마을',
    '새마을', '햇살', '바람', '하늘', '구름', '별', '달', '태양', '무지개', '노을',
    # 시설
    '역전', '시청', '도청', '군청', '구청', '청사', '공원', '광장', '체육', '운동',
    '대학', '학교', '병원', '시장', '백화점', '터미널', '공항', '항만', '부두',
    # 지역 특성
    '온천', '관광', '휴양', '리조트', '해변', '포구', '나루', '다리', '고개', '재',
]

# 도로명 접미사
ROAD_SUFFIXES = ['로', '길', '대로']


def generate_korean_name() -> str:
    """한국어 이름 생성"""
    return fake.name()


def generate_tracking_number() -> str:
    """8자리 운송장 번호 생성"""
    return ''.join([str(random.randint(0, 9)) for _ in range(8)])


def generate_region_code() -> str:
    """지역 코드 생성 (예: 서울1, 부산2)"""
    city = random.choice(KOREAN_CITIES)
    number = random.randint(1, 9)
    return f"{city}{number}"


def generate_korean_address() -> str:
    """
    한국 주소 생성 (간단한 형태)
    예: 광주광역시 남구 보문로 76
    """
    # 시/도 선택
    province = random.choice(list(KOREAN_DISTRICTS.keys()))
    
    # 구/군 선택
    district = random.choice(KOREAN_DISTRICTS[province])
    
    # 도로명 생성 (간단하게)
    road_style = random.choice(['simple', 'prefix', 'name'])
    
    if road_style == 'simple':
        # 간단한 도로명 (예: 보문로, 중앙로, 역전로)
        simple_prefixes = [
            '보문', '중앙', '역전', '시청', '문화', '산업', '번영', '평화', '자유', '통일',
            '세종', '광복', '독립', '민주', '정의', '희망', '미래', '새벽', '햇살', '바람',
            '청산', '녹수', '백운', '명수', '석계', '한강', '낙동', '금강', '영산', '섬진',
            '동문', '서문', '남문', '북문', '성내', '성외', '읍내', '장터', '시장', '공원',
        ]
        road_name = random.choice(simple_prefixes) + random.choice(ROAD_SUFFIXES)
    elif road_style == 'prefix':
        # 접두사 + 접미사 (예: 신문로, 구시장길)
        road_name = random.choice(ROAD_PREFIXES[:30]) + random.choice(ROAD_SUFFIXES)
    else:
        # 성씨 + 접미사 (예: 김로, 이길)
        extras = ['', '문', '산', '천', '정', '덕', '원']
        road_name = fake.last_name() + random.choice(extras) + random.choice(ROAD_SUFFIXES)
    
    # 번지
    number = random.randint(1, 500)
    
    return f"{province} {district} {road_name} {number}"


def generate_random_shipping_data() -> dict:
    """랜덤 운송장 데이터 생성"""
    return {
        'tracking_number': generate_tracking_number(),
        'region_code': generate_region_code(),
        'recipient_name': generate_korean_name(),
        'recipient_address': generate_korean_address(),
        'sender_name': generate_korean_name(),
        'sender_address': generate_korean_address(),
    }


def generate_single_worker(args):
    """
    병렬 처리용 워커 함수 (모듈 레벨에서 정의해야 pickle 가능)
    """
    idx, output_dir, template_path, font_path, effect_config = args

    # 각 워커에서 generator 인스턴스 생성
    generator = ShippingLabelGenerator(template_path=template_path, font_path=font_path)

    output_path = Path(output_dir)

    # 랜덤 데이터 생성
    data = generate_random_shipping_data()

    # 이미지 생성
    image = generator.render_image(data)

    # 효과 적용
    applied_effect = 'none'
    if effect_config:
        image, applied_effect = apply_image_effect(image, effect_config)

    # 파일명 생성
    image_filename = f"{idx:05d}.jpg"
    image_path = output_path / 'images' / image_filename

    # 이미지 저장
    image.save(image_path, 'JPEG', quality=95)

    # 라벨 생성
    relative_image_path = f"images/{image_filename}"
    label = generator.generate_label_json(data, relative_image_path)

    return label, applied_effect


class ShippingLabelGenerator:
    """운송장 라벨 이미지 생성기"""
    
    def __init__(self, template_path: str, font_path: Optional[str] = None):
        """
        Args:
            template_path: 템플릿 이미지 경로
            font_path: 폰트 파일 경로 (None이면 시스템 폰트 사용)
        """
        self.template_path = Path(template_path)
        self.template_image = Image.open(self.template_path)
        self.image_width, self.image_height = self.template_image.size
        
        # 폰트 설정
        self.font_path = font_path
        if font_path is None:
            # 스크립트 위치 기준 fonts 폴더
            script_dir = Path(__file__).parent
            local_fonts_dir = script_dir / 'fonts'
            
            # Windows / Linux / macOS 폰트 경로들
            possible_fonts = [
                # 프로젝트 로컬 폰트 (우선)
                str(local_fonts_dir / 'NanumGothic.ttf'),
                str(local_fonts_dir / 'NanumGothicBold.ttf'),
                str(local_fonts_dir / 'malgun.ttf'),
                # Windows
                'C:/Windows/Fonts/malgun.ttf',      # 맑은 고딕
                'C:/Windows/Fonts/malgunbd.ttf',    # 맑은 고딕 Bold
                'C:/Windows/Fonts/NanumGothic.ttf', # 나눔고딕
                'C:/Windows/Fonts/gulim.ttc',       # 굴림
                # Linux - 나눔폰트
                '/usr/share/fonts/truetype/nanum/NanumGothic.ttf',
                '/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf',
                '/usr/share/fonts/nanum/NanumGothic.ttf',
                '/usr/share/fonts/nanum/NanumGothicBold.ttf',
                # Linux - 나눔폰트 (다른 경로)
                '/usr/share/fonts/truetype/NanumGothic.ttf',
                '/usr/share/fonts/NanumGothic.ttf',
                # Linux - 본고딕 (Noto Sans CJK)
                '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
                '/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc',
                '/usr/share/fonts/google-noto-cjk/NotoSansCJK-Regular.ttc',
                '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc',
                # Linux - 은폰트
                '/usr/share/fonts/truetype/unfonts-core/UnDotum.ttf',
                '/usr/share/fonts/truetype/unfonts/UnDotum.ttf',
                # Linux - D2Coding
                '/usr/share/fonts/truetype/d2coding/D2Coding.ttf',
                # macOS
                '/System/Library/Fonts/AppleGothic.ttf',
                '/Library/Fonts/NanumGothic.ttf',
            ]
            for font in possible_fonts:
                if Path(font).exists():
                    self.font_path = font
                    print(f"폰트 발견: {font}")
                    break
            
            if self.font_path is None:
                print("=" * 60)
                print("경고: 한글 폰트를 찾을 수 없습니다!")
                print("=" * 60)
                print("\n다음 명령으로 폰트를 다운로드하세요:\n")
                print(f"  mkdir -p {local_fonts_dir}")
                print(f"  cd {local_fonts_dir}")
                print("  wget https://github.com/naver/nanumfont/releases/download/VER2.5/NanumGothic.ttf")
                print("  wget https://github.com/naver/nanumfont/releases/download/VER2.5/NanumGothicBold.ttf")
                print("=" * 60)
        
        self.font_path_bold = None
        if self.font_path:
            if 'malgun.ttf' in self.font_path:
                self.font_path_bold = self.font_path.replace('malgun.ttf', 'malgunbd.ttf')
            elif 'NanumGothic.ttf' in self.font_path:
                self.font_path_bold = self.font_path.replace('NanumGothic.ttf', 'NanumGothicBold.ttf')
        
        # 마스킹할 영역 정의 (텍스트를 덮어쓸 영역)
        self.mask_regions = self._define_mask_regions()
    
    def _define_mask_regions(self) -> dict:
        """각 필드의 마스킹 영역 정의 (label_config.json에서 로드)"""
        # 전역 MASK_REGIONS 사용 (설정 파일에서 로드됨)
        return {k: tuple(v) for k, v in MASK_REGIONS.items()}
    
    def _get_font(self, size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
        """폰트 객체 반환"""
        font_file = self.font_path_bold if bold and self.font_path_bold else self.font_path
        if font_file:
            try:
                return ImageFont.truetype(font_file, size)
            except Exception:
                pass
        return ImageFont.load_default()
    
    def _calculate_auto_fit_font_size(self, text: str, bbox: tuple, bold: bool = False, 
                                       min_size: int = 10, max_size: int = 200, 
                                       padding: int = 4) -> int:
        """
        텍스트가 bbox 안에 들어가도록 적절한 폰트 크기 계산 (이진 탐색)
        
        Args:
            text: 렌더링할 텍스트
            bbox: (x1, y1, x2, y2) 바운딩 박스
            bold: 굵은 폰트 여부
            min_size: 최소 폰트 크기
            max_size: 최대 폰트 크기
            padding: 여백 (픽셀)
            
        Returns:
            적절한 폰트 크기
        """
        x1, y1, x2, y2 = bbox
        max_width = (x2 - x1) - padding * 2
        max_height = (y2 - y1) - padding * 2
        
        if max_width <= 0 or max_height <= 0:
            return min_size
        
        # 이진 탐색으로 최적 폰트 크기 찾기
        low, high = min_size, max_size
        best_size = min_size
        
        while low <= high:
            mid = (low + high) // 2
            font = self._get_font(mid, bold)
            
            # 텍스트 크기 측정
            try:
                bbox_text = font.getbbox(text)
                text_width = bbox_text[2] - bbox_text[0]
                text_height = bbox_text[3] - bbox_text[1]
            except:
                # 구버전 PIL 호환
                text_width, text_height = font.getsize(text)
            
            if text_width <= max_width and text_height <= max_height:
                best_size = mid
                low = mid + 1
            else:
                high = mid - 1
        
        return best_size
    
    def _get_background_color(self, image: Image.Image, region: tuple, field_name: str) -> tuple:
        """영역의 배경색 반환 (운송장 배경색)"""
        # 운송장 배경색은 밝은 회색/베이지 계열
        # 필드별로 약간 다른 배경색 사용
        background_colors = {
            'tracking_number': (235, 232, 225),  # 상단 영역
            'region_code': (235, 232, 225),
            'recipient_name': (235, 232, 225),
            'recipient_address': (235, 232, 225),
            'sender_name': (235, 232, 225),
            'sender_address': (235, 232, 225),
        }
        return background_colors.get(field_name, (235, 232, 225))
    
    def render_image(self, data: dict) -> Image.Image:
        """
        데이터를 기반으로 운송장 이미지 생성
        
        Args:
            data: 운송장 데이터 딕셔너리
            
        Returns:
            생성된 이미지
        """
        # 템플릿 이미지 복사
        image = self.template_image.copy()
        draw = ImageDraw.Draw(image)
        
        # 각 필드에 대해 마스킹 후 텍스트 렌더링
        for field_name, field_config in SHIPPING_LABEL_FIELDS.items():
            if field_name not in data:
                continue
            
            text = data[field_name]
            mask_region = self.mask_regions.get(field_name)
            
            if mask_region:
                # 배경색으로 마스킹
                bg_color = self._get_background_color(image, mask_region, field_name)
                draw.rectangle(mask_region, fill=bg_color)
            
            # 폰트 크기 결정
            if field_config.auto_fit:
                # bbox에 맞게 자동 조절
                font_size = self._calculate_auto_fit_font_size(
                    text, field_config.bbox, field_config.font_bold
                )
            else:
                # 설정된 font_size 값 그대로 사용
                font_size = field_config.font_size
            
            # 텍스트 렌더링
            font = self._get_font(font_size, field_config.font_bold)
            x1, y1, x2, y2 = field_config.bbox
            
            # 텍스트 위치 계산 (좌상단 기준)
            text_x = x1
            text_y = y1
            
            draw.text(
                (text_x, text_y),
                text,
                font=font,
                fill=field_config.font_color
            )
        
        return image
    
    def generate_label_json(self, data: dict, image_path: str) -> dict:
        """
        JSON 라벨 데이터 생성
        
        Args:
            data: 운송장 데이터 딕셔너리
            image_path: 이미지 파일 경로
            
        Returns:
            JSON 라벨 데이터
        """
        fields = []
        
        for field_name, field_config in SHIPPING_LABEL_FIELDS.items():
            if field_name not in data:
                continue
            
            fields.append({
                'field_name': field_name,
                'text': data[field_name],
                'bbox': list(field_config.bbox)
            })
        
        return {
            'image_path': image_path,
            'width': self.image_width,
            'height': self.image_height,
            'fields': fields
        }
    
    def generate_single(self, output_dir: Path, index: int, effect_config: dict = None) -> tuple:
        """
        단일 이미지와 라벨 생성
        
        Args:
            output_dir: 출력 디렉토리
            index: 이미지 인덱스
            effect_config: 효과 설정 (optional)
            
        Returns:
            (이미지 경로, 라벨 데이터, 적용된 효과)
        """
        # 랜덤 데이터 생성
        data = generate_random_shipping_data()
        
        # 이미지 생성
        image = self.render_image(data)
        
        # 효과 적용
        applied_effect = 'none'
        if effect_config:
            image, applied_effect = apply_image_effect(image, effect_config)
        
        # 파일명 생성
        image_filename = f"{index:05d}.jpg"
        image_path = output_dir / 'images' / image_filename
        
        # 이미지 저장
        image.save(image_path, 'JPEG', quality=95)
        
        # 라벨 생성
        relative_image_path = f"images/{image_filename}"
        label = self.generate_label_json(data, relative_image_path)
        
        return image_path, label, applied_effect
    
    def generate_batch(self, count: int, output_dir: str = 'generated', start_index: int = 1, num_workers: int = None):
        """
        배치로 이미지와 라벨 생성 (병렬 처리)

        Args:
            count: 생성할 이미지 수
            output_dir: 출력 디렉토리
            start_index: 시작 인덱스 (기본값: 1)
            num_workers: 병렬 처리 워커 수 (기본값: CPU 코어 수)
        """
        output_path = Path(output_dir)
        images_dir = output_path / 'images'
        labels_dir = output_path / 'labels'

        # 디렉토리 생성
        images_dir.mkdir(parents=True, exist_ok=True)
        labels_dir.mkdir(parents=True, exist_ok=True)

        # 효과 설정 로드
        effect_config = load_effect_config()
        if effect_config.get('apply_effect'):
            effect_ratios = effect_config.get('effect_ratios', {})
            print(f"효과 적용: 비율 설정 {effect_ratios} (강도: {effect_config.get('effect_strength')})")
            if effect_config.get('random_strength'):
                print(f"  랜덤 강도 활성화: 1~{effect_config.get('effect_strength')}")

        # 워커 수 설정
        if num_workers is None:
            num_workers = mp.cpu_count()
        print(f"병렬 처리: {num_workers}개 워커 사용")

        if start_index > 1:
            print(f"시작 인덱스: {start_index} (이어서 생성)")
        print(f"생성 시작: {count}개의 이미지...")

        # 병렬 처리를 위한 인덱스 리스트
        indices = [start_index + i for i in range(count)]

        # 워커 함수에 전달할 인자 준비
        worker_args = [
            (idx, str(output_path), str(self.template_path), self.font_path, effect_config)
            for idx in indices
        ]

        # 병렬 처리 실행
        all_labels = []
        effect_stats = {}

        with mp.Pool(processes=num_workers) as pool:
            results = list(tqdm(
                pool.imap(generate_single_worker, worker_args),
                total=count,
                desc="이미지 생성"
            ))

        # 결과 처리
        for label, applied_effect in results:
            all_labels.append(label)
            effect_stats[applied_effect] = effect_stats.get(applied_effect, 0) + 1

        # 전체 라벨을 하나의 JSON 파일로 저장
        labels_file = labels_dir / 'labels.json'

        # 이어서 생성하는 경우 기존 라벨 로드
        existing_labels = []
        if start_index > 1 and labels_file.exists():
            try:
                with open(labels_file, 'r', encoding='utf-8') as f:
                    existing_labels = json.load(f)
                print(f"기존 라벨 {len(existing_labels)}개 로드됨")
            except:
                pass

        # 기존 라벨 + 새 라벨 합치기
        combined_labels = existing_labels + all_labels

        with open(labels_file, 'w', encoding='utf-8') as f:
            json.dump(combined_labels, f, ensure_ascii=False, indent=2)

        # 개별 라벨 파일도 저장 (시작 인덱스 적용)
        print("라벨 파일 저장 중...")
        for i, label in enumerate(tqdm(all_labels, desc="라벨 저장")):
            current_index = start_index + i
            label_file = labels_dir / f"{current_index:05d}.json"
            with open(label_file, 'w', encoding='utf-8') as f:
                json.dump(label, f, ensure_ascii=False, indent=2)

        print(f"\n완료!")
        print(f"이미지 저장 위치: {images_dir}")
        print(f"라벨 저장 위치: {labels_dir}")
        print(f"통합 라벨 파일: {labels_file}")
        print(f"총 라벨 수: {len(combined_labels)}개")

        # 효과별 통계 출력
        if effect_stats:
            print(f"\n=== 효과별 생성 통계 ===")
            effect_names = {
                'none': '원본', 'blur': '흐림', 'mosaic': '모자이크',
                'noise': '노이즈', 'combined': '복합'
            }
            for effect, cnt in sorted(effect_stats.items(), key=lambda x: -x[1]):
                name = effect_names.get(effect, effect)
                percent = cnt / count * 100
                print(f"  {name}: {cnt}개 ({percent:.1f}%)")


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description='OCR 학습 데이터 생성기')
    parser.add_argument(
        '-n', '--count',
        type=int,
        default=10,
        help='생성할 이미지 수 (기본값: 10)'
    )
    parser.add_argument(
        '-t', '--template',
        type=str,
        default=None,
        help='템플릿 이미지 경로'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        default='generated',
        help='출력 디렉토리 (기본값: generated)'
    )
    parser.add_argument(
        '-f', '--font',
        type=str,
        default=None,
        help='폰트 파일 경로'
    )
    parser.add_argument(
        '--start-index',
        type=int,
        default=1,
        help='시작 인덱스 (기본값: 1, 이어서 생성할 때 사용)'
    )
    parser.add_argument(
        '--effect',
        type=str,
        default=None,
        help='효과 비율 설정 (예: blur:50,mosaic:50 또는 none:100)'
    )
    parser.add_argument(
        '--strength',
        type=int,
        default=5,
        help='효과 강도 (1-20, 기본값: 5)'
    )
    parser.add_argument(
        '--random-strength',
        action='store_true',
        help='랜덤 강도 사용 (1~설정값)'
    )
    parser.add_argument(
        '--clear',
        action='store_true',
        help='기존 파일 삭제 후 새로 생성'
    )
    parser.add_argument(
        '-w', '--workers',
        type=int,
        default=None,
        help='병렬 처리 워커 수 (기본값: CPU 코어 수)'
    )

    args = parser.parse_args()
    
    # 템플릿 경로 결정
    if args.template:
        template_path = args.template
    else:
        # 기본 템플릿 경로
        script_dir = Path(__file__).parent
        template_path = script_dir / 'img' / '운송장 예시파일.jpg'
    
    if not Path(template_path).exists():
        print(f"템플릿 파일을 찾을 수 없습니다: {template_path}")
        return
    
    # 출력 디렉토리 경로 (스크립트 위치 기준)
    script_dir = Path(__file__).parent
    output_dir = script_dir / args.output
    
    # 기존 파일 삭제 옵션
    if args.clear and output_dir.exists():
        import shutil
        shutil.rmtree(output_dir)
        print(f"기존 폴더 삭제됨: {output_dir}")
    
    # CLI에서 효과 설정이 주어진 경우 effect_config.json 업데이트
    if args.effect:
        effect_ratios = {}
        for part in args.effect.split(','):
            if ':' in part:
                effect_name, ratio = part.split(':')
                effect_ratios[effect_name.strip()] = int(ratio.strip())
        
        effect_config = {
            'apply_effect': True,
            'effect_ratios': effect_ratios,
            'effect_strength': args.strength,
            'random_strength': args.random_strength,
        }
        
        with open(EFFECT_CONFIG_FILE, 'w') as f:
            json.dump(effect_config, f, indent=2)
        
        print(f"효과 설정: {effect_ratios}, 강도: {args.strength}")
    
    # 생성기 초기화 및 실행
    generator = ShippingLabelGenerator(
        template_path=str(template_path),
        font_path=args.font
    )
    
    generator.generate_batch(
        count=args.count,
        output_dir=str(output_dir),
        start_index=args.start_index,
        num_workers=args.workers
    )


if __name__ == '__main__':
    main()
