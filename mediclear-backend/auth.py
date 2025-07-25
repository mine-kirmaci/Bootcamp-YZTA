import hashlib
import re
from datetime import datetime
from config import users_collection

def hash_password(password: str) -> str:
    """Verilen şifreyi SHA256 ile hash'ler."""
    return hashlib.sha256(password.encode()).hexdigest()

def is_valid_email(email: str) -> bool:
    """E-posta formatını kontrol eder."""
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

def authenticate_user(email: str, password: str) -> bool:
    """Kullanıcıyı e-posta ve şifre ile doğrular."""
    user = users_collection.find_one({"email": email})
    if not user:
        return False
    return user.get("password") == hash_password(password)

def register_user(email: str, password: str, profile: dict = None) -> bool:
    """
    Yeni kullanıcıyı kaydeder. Zaten kayıtlıysa False döner.
    Profil bilgileri varsa 'profile' altında saklanır.
    """
    if not is_valid_email(email):
        return False

    existing = users_collection.find_one({"email": email})
    if existing:
        return False

    user_data = {
        "email": email,
        "password": hash_password(password),
        "created_at": datetime.utcnow(),
        "profile": profile or {}
    }

    users_collection.insert_one(user_data)
    return True

def update_user_profile(email: str, new_profile: dict) -> bool:
    """Kullanıcının profilini günceller."""
    result = users_collection.update_one(
        {"email": email},
        {"$set": {"profile": new_profile}}
    )
    return result.modified_count > 0
