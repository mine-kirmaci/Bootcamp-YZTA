# ocr_service.py
import os
import pytesseract
from PIL import Image
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# Eğer varsa özel tesseract yolu tanımlanır
CUSTOM_TESSERACT_PATH = os.getenv("TESSERACT_CMD")
if CUSTOM_TESSERACT_PATH:
    pytesseract.pytesseract.tesseract_cmd = CUSTOM_TESSERACT_PATH

def extract_text_from_image(image: Image.Image) -> str:
    """
    Görsel üzerinden OCR ile metin çıkarır.

    Args:
        image (PIL.Image.Image): OCR uygulanacak görsel.

    Returns:
        str: Görselden çıkarılan metin.
    """
    try:
        return pytesseract.image_to_string(image)
    except Exception as e:
        return f"OCR hatası: {e}"
