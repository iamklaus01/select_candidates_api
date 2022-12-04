from datetime import date
from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from passlib.hash import pbkdf2_sha256
from sqlalchemy import func, select
import re

from database import database
from utils.customException import EmailSyntaxeError
from utils.util import check_user, format_candidates_files_data, format_user_files
from utils.email import mail_to, verify
from models.authSchema import LoginSchema
from token_dependencie import JWTBearer
from tables import Role, users, candidates_files, selection_files
from token_handler import get_token, add_blacklist_token

EMAIL_PATTERN = re.compile("^[\w\-\.]+@([\w]+\.)+[\w]{2,4}$")
USER_NOT_FOUND_MESSAGE = "User not found! The email address or username is incorrect"

router = APIRouter()

# For user sign up
@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(request:Request, fullname:str = Form(...), email:str = Form(...), password:str = Form(...), pwd_confirmed:str = Form(...)):
    if not re.match(EMAIL_PATTERN, email):
        raise EmailSyntaxeError()
    if password != pwd_confirmed:
        raise HTTPException(status_code= status.HTTP_409_CONFLICT, detail="Non-compliant passwords")
    hash_pwd = pbkdf2_sha256.hash(password)
    query = users.insert().values(
        name = fullname,
        email = email,
        password = hash_pwd,
        role = Role.common,
        active = 1,
        verified = False,
        created_at = date.today()
    )
    try:
        await database.execute(query)
        await mail_to(fullname, email, request)
        return({"message" : "The account has been successfully created! A mail has been sent to you... Check your inbox to verify your email!"})
    except Exception as e:
        raise HTTPException(status_code= status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# Verify email
@router.get("/verify_user/{token}")
async def verify_user(token:str):
    try:
        print(token)
        message = await verify(token)
        print(message)
        return {'message' : message}
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    

# For user sign in
@router.post("/login", status_code=status.HTTP_200_OK)
async def login(usr:LoginSchema, request:Request):
    query = users.select().where(users.c.email  == usr.email)
    user = await database.fetch_one(query)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND_MESSAGE)
    if not pbkdf2_sha256.verify(usr.password, user.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND_MESSAGE)
    if not user.verified:
        await mail_to(user.name, user.email, request)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Your email address is still not verified! An email has been sent to you to verify it!")
    if not user.active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Your account is no longer active")

    return {"user_id":user.id, "username":user.name, "role": Role[user.role].value, "token":get_token(user.email)}


@router.post("/logout", status_code=status.HTTP_200_OK, dependencies=[Depends(JWTBearer())])
async def logout(req:Request):
    header_param = req.headers.get("Authorization").split(" ")
    if(add_blacklist_token(header_param[1])):
        raise HTTPException(status_code=status.HTTP_200_OK, detail="Déconnexion effectuée avec succès")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Une erreur est survenue! Vous êtes toujours connectés, Veuillez réessayer")


@router.delete("/delete", status_code=status.HTTP_200_OK, dependencies=[Depends(JWTBearer())])
async def delete_user(user_id:int = Form(...), user_email:str = Form(...), pwd:str = Form(...)):
    query = users.select().where(users.c.id  == user_id)
    user = await database.fetch_one(query)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND_MESSAGE)
    if not pbkdf2_sha256.verify(pwd, user.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND_MESSAGE)
    
    query = users.update().where(users.c.id == user_id).values(
        active = 0,
        email = '[Archived]'+user_email
    )
    await database.execute(query)
    return {
        "removed": True,
        "message": "Votre compte a été supprimé avec succès"
    }

@router.get("/profile/{user_id}", status_code=status.HTTP_200_OK, dependencies=[Depends(JWTBearer())])
async def get_user_profile(user_id:int):
    query = users.select().where(users.c.id  == user_id)
    user = await database.fetch_one(query)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur introuvable")
    count_files = await database.fetch_one( select([func.count(candidates_files.c.id)]) )
    count_sol = await database.fetch_one( select([func.count(selection_files.c.id)]) )

    return {
        'name' : user.name,
        'email' : user.email,
        'n_files' : count_files.count_1,
        'n_sol' : count_sol.count_1
    }

@router.put("/profile/update/{user_id}", status_code=status.HTTP_202_ACCEPTED, dependencies=[Depends(JWTBearer())])
async def update_profile(user_id: int, fullname:str = Form(...)):
    query = users.update().where(users.c.id == user_id).values(
        name = fullname,
    )
    await database.execute(query)
    query = users.select().where(users.c.id  == user_id)
    usr = await database.fetch_one(query)
    return {
        'name' : usr.name,
        'email' : usr.email,
    }

@router.get("/files/{user_id}", dependencies=[Depends(JWTBearer())])
async def get_users_files(user_id:int):

    if not await check_user(user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    c_file_id = []

    query = candidates_files.select().where(candidates_files.c.user_id == user_id)
    c_files = await database.fetch_all(query)

    for c_file in c_files:
        c_file_id.append(c_file.id)

    query = selection_files.select().where(selection_files.c.candidatesFile_id.in_(c_file_id))
    sol_files = await database.fetch_all(query)

    format_c_files = format_candidates_files_data(c_files)
    return format_user_files(format_c_files, sol_files)