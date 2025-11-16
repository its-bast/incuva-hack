from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import HTTPException, status
import os
import secrets

def get_secret_key():
    """Obtener o generar clave JWT segura"""
    secret = os.getenv("JWT_SECRET_KEY")
    
    if not secret:
        # En desarrollo, generar clave temporal segura
        secret = secrets.token_urlsafe(32)
        print("⚠️ JWT_SECRET_KEY no encontrada. Usando clave temporal.")
        print(f"🔑 Para producción, define: JWT_SECRET_KEY={secret}")
    
    if len(secret) < 32:
        print("⚠️ JWT_SECRET_KEY muy corta. Mínimo 32 caracteres recomendado.")
    
    return secret

SECRET_KEY = get_secret_key()
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("TOKEN_EXPIRE_MINUTES", "1440"))  # 24h

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Crear token JWT seguro"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Agregar metadata de seguridad
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),  # Issued at
        "type": "access_token"     # Tipo de token
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> str:
    """Verificar token JWT y devolver email"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Verificar tipo de token
        if payload.get("type") != "access_token":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tipo de token inválido"
            )
        
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token sin usuario"
            )
        
        return email
        
    except JWTError as e:
        print(f"❌ Error JWT: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado"
        )