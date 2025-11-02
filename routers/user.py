from fastapi import APIRouter, HTTPException

from models import Todos, Users
from starlette import status
from settings import Bcrypt_context, db_dependency
from routers.todos import user_dependency
from schemas import CreateUserRequest
from sqlalchemy.exc import SQLAlchemyError
from utils import classify_db_error



router = APIRouter(
    prefix='/user',
    tags = ['Users']
)
 
@router.get("/",status_code=status.HTTP_200_OK)
def read_user(user:user_dependency,db:db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    return db.query(Users).filter(Todos.owner_id == user.get('id')).all()

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_user(new_user: CreateUserRequest, db: db_dependency):
    user = Users(
        email=new_user.email,
        username=new_user.username,
        hashed_password=Bcrypt_context.hash(new_user.password),
        is_active=True,
        role=new_user.role
    )
    db.add(user)
    try:
        db.commit()
        db.refresh(user)  # load generated columns (e.g., id) back into the instance
    except SQLAlchemyError as exc:
        db.rollback()
        http_status, detail = classify_db_error(exc)
        raise HTTPException(status_code=http_status, detail=detail)
    return user
