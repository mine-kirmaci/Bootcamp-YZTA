import os
from dotenv import load_dotenv
from pymongo import MongoClient

# Ortam değişkenlerini yükle (.env dosyasından)
load_dotenv()

# --- OpenAI API Anahtarı ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise EnvironmentError("❌ OPENAI_API_KEY ortam değişkeni tanımlanmamış.")

# --- MongoDB Ayarları ---
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "mediclear_db")

try:
    client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)
    db = client[MONGO_DB_NAME]
    # Bağlantı testi
    client.admin.command('ping')
except Exception as e:
    raise ConnectionError(f"❌ MongoDB bağlantı hatası: {e}")

# --- Koleksiyonlar ---
users_collection = db.get_collection("users")          # Kullanıcı hesapları ve profiller
reports_collection = db.get_collection("reports")      # OCR & AI analiz raporları
