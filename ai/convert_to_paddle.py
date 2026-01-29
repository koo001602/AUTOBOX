"""
생성된 OCR 데이터를 PaddleOCR 학습 형식으로 변환
- 전체 이미지에서 각 필드를 크롭하여 저장
- label.txt 형식: 이미지경로\t텍스트
"""

import json
import random
from pathlib import Path
from PIL import Image
from tqdm import tqdm

def convert_to_paddle_format(
    generated_dir: str = "generated",
    output_dir: str = "paddle_data",
    train_ratio: float = 0.9
):
    """
    생성된 데이터를 PaddleOCR 형식으로 변환
    
    Args:
        generated_dir: generate_ocr_data.py로 생성된 데이터 디렉토리
        output_dir: PaddleOCR 학습용 출력 디렉토리
        train_ratio: 학습 데이터 비율 (나머지는 검증용)
    """
    script_dir = Path(__file__).parent
    generated_path = script_dir / generated_dir
    output_path = script_dir / output_dir
    
    # 출력 디렉토리 생성
    train_images_dir = output_path / "train" / "images"
    val_images_dir = output_path / "val" / "images"
    train_images_dir.mkdir(parents=True, exist_ok=True)
    val_images_dir.mkdir(parents=True, exist_ok=True)
    
    # labels.json 로드
    labels_file = generated_path / "labels" / "labels.json"
    if not labels_file.exists():
        print(f"오류: {labels_file} 파일을 찾을 수 없습니다.")
        print("먼저 generate_ocr_data.py를 실행하여 데이터를 생성하세요.")
        return
    
    with open(labels_file, 'r', encoding='utf-8') as f:
        labels_data = json.load(f)
    
    print(f"총 {len(labels_data)}개의 이미지 데이터 발견")
    
    # 데이터 섞기
    random.shuffle(labels_data)
    
    # train/val 분할
    split_idx = int(len(labels_data) * train_ratio)
    train_data = labels_data[:split_idx]
    val_data = labels_data[split_idx:]
    
    print(f"학습: {len(train_data)}개, 검증: {len(val_data)}개")
    
    train_labels = []
    val_labels = []
    
    # 학습 데이터 처리
    print("\n학습 데이터 처리 중...")
    for idx, item in enumerate(tqdm(train_data, desc="Train")):
        image_path = generated_path / item['image_path']
        if not image_path.exists():
            continue
        
        img = Image.open(image_path)
        
        for field in item['fields']:
            field_name = field['field_name']
            text = field['text']
            bbox = field['bbox']
            
            # bbox 크롭 (x1, y1, x2, y2)
            x1, y1, x2, y2 = bbox
            cropped = img.crop((x1, y1, x2, y2))
            
            # 크롭된 이미지 저장
            crop_filename = f"{idx:05d}_{field_name}.jpg"
            crop_path = train_images_dir / crop_filename
            cropped.save(crop_path, 'JPEG', quality=95)
            
            # 라벨 추가 (상대 경로 사용)
            train_labels.append(f"images/{crop_filename}\t{text}")
    
    # 검증 데이터 처리
    print("\n검증 데이터 처리 중...")
    for idx, item in enumerate(tqdm(val_data, desc="Val")):
        image_path = generated_path / item['image_path']
        if not image_path.exists():
            continue
        
        img = Image.open(image_path)
        
        for field in item['fields']:
            field_name = field['field_name']
            text = field['text']
            bbox = field['bbox']
            
            x1, y1, x2, y2 = bbox
            cropped = img.crop((x1, y1, x2, y2))
            
            crop_filename = f"{idx:05d}_{field_name}.jpg"
            crop_path = val_images_dir / crop_filename
            cropped.save(crop_path, 'JPEG', quality=95)
            
            val_labels.append(f"images/{crop_filename}\t{text}")
    
    # label.txt 저장
    train_label_file = output_path / "train" / "label.txt"
    val_label_file = output_path / "val" / "label.txt"
    
    with open(train_label_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(train_labels))
    
    with open(val_label_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(val_labels))
    
    print(f"\n변환 완료!")
    print(f"학습 이미지: {len(train_labels)}개 -> {train_label_file}")
    print(f"검증 이미지: {len(val_labels)}개 -> {val_label_file}")
    
    # 샘플 출력
    print(f"\n=== 라벨 샘플 (처음 5개) ===")
    for label in train_labels[:5]:
        print(f"  {label}")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='PaddleOCR 형식으로 데이터 변환')
    parser.add_argument('-i', '--input', default='generated', help='입력 디렉토리')
    parser.add_argument('-o', '--output', default='paddle_data', help='출력 디렉토리')
    parser.add_argument('-r', '--ratio', type=float, default=0.9, help='학습 데이터 비율')
    
    args = parser.parse_args()
    convert_to_paddle_format(args.input, args.output, args.ratio)
