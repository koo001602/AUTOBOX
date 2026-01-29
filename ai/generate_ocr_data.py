"""
OCR 학습 데이터 생성기
운송장 이미지 템플릿을 기반으로 텍스트만 변경한 합성 이미지와 JSON 라벨 데이터를 생성합니다.

설정 조절: label_editor.py를 실행하여 GUI에서 영역을 조절한 후 저장하면
자동으로 label_config.json에서 설정을 불러옵니다.
"""

import json
import random
import argparse
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

from PIL import Image, ImageDraw, ImageFont, ImageFilter
from faker import Faker


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
    font_size: int               # 폰트 크기
    font_color: tuple = (0, 0, 0)  # RGB 색상 (기본: 검정)
    font_bold: bool = False      # 굵은 폰트 여부


def load_field_config():
    """설정 파일에서 필드 설정 로드"""
    # 기본 설정
    default_fields = {
        'tracking_number': {'text': [35, 115, 440, 210], 'font_size': 75},
        'region_code': {'text': [905, 90, 1265, 220], 'font_size': 110},
        'recipient_name': {'text': [60, 270, 580, 365], 'font_size': 80},
        'recipient_address': {'text': [20, 380, 1260, 490], 'font_size': 68},
        'sender_name': {'text': [80, 520, 580, 615], 'font_size': 68},
        'sender_address': {'text': [20, 660, 1260, 760], 'font_size': 68},
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
            font_bold=True
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
    '서울', '부산', '대구', '인천', '광주', '대전', '울산', '세종',
    '수원', '성남', '고양', '용인', '창원', '청주', '전주', '천안',
    '안산', '안양', '남양주', '화성', '평택', '의정부', '시흥', '김해'
]

# 한국 도/시 목록
KOREAN_PROVINCES = [
    '서울특별시', '부산광역시', '대구광역시', '인천광역시', '광주광역시',
    '대전광역시', '울산광역시', '세종특별자치시', '경기도', '강원도',
    '충청북도', '충청남도', '전라북도', '전라남도', '경상북도', '경상남도', '제주특별자치도'
]

# 구/군 목록 (샘플)
KOREAN_DISTRICTS = {
    '서울특별시': ['강남구', '강동구', '강북구', '강서구', '관악구', '광진구', '구로구', '금천구', '노원구', '도봉구', '동대문구', '동작구', '마포구', '서대문구', '서초구', '성동구', '성북구', '송파구', '양천구', '영등포구', '용산구', '은평구', '종로구', '중구', '중랑구'],
    '부산광역시': ['강서구', '금정구', '남구', '동구', '동래구', '부산진구', '북구', '사상구', '사하구', '서구', '수영구', '연제구', '영도구', '중구', '해운대구'],
    '대구광역시': ['남구', '달서구', '달성군', '동구', '북구', '서구', '수성구', '중구'],
    '인천광역시': ['강화군', '계양구', '남동구', '동구', '미추홀구', '부평구', '서구', '연수구', '옹진군', '중구'],
    '광주광역시': ['광산구', '남구', '동구', '북구', '서구'],
    '대전광역시': ['대덕구', '동구', '서구', '유성구', '중구'],
    '울산광역시': ['남구', '동구', '북구', '울주군', '중구'],
}

# 도로명 샘플
ROAD_NAMES = [
    '대로', '로', '길', 'street', '대학로', '중앙로', '역전로', '시청로',
    '문화로', '산업로', '번영로', '평화로', '자유로', '통일로', '세종로'
]


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
    """한국 주소 생성"""
    # 시/도 선택
    province = random.choice(list(KOREAN_DISTRICTS.keys()))
    
    # 구/군 선택
    district = random.choice(KOREAN_DISTRICTS[province])
    
    # 도로명 생성
    road_prefix = fake.last_name() + random.choice(['', '문', '산', '천', '강'])
    road_suffix = random.choice(['로', '길', '대로'])
    road_name = road_prefix + road_suffix
    
    # 번지
    number = random.randint(1, 500)
    
    # 상세주소 (선택적)
    detail = ''
    if random.random() > 0.5:
        building_num = random.randint(1, 30)
        detail = f" {building_num}"
    
    return f"{province} {district} {road_name} {number}{detail}"


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
            # Windows 기본 폰트 경로들
            possible_fonts = [
                'C:/Windows/Fonts/malgun.ttf',      # 맑은 고딕
                'C:/Windows/Fonts/malgunbd.ttf',   # 맑은 고딕 Bold
                'C:/Windows/Fonts/NanumGothic.ttf', # 나눔고딕
                'C:/Windows/Fonts/gulim.ttc',       # 굴림
                '/usr/share/fonts/truetype/nanum/NanumGothic.ttf',  # Linux
                '/System/Library/Fonts/AppleGothic.ttf',  # macOS
            ]
            for font in possible_fonts:
                if Path(font).exists():
                    self.font_path = font
                    break
        
        self.font_path_bold = None
        if self.font_path and 'malgun.ttf' in self.font_path:
            self.font_path_bold = self.font_path.replace('malgun.ttf', 'malgunbd.ttf')
        
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
            
            # 텍스트 렌더링
            font = self._get_font(field_config.font_size, field_config.font_bold)
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
    
    def generate_batch(self, count: int, output_dir: str = 'generated', start_index: int = 1):
        """
        배치로 이미지와 라벨 생성
        
        Args:
            count: 생성할 이미지 수
            output_dir: 출력 디렉토리
            start_index: 시작 인덱스 (기본값: 1)
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
        
        all_labels = []
        effect_stats = {}  # 효과별 통계
        
        if start_index > 1:
            print(f"시작 인덱스: {start_index} (이어서 생성)")
        print(f"생성 시작: {count}개의 이미지...")
        
        for i in range(count):
            current_index = start_index + i
            image_path, label, applied_effect = self.generate_single(output_path, current_index, effect_config)
            all_labels.append(label)
            
            # 효과 통계 업데이트
            effect_stats[applied_effect] = effect_stats.get(applied_effect, 0) + 1
            
            if (i + 1) % 10 == 0 or i == count - 1:
                print(f"진행률: {i + 1}/{count} ({(i + 1) / count * 100:.1f}%)")
        
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
        for i, label in enumerate(all_labels):
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
        start_index=args.start_index
    )


if __name__ == '__main__':
    main()
