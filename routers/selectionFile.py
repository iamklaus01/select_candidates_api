from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from database import database

from models.selectionFileSchema import SelectionFile, SelectionFileIn, SelectionFileToDelete
from tables import selection_files, users
from token_dependencie import JWTBearer
from passlib.hash import pbkdf2_sha256

router = APIRouter()

USER_NOT_FOUND_MESSAGE = "User not found! The email address or username is incorrect"

@router.get("/cfile", response_model=List[SelectionFile], dependencies=[Depends(JWTBearer())])
async def get_selection_file(cfile_id:int):
    query = selection_files.select().where(selection_files.c.candidatesFile_id == cfile_id)
    all_files = await database.fetch_all(query)
    return all_files

@router.get("/{id}", response_model=SelectionFile, dependencies=[Depends(JWTBearer())])
async def get_single_selection_file(id:int):
    query = selection_files.select().where(selection_files.c.id == id)
    candidate_file = await database.fetch_one(query)
    return {**candidate_file}


@router.post("/log", response_model=SelectionFile, status_code=status.HTTP_201_CREATED, dependencies=[Depends(JWTBearer())])
async def store_selection_file(sol_file : SelectionFileIn):
    
    query = selection_files.insert().values(
        encodedFile = sol_file.encodedFile,
        status = sol_file.status,
        nbre_sol = sol_file.n_sol,
        satisfaction = sol_file.satisfaction,
        features = sol_file.features,
        candidatesFile_id = sol_file.candidatesFile_id,
    )
    record_id = await database.execute(query)

    query = selection_files.select().where(selection_files.c.id == record_id)
    row = await database.fetch_one(query)
    return {**row}


@router.post("/remove/{id}", status_code = status.HTTP_200_OK, dependencies=[Depends(JWTBearer())])
async def delete_selection_file(id:int, data:SelectionFileToDelete):

    query = users.select().where(users.c.id  == data.user_id)
    user = await database.fetch_one(query)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND_MESSAGE)
    if not pbkdf2_sha256.verify(data.user_pwd, user.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND_MESSAGE)

    query = selection_files.delete().where(selection_files.c.id == id)
    await database.execute(query)
    return {
        "removed": True,
        "message": "Operation deleted successfully"
    }



