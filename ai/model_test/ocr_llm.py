import httpx
import base64
import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv


load_dotenv()

# GMS API 설정
GMS_API_URL = "https://gms.ssafy.io/gmsapi/api.openai.com/v1/responses"
GMS_API_KEY = os.environ.get("OPENAI_API_KEY")


def encode_image_to_base64(image_path: str) -> str:
    """이미지 파일을 base64로 인코딩합니다."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def get_image_media_type(image_path: str) -> str:
    """이미지 파일의 미디어 타입을 반환합니다."""
    extension = Path(image_path).suffix.lower()
    media_types = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.webp': 'image/webp',
        '.bmp': 'image/bmp',
    }
    return media_types.get(extension, 'image/jpeg')


async def ocr_image(image_path: str) -> dict:
    """
    GPT Vision API를 사용하여 이미지에서 텍스트를 추출합니다.

    Args:
        image_path: 이미지 파일 경로

    Returns:
        OCR 결과를 담은 딕셔너리
    """
    # 이미지를 base64로 인코딩
    base64_image = encode_image_to_base64(image_path)
    media_type = get_image_media_type(image_path)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GMS_API_KEY}"
    }

    # Responses API 형식으로 요청
    payload = {
        "model": "gpt-5.2-pro",
        "input": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": "이 이미지에서 모든 텍스트를 추출해주세요. 한글과 영어 모두 정확하게 인식해주세요. 텍스트의 위치나 레이아웃을 최대한 유지하면서 추출해주세요."
                    },
                    {
                        "type": "input_image",
                        "image_url": f"data:{media_type};base64,{base64_image}"
                    }
                ]
            }
        ]
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(GMS_API_URL, headers=headers, json=payload)
        
        # 에러 응답 확인
        if response.status_code != 200:
            print(f"API 에러 ({response.status_code}): {response.text}")
            response.raise_for_status()
        
        result = response.json()
        print(f"API 응답: {result}")

    # 응답에서 텍스트 추출
    extracted_text = result.get("output", [{}])[0].get("content", [{}])[0].get("text", "")
    
    # 다른 응답 형식도 처리
    if not extracted_text and "output" in result:
        extracted_text = str(result["output"])

    return {
        'file': image_path,
        'full_text': extracted_text,
        'model': 'gpt-5.2-pro'
    }


async def ocr_folder(folder_path: str) -> list:
    """
    폴더 내 모든 이미지 파일을 OCR 처리합니다.

    Args:
        folder_path: 이미지가 있는 폴더 경로

    Returns:
        각 이미지의 OCR 결과 리스트
    """
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp'}
    folder = Path(folder_path)

    results = []
    for file in folder.iterdir():
        if file.suffix.lower() in image_extensions:
            print(f"처리 중: {file.name}")
            result = await ocr_image(str(file))
            results.append(result)
            print(f"완료: {file.name}\n")

    return results


async def main():
    # img 폴더 경로
    img_folder = Path(__file__).parent / "img"

    if not img_folder.exists():
        print(f"폴더를 찾을 수 없습니다: {img_folder}")
        return

    if not GMS_API_KEY:
        print("OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
        print(".env 파일에 OPENAI_API_KEY=your_key 형식으로 설정해주세요.")
        return

    print("=" * 50)
    print("한글 OCR 시작 (GPT-5.2-pro Vision)")
    print("=" * 50)

    # 폴더 내 모든 이미지 OCR
    results = await ocr_folder(str(img_folder))

    # 결과 출력
    print("\n" + "=" * 50)
    print("OCR 결과")
    print("=" * 50)

    for result in results:
        print(f"\n파일: {result['file']}")
        print(f"모델: {result['model']}")
        print("-" * 40)
        print("추출된 텍스트:")
        print(result['full_text'])
        print("-" * 40)


if __name__ == "__main__":
    asyncio.run(main())
