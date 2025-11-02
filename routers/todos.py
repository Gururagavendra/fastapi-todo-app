
from typing import Annotated
from fastapi import APIRouter, Depends, Request
from fastapi import HTTPException, Path
from fastapi.responses import RedirectResponse
from starlette import status

from settings import db_dependency
from routers.auth import get_current_user, templates

from models import Todos
from schemas import TodoRequest
router = APIRouter(
    prefix='/todos',
    tags = ['todos']
)

#validate the jwt token
user_dependency = Annotated[dict, Depends(get_current_user)]
### Pages ###

def redirect_to_login():
    redirect_response = RedirectResponse(url="/auth/login-page", status_code=status.HTTP_302_FOUND)
    redirect_response.delete_cookie(key="access_token")
    return redirect_response



@router.get("/todo-page")
async def render_todo_page(request: Request, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get('access_token'))

        if user is None:
            return redirect_to_login()

        todos = db.query(Todos).filter(Todos.owner_id == user.get("id")).all()

        return templates.TemplateResponse("todo.html", {"request": request, "todos": todos, "user": user})

    except:
        return redirect_to_login()


@router.get('/add-todo-page')
async def render_todo_page(request: Request):
    try:
        user = await get_current_user(request.cookies.get('access_token'))

        if user is None:
            return redirect_to_login()

        return templates.TemplateResponse("add-todo.html", {"request": request, "user": user})

    except:
        return redirect_to_login()


@router.get("/edit-todo-page/{todo_id}")
async def render_edit_todo_page(request: Request, todo_id: int, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get('access_token'))

        if user is None:
            return redirect_to_login()

        todo = db.query(Todos).filter(Todos.id == todo_id).first()

        return templates.TemplateResponse("edit-todo.html", {"request": request, "todo": todo, "user": user})

    except:
        return redirect_to_login()
    
##endpoints

@router.get("/", status_code=status.HTTP_200_OK)
async def read_all_todo(user:user_dependency,db: db_dependency):
    print('authentication failed')
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    return db.query(Todos).filter(Todos.owner_id == user.get('id')).all()


@router.get("/todo/{task_id}", status_code = status.HTTP_200_OK)
def read_todo(user:user_dependency,db: db_dependency, task_id:int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    todo_model = db.query(Todos).filter(Todos.id == task_id).first()

    if todo_model:
        return todo_model
    raise HTTPException(status_code = 404, detail = 'resource not found')


@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency, db: db_dependency,
                      todo_request: TodoRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    todo_model = Todos(**todo_request.model_dump(), owner_id=user.get('id'))

    db.add(todo_model)
    db.commit()

@router.put("/todo/{task_id}",status_code=status.HTTP_204_NO_CONTENT)
def update_todo(user: user_dependency,updated_todo: TodoRequest,task_id:int, db:db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    todo_model =  db.query(Todos).filter(Todos.id == task_id).filter(Todos.owner_id == user.get('id')).first()

    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found.')

    update_data = updated_todo.model_dump()

    for field,value in update_data.items():
        if field == "id":
            continue
        setattr(todo_model,field,value)
    
    db.commit()

@router.delete("/todo/{task_id}",status_code=status.HTTP_204_NO_CONTENT)
def remove_todo(user: user_dependency,task_id:int,db:db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    todo_model =  db.query(Todos).filter(Todos.id == task_id).filter(Todos.owner_id == user.get('id')).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found.')
        
    db.delete(todo_model)   
    db.commit()


