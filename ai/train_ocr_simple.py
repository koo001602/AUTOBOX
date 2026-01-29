"""
간단한 PaddleOCR 텍스트 인식 학습 스크립트

원천 데이터 구조:
- generated/images/: 전체 운송장 이미지
- generated/labels/labels.json: 필드별 bbox와 텍스트
"""

import os
import sys
import json
import shutil
import random
import argparse
from pathlib import Path
from PIL import Image
from tqdm import tqdm

# GPU 설정
def setup_gpu(gpu_id=0):
    os.environ['CUDA_VISIBLE_DEVICES'] = str(gpu_id)
    print(f"GPU {gpu_id} 사용")


def prepare_data(generated_dir: Path, output_dir: Path, train_ratio: float = 0.9):
    """
    원천 데이터를 PaddleOCR 형식으로 변환
    """
    print("\n" + "=" * 60)
    print("데이터 준비")
    print("=" * 60)
    
    # 출력 디렉토리 초기화
    if output_dir.exists():
        shutil.rmtree(output_dir)
    
    train_dir = output_dir / 'train'
    val_dir = output_dir / 'val'
    (train_dir / 'images').mkdir(parents=True)
    (val_dir / 'images').mkdir(parents=True)
    
    # labels.json 로드
    labels_file = generated_dir / 'labels' / 'labels.json'
    with open(labels_file, 'r', encoding='utf-8') as f:
        all_data = json.load(f)
    
    print(f"총 {len(all_data)}개 이미지 발견")
    
    # 데이터 섞기
    random.shuffle(all_data)
    
    # Train/Val 분할
    split_idx = int(len(all_data) * train_ratio)
    train_data = all_data[:split_idx]
    val_data = all_data[split_idx:]
    
    # 문자 집합 수집
    all_chars = set()
    
    def process_split(data, out_dir, prefix):
        labels = []
        for idx, item in enumerate(tqdm(data, desc=prefix)):
            img_path = generated_dir / item['image_path']
            if not img_path.exists():
                continue
            
            img = Image.open(img_path)
            
            for field in item['fields']:
                text = field['text']
                bbox = field['bbox']
                field_name = field['field_name']
                
                # 문자 수집
                all_chars.update(text)
                
                # bbox 크롭
                x1, y1, x2, y2 = bbox
                cropped = img.crop((x1, y1, x2, y2))
                
                # 저장
                filename = f"{prefix}_{idx:05d}_{field_name}.jpg"
                save_path = out_dir / 'images' / filename
                cropped.save(save_path, 'JPEG', quality=95)
                
                # 라벨 추가
                labels.append(f"images/{filename}\t{text}")
        
        # label.txt 저장
        with open(out_dir / 'label.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(labels))
        
        return len(labels)
    
    train_count = process_split(train_data, train_dir, 'train')
    val_count = process_split(val_data, val_dir, 'val')
    
    # 문자 사전 저장
    sorted_chars = sorted(all_chars)
    dict_file = output_dir / 'dict.txt'
    with open(dict_file, 'w', encoding='utf-8') as f:
        for char in sorted_chars:
            f.write(char + '\n')
    
    print(f"\n데이터 준비 완료!")
    print(f"  Train: {train_count}개")
    print(f"  Val: {val_count}개")
    print(f"  문자 사전: {len(sorted_chars)}개 문자")
    
    return train_count, val_count, len(sorted_chars)


def create_config(output_dir: Path, config_file: Path, 
                  batch_size: int = 64, epochs: int = 100, lr: float = 0.001):
    """
    PaddleOCR 설정 파일 생성
    """
    print("\n" + "=" * 60)
    print("설정 파일 생성")
    print("=" * 60)
    
    def to_posix(path):
        return str(path).replace('\\', '/')
    
    config = f'''Global:
  debug: false
  use_gpu: false
  epoch_num: {epochs}
  log_smooth_window: 20
  print_batch_step: 20
  save_model_dir: ./output/rec_shipping_label
  save_epoch_step: 10
  eval_batch_step: [0, 100]
  cal_metric_during_train: true
  pretrained_model:
  checkpoints:
  save_inference_dir:
  use_visualdl: false
  character_dict_path: {to_posix(output_dir / 'dict.txt')}
  max_text_length: 50
  infer_mode: false
  use_space_char: true
  distributed: false

Optimizer:
  name: Adam
  beta1: 0.9
  beta2: 0.999
  lr:
    name: Cosine
    learning_rate: {lr}
    warmup_epoch: 5
  regularizer:
    name: L2
    factor: 1.0e-05

Architecture:
  model_type: rec
  algorithm: Rosetta
  Transform:
  Backbone:
    name: MobileNetV3
    scale: 0.5
    model_name: large
  Neck:
    name: SequenceEncoder
    encoder_type: reshape
  Head:
    name: CTCHead
    fc_decay: 0.0004

Loss:
  name: CTCLoss

PostProcess:
  name: CTCLabelDecode

Metric:
  name: RecMetric
  main_indicator: acc

Train:
  dataset:
    name: SimpleDataSet
    data_dir: {to_posix(output_dir / 'train')}
    label_file_list:
      - {to_posix(output_dir / 'train' / 'label.txt')}
    transforms:
      - DecodeImage:
          img_mode: BGR
          channel_first: false
      - RecAug:
      - CTCLabelEncode:
      - RecResizeImg:
          image_shape: [3, 32, 100]
      - KeepKeys:
          keep_keys:
            - image
            - label
            - length
  loader:
    shuffle: true
    batch_size_per_card: {batch_size}
    drop_last: true
    num_workers: 0

Eval:
  dataset:
    name: SimpleDataSet
    data_dir: {to_posix(output_dir / 'val')}
    label_file_list:
      - {to_posix(output_dir / 'val' / 'label.txt')}
    transforms:
      - DecodeImage:
          img_mode: BGR
          channel_first: false
      - CTCLabelEncode:
      - RecResizeImg:
          image_shape: [3, 32, 100]
      - KeepKeys:
          keep_keys:
            - image
            - label
            - length
  loader:
    shuffle: false
    drop_last: false
    batch_size_per_card: {batch_size}
    num_workers: 0
'''
    
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(config)
    
    print(f"설정 파일 저장: {config_file}")
    print(f"  Batch size: {batch_size}")
    print(f"  Epochs: {epochs}")
    print(f"  Learning rate: {lr}")


def train(paddleocr_dir: Path, config_file: Path):
    """
    학습 실행
    """
    import subprocess
    
    print("\n" + "=" * 60)
    print("학습 시작")
    print("=" * 60)
    
    train_script = paddleocr_dir / 'tools' / 'train.py'
    cmd = [sys.executable, str(train_script), '-c', str(config_file)]
    
    print(f"명령어: {' '.join(cmd)}")
    print("-" * 60)
    
    subprocess.run(cmd, cwd=str(paddleocr_dir))


def main():
    parser = argparse.ArgumentParser(description='운송장 OCR 학습')
    parser.add_argument('--gpu', type=int, default=7, help='GPU ID')
    parser.add_argument('--batch-size', type=int, default=64, help='배치 크기')
    parser.add_argument('--epochs', type=int, default=100, help='에폭 수')
    parser.add_argument('--lr', type=float, default=0.001, help='학습률')
    parser.add_argument('--prepare-only', action='store_true', help='데이터 준비만')
    parser.add_argument('--train-only', action='store_true', help='학습만 실행')
    
    args = parser.parse_args()
    
    # 경로 설정
    base_dir = Path(__file__).parent
    generated_dir = base_dir / 'generated'
    output_dir = base_dir / 'ocr_data'
    config_file = output_dir / 'config.yml'
    paddleocr_dir = base_dir / 'PaddleOCR'
    
    # GPU 설정
    setup_gpu(args.gpu)
    
    # 데이터 준비
    if not args.train_only:
        prepare_data(generated_dir, output_dir)
    
    if args.prepare_only:
        print("\n데이터 준비 완료!")
        return
    
    # 설정 파일 생성
    create_config(output_dir, config_file, args.batch_size, args.epochs, args.lr)
    
    # 학습
    if paddleocr_dir.exists():
        train(paddleocr_dir, config_file)
    else:
        print(f"\nPaddleOCR 디렉토리를 찾을 수 없습니다: {paddleocr_dir}")
        print("다음 명령으로 클론하세요:")
        print(f"  git clone https://github.com/PaddlePaddle/PaddleOCR.git {paddleocr_dir}")


if __name__ == '__main__':
    main()
