from datetime import date
import email
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
        role = Role.common,
        active = 1,
        created_at = date.today()
    )
    try:
        await database.execute(query)
        return({"message" : "Le compte a été créé avec succès"})
    except(Exception):
        raise HTTPException(status_code= status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Une erreur est survenue... Il se pourrait que l'adresse mail soit déjà utilisée!")




# For user sign in
@router.post("/login", status_code=status.HTTP_200_OK)
async def login(usr:LoginSchema):
    query = users.select().where(users.c.email  == usr.email)
    user = await database.fetch_one(query)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND_MESSAGE)
    if not pbkdf2_sha256.verify(usr.password, user.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND_MESSAGE)
    if not user.active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Votre compte n'est plus actif")

    return {"user_id":user.id, "username":user.name, "role": Role[user.role].value, "token":get_token(user.email)}


@router.post("/logout", status_code=status.HTTP_200_OK, dependencies=[Depends(JWTBearer())])
async def logout(req:Request):
    header_param = req.headers.get("Authorization").split(" ")
    if(add_blacklist_token(header_param[1])):
            raise HTTPException(status_code=status.HTTP_200_OK, detail="Déconnexion effectuée avec succès")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Une erreur est survenue! Vous êtes toujours connectés, Veuillez réessayer")


@router.delete("/delete", status_code=status.HTTP_200_OK, dependencies=[Depends(JWTBearer())])
async def delete_user(user_id:int = Form(...), usr_email:str = Form(...), pwd:str = Form(...)):
    query = users.select().where(users.c.id  == user_id)
    user = await database.fetch_one(query)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND_MESSAGE)
    if not pbkdf2_sha256.verify(pwd, user.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND_MESSAGE)
    
    query = users.update().where(users.c.id == user_id).values(
        active = 0,
        email = '[Archived]'+usr_email
    )
    await database.execute(query)
    return {
        "removed": True,
        "message": "Votre compte a été supprimé avec succès"
    }

