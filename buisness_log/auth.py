from fastapi import FastAPI, Depends
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import jwt
from cryptography.fernet import Fernet
from secret_key import f,encrypted

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
SECRET_KEY = f.decrypt(encrypted).decode() #Notice, secret key is decrypted in this file, not in "secret_key.py" file!, File "secret_key.py" is added to .gitignore for security reasons!
ALGORITHM = "HS256" 
TOKEN_EXPIRE_MINUTES = 30

def create_jwt_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM, expires_delta=datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE_MINUTES))

def get_user_from_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]) 
        return payload.get("sub") 
    except jwt.ExpiredSignatureError:
        pass 
    except jwt.InvalidTokenError:
        pass