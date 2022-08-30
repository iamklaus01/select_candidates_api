from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from passlib.hash import pbkdf2_sha256
import re

from database import database
from utils.customException import EmailSyntaxeError
from models.authSchema import LoginSchema
from token_dependencie import JWTBearer
from tables import Role, users
from token_handler import get_token, add_blacklist_token

EMAIL_PATTERN = re.compile("^[\w\-\.]+@([\w]+\.)+[\w]{2,4}$")
USER_NOT_FOUND_MESSAGE = "Utilisateur introuvable! L'adresse mail ou le nom d'utilisateur est incorrecte"

router = APIRouter()

# For user sign up
@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(fullname:str = Form(...), email:str = Form(...), password:str = Form(...), pwd_confirmed:str = Form(...)):
    if not re.match(EMAIL_PATTERN, email):
        raise EmailSyntaxeError()
    if password != pwd_confirmed:
        raise HTTPException(status_code= status.HTTP_409_CONFLICT, detail="Mots de passe non conformes")
    hash_pwd = pbkdf2_sha256.hash(password)
    query = users.insert().values(
        name = fullname,
        email = email,
        password = hash_pwd,
        role = Role.common
    )
    await database.execute(query)
    return({"message" : "Le compte a été créé avec succès"})

# For user sign in
@router.post("/login", status_code=status.HTTP_200_OK)
async def login(usr:LoginSchema):
    query = users.select().where(users.c.email  == usr.email)
    user = await database.fetch_one(query)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND_MESSAGE)
    if not pbkdf2_sha256.verify(usr.password, user.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND_MESSAGE)
    return {"user_id":user.id, "username":user.name, "role": Role[user.role].value, "token":get_token(user.email)}


@router.post("/logout", status_code=status.HTTP_200_OK, dependencies=[Depends(JWTBearer())])
async def logout(req:Request):
    header_param = req.headers.get("Authorization").split(" ")
    if(add_blacklist_token(header_param[1])):
            raise HTTPException(status_code=status.HTTP_200_OK, detail="Déconnexion effectuée avec succès")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Une erreur est survenue! Vous êtes toujours connectés, Veuillez réessayer")


@router.delete("/admin/delete", status_code=status.HTTP_200_OK, dependencies=[Depends(JWTBearer())])
async def delete_user(user_id:str = Form(...), admin_email:str = Form(...), admin_pwd:str = Form(...)):
    query = users.select().where(users.c.id  == admin_email)
    user = await database.fetch_one(query)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND_MESSAGE)
    if not pbkdf2_sha256.verify(admin_pwd, user.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND_MESSAGE)
    if Role[user.role] != Role.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Vous n'êtes pas autorisé(e)s à réaliser une telle opération")
    
    query = users.delete().where(users.c.id == user_id)
    await database.execute(query)
    return {
        "removed": True,
        "message": "Utilisateur supprimée avec succès"
    }

