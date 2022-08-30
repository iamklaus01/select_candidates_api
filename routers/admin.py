from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from sqlalchemy import func
from database import database
from token_dependencie import JWTBearer
from tables import Role, users, selection_files, candidates_files


router = APIRouter()

@router.get("/stats", dependencies=[Depends(JWTBearer())])
async def get_system_stats(user_id :int):

    query = users.select().where(users.c.id  == user_id)
    user = await database.fetch_one(query)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur introuvable")
    if Role[user.role] != Role.admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Vous n'êtes pas autorisé(e)s pour une telle opération")

    count_files = func.count(candidates_files.c.id)
    count_sol = func.count(users.c.id)
    count_users = func.count(selection_files.c.id)
    

    return {
        'n_files' : count_files,
        'n_sol' : count_sol,
        'n_users' : count_users
    }