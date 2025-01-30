import datetime
from typing import Optional
import jwt
import toml

with open('config.toml', 'r') as f:
    config = toml.load(f)


ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 
SECRET_KEY = config['Token']['SECRET_KEY']

def create_access_token(data: dict, expires_delta: Optional[datetime.timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.now() + expires_delta
    else:
        expire = datetime.datetime.now() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt   