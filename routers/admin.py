from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Form, status
from sqlalchemy import func, select
from database import database
from token_dependencie import JWTBearer
from tables import Role, users, selection_files, candidates_files
from utils.customException import EmailSyntaxeError
from passlib.hash import pbkdf2_sha256

import re


EMAIL_PATTERN = re.compile("^[\w\-\.]+@([\w]+\.)+[\w]{2,4}$")
USER_NOT_FOUND_MESSAGE = "User not found! The email address or username is incorrect"

router = APIRouter()

@router.post("/user/register", status_code=status.HTTP_201_CREATED)
async def register(fullname:str = Form(...), email:str = Form(...), password:str = Form(...), pwd_confirmed:str = Form(...)):
    if not re.match(EMAIL_PATTERN, email):
        raise EmailSyntaxeError()
    if password != pwd_confirmed:
        raise HTTPException(status_code= status.HTTP_409_CONFLICT, detail="Non-compliant passwords")
    hash_pwd = pbkdf2_sha256.hash(password)
    query = users.insert().values(
        name = fullname,
        email = email,
        password = hash_pwd,
        role = Role.admin,
        active = 1,
        created_at = date.today()
    )
    await database.execute(query)
    return({"message" : "The admin account has been successfully created"})

@router.delete("/user/delete", status_code=status.HTTP_200_OK, dependencies=[Depends(JWTBearer())])
async def delete_user(user_id:int = Form(...), admin_email:str = Form(...), admin_pwd:str = Form(...)):
    query = users.select().where(users.c.email  == admin_email)
    user = await database.fetch_one(query)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND_MESSAGE)
    if not pbkdf2_sha256.verify(admin_pwd, user.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND_MESSAGE)
    if Role[user.role] != Role.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized for such an operation !")
    
    query = users.select().where(users.c.id  == user_id)
    user_to_delete = await database.fetch_one(query)


    query = users.update().where(users.c.id == user_id).values(
        active = 0,
        email = '[Archived]'+user_to_delete.email
    )
    await database.execute(query)
    return {
        "removed": True,
        "message": "User archived successfully"
    }


@router.get("/stats/{user_id}", dependencies=[Depends(JWTBearer())])
async def get_system_stats(user_id :int):

    query = users.select().where(users.c.id  == user_id)
    user = await database.fetch_one(query)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    # if Role[user.role] != Role.admin:
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Vous n'êtes pas autorisé(e)s pour une telle opération")

    count_files = await database.fetch_one( select([func.count(candidates_files.c.id)]) )
    count_users = await database.fetch_one( select([func.count(users.c.id)]) )
    count_sol = await database.fetch_one( select([func.count(selection_files.c.id), func.avg(selection_files.c.satisfaction)]) )

    return {
        'n_files' : count_files.count_1,
        'n_users' : count_users.count_1,
        'n_sol' : count_sol.count_1,
        'percent' : count_sol.avg_1
    }

@router.get("/all_users/{user_id}", dependencies=[Depends(JWTBearer())])
async def get_system_users(user_id :int):

    query = users.select().where(users.c.id  == user_id)
    user = await database.fetch_one(query)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User nor found !")
    if Role[user.role] != Role.admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authorized for such an operation")

    query = select([users.c.name, users.c.email, users.c.role, users.c.active, users.c.created_at])
    all_users = await database.fetch_all(query)
    

    return all_users