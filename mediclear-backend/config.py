import os
from dotenv import load_dotenv
from pymongo import MongoClient

# Ortam değişkenlerini yükle
load_dotenv()

# OpenAI API anahtarı
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise EnvironmentError("❌ OPENAI_API_KEY ortam değişkeni tanımlanmamış.")

# MongoDB bağlantısı
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URL)
db = client.get_database(os.getenv("MONGO_DB_NAME", "mediclear_db"))

# Koleksiyonlar
users_collection = db.get_collection("users")         # Kullanıcı hesapları ve profiller
reports_collection = db.get_collection("reports")     # Raporlar ve AI analizleri
