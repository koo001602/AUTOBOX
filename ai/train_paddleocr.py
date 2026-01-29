"""
PaddleOCR 파인튜닝 스크립트

운송장 OCR 데이터를 전처리하고 PaddleOCR 모델을 파인튜닝합니다.

사용법:
    python train_paddleocr.py --help
"""

import os
import sys
import json
import shutil
import random
import argparse
import subprocess
import urllib.request
import tarfile
from pathlib import Path
from PIL import Image


# ============================================================
# GPU 설정 함수
# ============================================================

def setup_gpu_environment(gpu_id: int = 0, memory_fraction: float = 0.95):
    """
    GPU 환경 변수 설정 (스크립트 시작 시 호출)
    
    Args:
        gpu_id: 사용할 GPU ID
        memory_fraction: GPU 메모리 사용 비율 (0.0 ~ 1.0)
    """
    # CUDA 환경 변수 설정 (paddle import 전에 설정해야 함)
    os.environ['CUDA_VISIBLE_DEVICES'] = str(gpu_id)
    os.environ['FLAGS_fraction_of_gpu_memory_to_use'] = str(memory_fraction)
    os.environ['FLAGS_eager_delete_tensor_gb'] = '0.0'  # 텐서 즉시 삭제
    os.environ['FLAGS_memory_fraction_of_eager_deletion'] = '1.0'  # 메모리 즉시 해제
    
    print(f"GPU 환경 설정 완료:")
    print(f"  CUDA_VISIBLE_DEVICES: {gpu_id}")
    print(f"  메모리 사용 비율: {memory_fraction * 100:.0f}%")


def verify_gpu():
    """
    GPU 설정 확인 (paddle import 후 호출)
    """
    try:
        import paddle
        paddle.device.set_device('gpu:0')
        
        print(f"\nPaddlePaddle 정보:")
        print(f"  버전: {paddle.__version__}")
        print(f"  GPU 사용 가능: {paddle.is_compiled_with_cuda()}")
        print(f"  현재 장치: {paddle.device.get_device()}")
        
        if paddle.is_compiled_with_cuda():
            gpu_props = paddle.device.cuda.get_device_properties()
            print(f"  GPU 이름: {gpu_props.name}")
            print(f"  GPU 메모리: {gpu_props.total_memory / 1024**3:.1f} GB")
        
        return True
    except Exception as e:
        print(f"GPU 확인 실패: {e}")
        return False


# ============================================================
# 1. 데이터 전처리
# ============================================================

def convert_to_paddle_format(generated_dir: Path, output_dir: Path, train_ratio: float = 0.9):
    """
    생성된 데이터를 PaddleOCR 텍스트 인식 형식으로 변환
    
    PaddleOCR Recognition 형식:
    - 이미지: 텍스트 영역만 크롭된 이미지
    - 라벨: image_path\tlabel 형식의 txt 파일
    """
    print("\n" + "=" * 60)
    print("1단계: 데이터 전처리 (PaddleOCR 형식 변환)")
    print("=" * 60)
    
    # 출력 디렉토리 생성
    train_img_dir = output_dir / 'train' / 'images'
    val_img_dir = output_dir / 'val' / 'images'
    
    # 기존 디렉토리 삭제 후 재생성
    if output_dir.exists():
        shutil.rmtree(output_dir)
    
    train_img_dir.mkdir(parents=True, exist_ok=True)
    val_img_dir.mkdir(parents=True, exist_ok=True)
    
    # 라벨 파일 로드
    labels_file = generated_dir / 'labels' / 'labels.json'
    if not labels_file.exists():
        print(f"오류: 라벨 파일을 찾을 수 없습니다: {labels_file}")
        print("먼저 python generate_ocr_data.py -n <개수> 명령으로 데이터를 생성하세요.")
        sys.exit(1)
    
    with open(labels_file, 'r', encoding='utf-8') as f:
        all_labels = json.load(f)
    
    print(f"총 {len(all_labels)}개 이미지 로드됨")
    
    # 데이터 섞기
    random.shuffle(all_labels)
    
    # Train/Val 분할
    split_idx = int(len(all_labels) * train_ratio)
    train_labels = all_labels[:split_idx]
    val_labels = all_labels[split_idx:]
    
    train_records = []
    val_records = []
    
    def process_labels(labels, img_dir, records, prefix):
        for idx, label_data in enumerate(labels):
            # 원본 이미지 로드
            img_path = generated_dir / label_data['image_path']
            if not img_path.exists():
                continue
            
            img = Image.open(img_path)
            
            # 각 필드별로 크롭하여 저장
            for field_idx, field in enumerate(label_data['fields']):
                bbox = field['bbox']  # [x1, y1, x2, y2]
                text = field['text']
                field_name = field['field_name']
                
                # 이미지 크롭
                cropped = img.crop((bbox[0], bbox[1], bbox[2], bbox[3]))
                
                # 파일명 생성
                crop_filename = f"{prefix}_{idx:05d}_{field_name}.jpg"
                crop_path = img_dir / crop_filename
                
                # 저장
                cropped.save(crop_path, 'JPEG', quality=95)
                
                # 레코드 추가 (상대 경로 사용)
                relative_path = f"images/{crop_filename}"
                records.append(f"{relative_path}\t{text}")
            
            if (idx + 1) % 500 == 0:
                print(f"  {prefix}: {idx + 1}/{len(labels)} 처리 완료")
    
    print(f"\nTrain 데이터 처리 중... ({len(train_labels)}개)")
    process_labels(train_labels, train_img_dir, train_records, 'train')
    
    print(f"\nVal 데이터 처리 중... ({len(val_labels)}개)")
    process_labels(val_labels, val_img_dir, val_records, 'val')
    
    # 라벨 파일 저장
    with open(output_dir / 'train' / 'label.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(train_records))
    
    with open(output_dir / 'val' / 'label.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(val_records))
    
    print(f"\n전처리 완료!")
    print(f"  Train 샘플: {len(train_records)}개")
    print(f"  Val 샘플: {len(val_records)}개")
    
    return len(train_records), len(val_records)


# ============================================================
# 2. 한글 문자 사전 생성
# ============================================================

def create_korean_dict(data_dir: Path, output_file: Path):
    """
    학습 데이터에서 사용된 모든 문자를 추출하여 사전 생성
    """
    print("\n" + "=" * 60)
    print("2단계: 한글 문자 사전 생성")
    print("=" * 60)
    
    chars = set()
    
    # Train 라벨에서 문자 추출
    label_file = data_dir / 'train' / 'label.txt'
    with open(label_file, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 2:
                text = parts[1]
                chars.update(text)
    
    # 기본 한글 완성형 추가 (가-힣)
    for code in range(0xAC00, 0xD7A4):
        chars.add(chr(code))
    
    # 숫자, 영문, 특수문자 추가
    chars.update('0123456789')
    chars.update('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
    chars.update(' .-_,()[]{}:;/\\@#$%&*+=<>?!"\'~`|^')
    
    # 정렬 후 저장
    sorted_chars = sorted(chars)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for char in sorted_chars:
            f.write(char + '\n')
    
    print(f"문자 사전 생성 완료: {len(sorted_chars)}개 문자")
    print(f"저장 위치: {output_file}")
    
    return sorted_chars


# ============================================================
# 3. 설정 파일 생성
# ============================================================

def create_config_file(data_dir: Path, config_file: Path, pretrain_model_path: str,
                       batch_size: int = 128, epoch_num: int = 100, learning_rate: float = 0.0005):
    """
    PaddleOCR 학습 설정 파일 생성
    """
    print("\n" + "=" * 60)
    print("3단계: 설정 파일 생성")
    print("=" * 60)
    
    # 경로를 forward slash로 변환 (YAML 호환)
    def to_posix(path):
        return str(path).replace('\\', '/')
    
    config_content = f'''Global:
  debug: false
  use_gpu: true
  epoch_num: {epoch_num}
  log_smooth_window: 20
  print_batch_step: 10
  save_model_dir: ./output/rec_korean_finetune
  save_epoch_step: 10
  eval_batch_step: [0, 500]
  cal_metric_during_train: true
  pretrained_model: {pretrain_model_path}
  checkpoints:
  save_inference_dir:
  use_visualdl: false
  infer_img: 
  character_dict_path: {to_posix(data_dir / 'korean_dict.txt')}
  max_text_length: 50
  infer_mode: false
  use_space_char: true
  distributed: true
  save_res_path: ./output/rec/predicts.txt

Optimizer:
  name: Adam
  beta1: 0.9
  beta2: 0.999
  lr:
    name: Cosine
    learning_rate: {learning_rate}
    warmup_epoch: 5
  regularizer:
    name: L2
    factor: 3.0e-05

Architecture:
  model_type: rec
  algorithm: SVTR_LCNet
  Transform:
  Backbone:
    name: MobileNetV1Enhance
    scale: 0.5
    last_conv_stride: [1, 2]
    last_pool_type: avg
  Head:
    name: MultiHead
    head_list:
      - CTCHead:
          Neck:
            name: svtr
            dims: 64
            depth: 2
            hidden_dims: 120
            use_guide: True
          Head:
            fc_decay: 0.00001
      - SARHead:
          enc_dim: 512
          max_text_length: 50

Loss:
  name: MultiLoss
  loss_config_list:
    - CTCLoss:
    - SARLoss:

PostProcess:  
  name: CTCLabelDecode

Metric:
  name: RecMetric
  main_indicator: acc
  ignore_space: False

Train:
  dataset:
    name: SimpleDataSet
    data_dir: {to_posix(data_dir / 'train')}
    ext_op_transform_idx: 1
    label_file_list:
      - {to_posix(data_dir / 'train' / 'label.txt')}
    transforms:
      - DecodeImage:
          img_mode: BGR
          channel_first: false
      - RecConAug:
          prob: 0.5
          ext_data_num: 2
          image_shape: [48, 320, 3]
      - RecAug:
      - MultiLabelEncode:
      - RecResizeImg:
          image_shape: [3, 48, 320]
      - KeepKeys:
          keep_keys:
            - image
            - label_ctc
            - label_sar
            - length
            - valid_ratio
  loader:
    shuffle: true
    batch_size_per_card: {batch_size}
    drop_last: true
    num_workers: 4

Eval:
  dataset:
    name: SimpleDataSet
    data_dir: {to_posix(data_dir / 'val')}
    label_file_list:
      - {to_posix(data_dir / 'val' / 'label.txt')}
    transforms:
      - DecodeImage:
          img_mode: BGR
          channel_first: false
      - MultiLabelEncode:
      - RecResizeImg:
          image_shape: [3, 48, 320]
      - KeepKeys:
          keep_keys:
            - image
            - label_ctc
            - label_sar
            - length
            - valid_ratio
  loader:
    shuffle: false
    drop_last: false
    batch_size_per_card: {batch_size}
    num_workers: 4
'''
    
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print(f"설정 파일 저장: {config_file}")
    print(f"  Batch Size: {batch_size}")
    print(f"  Epoch: {epoch_num}")
    print(f"  Learning Rate: {learning_rate}")


# ============================================================
# 4. 사전 학습 모델 다운로드
# ============================================================

def download_pretrain_model(pretrain_dir: Path):
    """
    한국어 PP-OCRv3 사전 학습 모델 다운로드
    """
    print("\n" + "=" * 60)
    print("4단계: 사전 학습 모델 다운로드")
    print("=" * 60)
    
    pretrain_dir.mkdir(parents=True, exist_ok=True)
    
    model_name = "korean_PP-OCRv3_rec_train"
    model_url = f"https://paddleocr.bj.bcebos.com/PP-OCRv3/multilingual/{model_name}.tar"
    model_tar = pretrain_dir / f"{model_name}.tar"
    model_dir = pretrain_dir / model_name
    
    if model_dir.exists():
        print(f"사전 학습 모델이 이미 존재합니다: {model_dir}")
        return str(model_dir / "best_accuracy")
    
    print(f"다운로드 중: {model_url}")
    urllib.request.urlretrieve(model_url, model_tar)
    
    print("압축 해제 중...")
    with tarfile.open(model_tar, 'r') as tar:
        tar.extractall(pretrain_dir)
    
    # tar 파일 삭제
    model_tar.unlink()
    print(f"완료: {model_dir}")
    
    return str(model_dir / "best_accuracy")


# ============================================================
# 5. PaddleOCR 클론
# ============================================================

def setup_paddleocr(base_dir: Path):
    """
    PaddleOCR 저장소 클론 및 설정
    """
    print("\n" + "=" * 60)
    print("5단계: PaddleOCR 환경 설정")
    print("=" * 60)
    
    paddleocr_dir = base_dir / 'PaddleOCR'
    
    if paddleocr_dir.exists():
        print(f"PaddleOCR이 이미 존재합니다: {paddleocr_dir}")
        return paddleocr_dir
    
    print("PaddleOCR 클론 중...")
    subprocess.run(['git', 'clone', 'https://github.com/PaddlePaddle/PaddleOCR.git', str(paddleocr_dir)], check=True)
    
    print("의존성 설치 중...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', str(paddleocr_dir / 'requirements.txt')], check=True)
    
    return paddleocr_dir


# ============================================================
# 6. 학습 실행
# ============================================================

def run_training(paddleocr_dir: Path, config_file: Path, use_gpu: bool = True, gpu_id: int = 0):
    """
    PaddleOCR 학습 실행
    """
    print("\n" + "=" * 60)
    print("6단계: 모델 학습")
    print("=" * 60)
    
    # GPU 설정
    env = os.environ.copy()
    if use_gpu:
        env['CUDA_VISIBLE_DEVICES'] = str(gpu_id)
        print(f"GPU {gpu_id} 사용")
    
    # 학습 명령 실행
    train_script = paddleocr_dir / 'tools' / 'train.py'
    cmd = [
        sys.executable,
        str(train_script),
        '-c', str(config_file)
    ]
    
    if not use_gpu:
        cmd.extend(['-o', 'Global.use_gpu=false'])
    
    print(f"학습 시작...")
    print(f"명령어: {' '.join(cmd)}")
    print("-" * 60)
    
    subprocess.run(cmd, cwd=str(paddleocr_dir), env=env, check=True)
    
    print("\n학습 완료!")


# ============================================================
# 7. 모델 평가
# ============================================================

def run_evaluation(paddleocr_dir: Path, config_file: Path, checkpoint_path: str = None):
    """
    학습된 모델 평가
    """
    print("\n" + "=" * 60)
    print("7단계: 모델 평가")
    print("=" * 60)
    
    eval_script = paddleocr_dir / 'tools' / 'eval.py'
    
    if checkpoint_path is None:
        checkpoint_path = './output/rec_korean_finetune/best_accuracy'
    
    cmd = [
        sys.executable,
        str(eval_script),
        '-c', str(config_file),
        '-o', f'Global.checkpoints={checkpoint_path}'
    ]
    
    print(f"평가 실행 중...")
    subprocess.run(cmd, cwd=str(paddleocr_dir), check=True)


# ============================================================
# 8. 추론 모델 내보내기
# ============================================================

def export_model(paddleocr_dir: Path, config_file: Path, output_dir: Path):
    """
    추론용 모델로 변환
    """
    print("\n" + "=" * 60)
    print("8단계: 추론 모델 내보내기")
    print("=" * 60)
    
    export_script = paddleocr_dir / 'tools' / 'export_model.py'
    inference_dir = output_dir / 'inference'
    
    cmd = [
        sys.executable,
        str(export_script),
        '-c', str(config_file),
        '-o', 'Global.pretrained_model=./output/rec_korean_finetune/best_accuracy',
        f'Global.save_inference_dir={str(inference_dir).replace(chr(92), "/")}'
    ]
    
    print(f"모델 내보내기 중...")
    subprocess.run(cmd, cwd=str(paddleocr_dir), check=True)
    
    print(f"\n추론 모델 저장됨: {inference_dir}")
    return inference_dir


# ============================================================
# 9. 최종 모델 복사
# ============================================================

def save_final_model(paddleocr_dir: Path, data_dir: Path, final_model_dir: Path):
    """
    최종 모델을 지정된 폴더로 복사
    """
    print("\n" + "=" * 60)
    print("9단계: 최종 모델 저장")
    print("=" * 60)
    
    final_model_dir.mkdir(parents=True, exist_ok=True)
    
    # 추론 모델 복사
    inference_dir = paddleocr_dir / 'output' / 'rec_korean_finetune' / 'inference'
    
    if inference_dir.exists():
        for file in inference_dir.glob('*'):
            shutil.copy(file, final_model_dir)
        
        # 문자 사전도 복사
        dict_file = data_dir / 'korean_dict.txt'
        if dict_file.exists():
            shutil.copy(dict_file, final_model_dir / 'korean_dict.txt')
        
        print(f"모델 저장 완료: {final_model_dir}")
        
        # 사용법 출력
        print("\n" + "=" * 60)
        print("파인튜닝된 모델 사용법:")
        print("=" * 60)
        print(f'''
from paddleocr import PaddleOCR

ocr = PaddleOCR(
    rec_model_dir='{final_model_dir}',
    rec_char_dict_path='{final_model_dir / "korean_dict.txt"}',
    use_angle_cls=False,
    lang='korean'
)

result = ocr.ocr('your_image.jpg', cls=False)
for line in result[0]:
    bbox, (text, confidence) = line
    print(f"텍스트: {{text}}, 신뢰도: {{confidence:.4f}}")
''')
    else:
        print(f"오류: 추론 모델을 찾을 수 없습니다: {inference_dir}")


# ============================================================
# 메인 함수
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description='PaddleOCR 파인튜닝 스크립트',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
사용 예시:
  # 전처리 + 학습 전체 실행 (GPU 7번 사용)
  python train_paddleocr.py

  # 전처리만 실행
  python train_paddleocr.py --preprocess-only

  # 학습만 실행 (전처리 완료 후)
  python train_paddleocr.py --train-only

  # 학습 설정 변경
  python train_paddleocr.py --batch-size 64 --epochs 50 --lr 0.001
        '''
    )
    
    # 경로 설정
    parser.add_argument('--generated-dir', type=str, default='generated',
                        help='생성된 데이터 디렉토리 (기본값: generated)')
    parser.add_argument('--output-dir', type=str, default='paddle_data',
                        help='PaddleOCR 데이터 출력 디렉토리 (기본값: paddle_data)')
    parser.add_argument('--model-dir', type=str, default='models/paddleocr_korean_finetuned',
                        help='최종 모델 저장 디렉토리')
    
    # 학습 설정
    parser.add_argument('--batch-size', type=int, default=128,
                        help='배치 크기 (기본값: 128)')
    parser.add_argument('--epochs', type=int, default=100,
                        help='에폭 수 (기본값: 100)')
    parser.add_argument('--lr', type=float, default=0.0005,
                        help='학습률 (기본값: 0.0005)')
    parser.add_argument('--train-ratio', type=float, default=0.9,
                        help='Train/Val 분할 비율 (기본값: 0.9)')
    
    # GPU 설정
    parser.add_argument('--gpu', type=int, default=7,
                        help='사용할 GPU ID (기본값: 7)')
    parser.add_argument('--gpu-memory', type=float, default=0.95,
                        help='GPU 메모리 사용 비율 (0.0~1.0, 기본값: 0.95)')
    parser.add_argument('--cpu', action='store_true',
                        help='CPU 모드로 학습')
    
    # 실행 모드
    parser.add_argument('--preprocess-only', action='store_true',
                        help='전처리만 실행')
    parser.add_argument('--train-only', action='store_true',
                        help='학습만 실행 (전처리 건너뜀)')
    parser.add_argument('--eval-only', action='store_true',
                        help='평가만 실행')
    parser.add_argument('--export-only', action='store_true',
                        help='모델 내보내기만 실행')
    
    args = parser.parse_args()
    
    # GPU 환경 설정 (가장 먼저 실행 - paddle import 전에)
    if not args.cpu:
        setup_gpu_environment(gpu_id=args.gpu, memory_fraction=args.gpu_memory)
    
    # 경로 설정
    base_dir = Path(__file__).parent
    generated_dir = base_dir / args.generated_dir
    data_dir = base_dir / args.output_dir
    model_dir = base_dir / args.model_dir
    config_file = data_dir / 'rec_korean_finetune.yml'
    
    print("\n" + "=" * 60)
    print("PaddleOCR 파인튜닝")
    print("=" * 60)
    print(f"생성된 데이터: {generated_dir}")
    print(f"PaddleOCR 데이터: {data_dir}")
    print(f"최종 모델: {model_dir}")
    
    # GPU 확인 (학습 시에만)
    if not args.cpu and not args.preprocess_only:
        verify_gpu()
    
    # 1. 전처리
    if not args.train_only and not args.eval_only and not args.export_only:
        convert_to_paddle_format(generated_dir, data_dir, args.train_ratio)
        create_korean_dict(data_dir, data_dir / 'korean_dict.txt')
    
    if args.preprocess_only:
        print("\n전처리 완료!")
        return
    
    # 2. PaddleOCR 설정
    paddleocr_dir = setup_paddleocr(base_dir)
    
    # 3. 사전 학습 모델 다운로드
    pretrain_dir = paddleocr_dir / 'pretrain_models'
    pretrain_model_path = download_pretrain_model(pretrain_dir)
    
    # 4. 설정 파일 생성
    if not args.eval_only and not args.export_only:
        create_config_file(
            data_dir, config_file, pretrain_model_path,
            batch_size=args.batch_size,
            epoch_num=args.epochs,
            learning_rate=args.lr
        )
    
    # 5. 학습
    if not args.eval_only and not args.export_only:
        run_training(paddleocr_dir, config_file, use_gpu=not args.cpu, gpu_id=args.gpu)
    
    # 6. 평가
    if args.eval_only or not args.export_only:
        run_evaluation(paddleocr_dir, config_file)
    
    # 7. 모델 내보내기
    export_model(paddleocr_dir, config_file, paddleocr_dir / 'output' / 'rec_korean_finetune')
    
    # 8. 최종 모델 저장
    save_final_model(paddleocr_dir, data_dir, model_dir)
    
    print("\n" + "=" * 60)
    print("모든 작업 완료!")
    print("=" * 60)


if __name__ == '__main__':
    main()
