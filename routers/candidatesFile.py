from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from os import getcwd, remove
from typing import List
from database import database
import shutil


from models.candidatesFileSchema import CandidateFile
from tables import Role, candidates_files, features, users
from token_dependencie import JWTBearer
from utils.util import rename_file, get_file_path, extract_features, FileType


router = APIRouter()

@router.get("/", response_model=List[CandidateFile], dependencies=[Depends(JWTBearer())])
async def get_candidates_files(user_id :int):
    query = users.select().where(users.c.id  == user_id)
    user = await database.fetch_one(query)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur introuvable")
    if user.role.upper() != Role.admin.value:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Vous n'êtes pas autorisé(e)s pour une telle opération")
    query = candidates_files.select()
    all_files = await database.fetch_all(query)
    return all_files

@router.get("/user", response_model=List[CandidateFile], dependencies=[Depends(JWTBearer())])
async def get_users_candidates_files(user_id:int):
    query = candidates_files.select().where(candidates_files.c.user_id == user_id)
    user_files = await database.fetch_all(query)
    return user_files

@router.get("/single", response_model=CandidateFile, dependencies=[Depends(JWTBearer())])
async def get_single_candidate_file(id:int):
    query = candidates_files.select().where(candidates_files.c.id == id)
    candidate_file = await database.fetch_one(query)
    return {**candidate_file}


@router.post("/add/{user_id}", response_model=CandidateFile, status_code=status.HTTP_201_CREATED, dependencies=[Depends(JWTBearer())])
async def store_candidates_files(user_id:int ,c_file:UploadFile = File(...)):
    c_file.filename = rename_file(c_file.filename)
    with open(f'files/candidates/{c_file.filename}', "wb") as buffer:
        shutil.copyfileobj(c_file.file, buffer)
    file_path = get_file_path(FileType.cFile, c_file.filename)
    c_file_features = extract_features(file_path)

    query = features.insert().values(
        extension = c_file.filename.split(".")[1],
        path = file_path,
        user_id = user_id
    )
    record_id = await database.execute(query)

    for i in range(len(c_file_features[0])):
        query = features.insert().values(
            label = c_file_features[0][i],
            valueType = c_file_features[1][i],
            candidatesFile_id = record_id
        )
        await database.execute(query)

    query = candidates_files.select().where(candidates_files.c.id == record_id)
    row = await database.fetch_one(query)
    return {**row}


@router.delete("/remove", status_code = status.HTTP_200_OK, dependencies=[Depends(JWTBearer())])
async def delete_candidates_file(id:int):
    query = candidates_files.delete().where(candidates_files.c.id == id)
    deleted_file = await database.execute(query)
    try:
        remove(getcwd() + "/" + deleted_file.path)
        return {
            "removed": True,
            "message" : "Le fichier et ses données correspondantes ont été supprimé avec succès:"
        }   
    except FileNotFoundError:
        return {
            "removed": False,
            "message": "Une erreur est survenue durant la supression du fichier"
        }



