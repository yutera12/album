import os
from pwdlib import PasswordHash
from dotenv import load_dotenv
load_dotenv()

password_hash = PasswordHash.recommended()
DUMMY_HASH = password_hash.hash("dummypassword")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = None
SECRET_KEY = os.getenv("SECRET_KEY")
if SECRET_KEY is None:
    raise RuntimeError("環境変数 SECRET_KEY が設定されていません")