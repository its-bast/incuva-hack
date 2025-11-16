from typing import Optional
from pydantic import BaseModel
from passlib.context import CryptContext
import json
import os

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(BaseModel):
    email: str
    name: str
    hashed_password: str

class UserInDB(User):
    def verify_password(self, plain_password: str) -> bool:
        # Truncar password si es muy largo (límite de bcrypt)
        if len(plain_password.encode('utf-8')) > 72:
            plain_password = plain_password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
        return pwd_context.verify(plain_password, self.hashed_password)

class UserManager:
    def __init__(self):
        self.users_file = "data/users.json"
        self._ensure_users_file()
    
    def hash_password(self, password: str) -> str:
        """Hash password con límite de 72 bytes para bcrypt"""
        # Truncate password to 72 bytes if necessary (bcrypt limitation)
        if len(password.encode('utf-8')) > 72:
            password = password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
        return pwd_context.hash(password)
    
    def _ensure_users_file(self):
        os.makedirs("data", exist_ok=True)
        if not os.path.exists(self.users_file):
            # Usuario por defecto - USAR EL NUEVO MÉTODO
            default_user = {
                "testuser@tomi.com.pe": {
                    "email": "testuser@tomi.com.pe",
                    "name": "Test User",
                    "hashed_password": self.hash_password("12345678")  # ← CAMBIO AQUÍ
                }
            }
            with open(self.users_file, "w") as f:
                json.dump(default_user, f, indent=2)
    
    def get_user(self, email: str) -> Optional[UserInDB]:
        try:
            with open(self.users_file, "r") as f:
                users = json.load(f)
            
            if email in users:
                return UserInDB(**users[email])
        except:
            pass
        return None
    
    def authenticate_user(self, email: str, password: str) -> Optional[UserInDB]:
        user = self.get_user(email)
        if user and user.verify_password(password):
            return user
        return None
    
    def create_user(self, email: str, name: str, password: str) -> bool:
        """Crear nuevo usuario"""
        try:
            users = {}
            if os.path.exists(self.users_file):
                with open(self.users_file, "r") as f:
                    users = json.load(f)
            
            if email in users:
                return False  # Usuario ya existe
            
            users[email] = {
                "email": email,
                "name": name,
                "hashed_password": self.hash_password(password)  # ← USAR MÉTODO SEGURO
            }
            
            with open(self.users_file, "w") as f:
                json.dump(users, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error creando usuario: {e}")
            return False

user_manager = UserManager()