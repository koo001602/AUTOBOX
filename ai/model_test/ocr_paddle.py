from paddleocr import PaddleOCR
import cv2
import numpy as np
from pathlib import Path


def read_image_with_korean_path(image_path: str):
    """한글 경로의 이미지를 읽습니다."""
    with open(image_path, 'rb') as f:
        img_array = np.frombuffer(f.read(), dtype=np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    return img


def ocr_image(image_path: str, ocr_engine) -> dict:
    """
    이미지에서 텍스트를 추출합니다.

    Args:
        image_path: 이미지 파일 경로
        ocr_engine: PaddleOCR 인스턴스

    Returns:
        OCR 결과를 담은 딕셔너리
    """
    # 한글 경로 지원하여 이미지 읽기
    img = read_image_with_korean_path(image_path)

    # OCR 수행
    results = ocr_engine.ocr(img, cls=True)

    # 결과 정리
    extracted_texts = []
    full_text = []

    if results and results[0]:
        for line in results[0]:
            bbox = line[0]
            text = line[1][0]
            confidence = line[1][1]

            extracted_texts.append({
                'text': text,
                'confidence': round(confidence * 100, 2),
                'bbox': bbox
            })
            full_text.append(text)

    return {
        'file': image_path,
        'full_text': '\n'.join(full_text),
        'details': extracted_texts
    }


def ocr_folder(folder_path: str) -> list:
    """
    폴더 내 모든 이미지 파일을 OCR 처리합니다.

    Args:
        folder_path: 이미지가 있는 폴더 경로

    Returns:
        각 이미지의 OCR 결과 리스트
    """
    # PaddleOCR 초기화 (한국어)
    print("PaddleOCR 모델 로딩 중...")
    ocr_engine = PaddleOCR(use_angle_cls=True, lang='korean', use_gpu=False)
    print("모델 로딩 완료!\n")

    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp'}
    folder = Path(folder_path)

    results = []
    for file in folder.iterdir():
        if file.suffix.lower() in image_extensions:
            print(f"처리 중: {file.name}")
            result = ocr_image(str(file), ocr_engine)
            results.append(result)
            print(f"완료: {file.name}\n")

    return results


def main():
    # img 폴더 경로
    img_folder = Path(__file__).parent / "img"
    output_file = Path(__file__).parent / "ocr_paddle_result.txt"

    if not img_folder.exists():
        print(f"폴더를 찾을 수 없습니다: {img_folder}")
        return

    print("=" * 50)
    print("한글 OCR 시작 (PaddleOCR)")
    print("=" * 50)

    # 폴더 내 모든 이미지 OCR
    results = ocr_folder(str(img_folder))

    # 결과를 파일로 저장
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 50 + "\n")
        f.write("OCR 결과 (PaddleOCR)\n")
        f.write("=" * 50 + "\n")

        for result in results:
            f.write(f"\n파일: {result['file']}\n")
            f.write("-" * 40 + "\n")
            f.write("추출된 텍스트:\n")
            f.write(result['full_text'] + "\n")
            f.write("-" * 40 + "\n")
            f.write("상세 정보:\n")
            for detail in result['details']:
                f.write(f"  - '{detail['text']}' (신뢰도: {detail['confidence']}%)\n")

    print(f"\n결과가 저장되었습니다: {output_file}")


if __name__ == "__main__":
    main()
