# config.py
import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# Ortam değişkeninden API anahtarını al
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Anahtarın yüklenip yüklenmediğini kontrol etmek için basit bir kontrol
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY ortam değişkeni ayarlanmamış. Lütfen .env dosyanızı kontrol edin veya ortam değişkeni olarak ayarlayın.")