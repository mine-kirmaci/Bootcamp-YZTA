import os
import pytesseract
from PIL import Image
from dotenv import load_dotenv

# .env varsa yükle
load_dotenv()

# Eğer özel bir Tesseract yolu belirtildiyse onu kullan
CUSTOM_TESSERACT_PATH = os.getenv("TESSERACT_CMD")
if CUSTOM_TESSERACT_PATH:
    pytesseract.pytesseract.tesseract_cmd = CUSTOM_TESSERACT_PATH

def extract_text_from_image(image: Image.Image) -> str:
    """
    Görsel üzerinden OCR ile metin çıkarır.

    Args:
        image (PIL.Image.Image): OCR uygulanacak görsel.

    Returns:
        str: Görselden çıkarılan temizlenmiş metin veya hata mesajı.
    """
    try:
        raw_text = pytesseract.image_to_string(image)
        return raw_text.strip()
    except Exception as e:
        return f"⚠️ OCR işleminde hata oluştu: {e}"
