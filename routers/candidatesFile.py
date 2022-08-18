from operator import and_
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from os import getcwd, remove
from typing import List
from database import database
import shutil


from tables import Role, ValueType, candidates_files, features, users
from token_dependencie import JWTBearer
from solver.solver import solve
from models.candidatesFileSchema import CandidateFile
from utils.util import check_user, rename_file, get_file_path, extract_features, FileType

FILE_NOT_FOUND_MESSAGE = "Fichier non retrouvé! Rassurez-vous d'avoir le bon identifiant"

router = APIRouter()

@router.get("/", response_model=List[CandidateFile], dependencies=[Depends(JWTBearer())])
async def get_candidates_files(user_id :int):

    query = users.select().where(users.c.id  == user_id)
    user = await database.fetch_one(query)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur introuvable")
    if Role[user.role] != Role.admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Vous n'êtes pas autorisé(e)s pour une telle opération")
    query = candidates_files.select()
    all_files = await database.fetch_all(query)
    return all_files

@router.get("/user", response_model=List[CandidateFile], dependencies=[Depends(JWTBearer())])
async def get_users_candidates_files(user_id:int):

    if not await check_user(user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur non retrouvé")

    query = candidates_files.select().where(candidates_files.c.user_id == user_id)
    user_files = await database.fetch_all(query)
    return user_files

@router.get("/single", response_model=CandidateFile, dependencies=[Depends(JWTBearer())])
async def get_single_candidate_file(id:int):

    query = candidates_files.select().where(candidates_files.c.id == id)
    candidate_file = await database.fetch_one(query)
    if not candidate_file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=FILE_NOT_FOUND_MESSAGE)

    return {**candidate_file}


@router.post("/add/{user_id}", response_model=CandidateFile, status_code=status.HTTP_201_CREATED, dependencies=[Depends(JWTBearer())])
async def store_candidates_files(user_id:int ,c_file:UploadFile = File(...), ignore_col:int = Form(...)):
    if not await check_user(user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur introuvable. Vous devriez avoir un compte pour utiliser nos services.")

    c_file.filename = rename_file(c_file.filename)
    with open(f'files/candidates/{c_file.filename}', "wb") as buffer:
        shutil.copyfileobj(c_file.file, buffer)
    file_path = get_file_path(FileType.cFile, c_file.filename)
    c_file_features = extract_features(file_path, ignore_col)

    query = candidates_files.insert().values(
        extension = c_file.filename.split(".")[1],
        path = file_path,
        user_id = user_id
    )
    record_id = await database.execute(query)

    for i in range(len(c_file_features[0])):
        query = features.insert().values(
            label = c_file_features[0][i],
            valueType = ( ValueType.multiple, ValueType.integer ) [c_file_features[1][i] == "int64"],
            candidatesFile_id = record_id
        )
        await database.execute(query)

    query = candidates_files.select().where(candidates_files.c.id == record_id)
    row = await database.fetch_one(query)
    return {**row}


@router.delete("/remove", status_code = status.HTTP_200_OK, dependencies=[Depends(JWTBearer())])
async def delete_candidates_file(id:int):
    query = candidates_files.select().where(candidates_files.c.id == id)
    file_to_delete = await database.fetch_one(query)
    if not file_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=FILE_NOT_FOUND_MESSAGE)

    query = candidates_files.delete().where(candidates_files.c.id == id)
    await database.execute(query)
    try:
        print(file_to_delete)
        remove(getcwd() + "/" + file_to_delete["path"])
        return {
            "removed": True,
            "message" : "Le fichier et ses données correspondantes ont été supprimé avec succès:"
        }   
    except FileNotFoundError:
        return {
            "removed": False,
            "message": "Une erreur est survenue durant la supression du fichier"
        }



@router.get("/solve/{file_id}", dependencies=[Depends(JWTBearer())])
async def resolve(file_id : int):
    query = candidates_files.select().where(candidates_files.c.id == file_id)
    candidate_file = await database.fetch_one(query)
    if not candidate_file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=FILE_NOT_FOUND_MESSAGE)

    query = features.select().where(and_(features.c.candidatesFile_id  == file_id, features.c.valueType == ValueType.integer))
    all_int_features = await database.fetch_all(query)

    query = features.select().where(and_(features.c.candidatesFile_id  == file_id, features.c.valueType == ValueType.multiple))
    all_enum_features = await database.fetch_all(query)

    return await solve(candidate_file, all_int_features, all_enum_features)