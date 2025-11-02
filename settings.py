from typing import Annotated
from database import SessionLocal
from sqlalchemy.orm import Session

from fastapi import Depends
from passlib.context import CryptContext



#for db connection
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]


#for password hashing
Bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated = 'auto')


#for jwt (token generation)
SECRET_KEY = 'c776f5375c9ff14bc74a3f04d766477ff1b7fa5279da1286008e1f537f1c399b'
ALGORITHM = 'HS256'