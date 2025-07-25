import hashlib
from datetime import datetime
from config import users_collection

def hash_password(password: str) -> str:
    """Verilen şifreyi SHA256 ile hash'ler."""
    return hashlib.sha256(password.encode()).hexdigest()

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
