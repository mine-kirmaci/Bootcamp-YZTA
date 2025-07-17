import pytesseract
from PIL import Image
import io

# pytesseract'ın sistem PATH'inde olduğundan emin olun veya exe yolunu belirtin.
# Örneğin: pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# Eğer Linux veya macOS kullanıyorsanız ve tesseract yüklüyse bu satıra genellikle gerek kalmaz.

def extract_text_from_image(image: Image.Image) -> str:
    """
    PIL Image nesnesinden metin çıkarır.

    Args:
        image (PIL.Image.Image): Metin çıkarılacak görüntü nesnesi.

    Returns:
        str: Görüntüden çıkarılan metin.
    """
    return pytesseract.image_to_string(image)