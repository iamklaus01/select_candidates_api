from fastapi import APIRouter, Depends, status
from typing import List
from database import database


from models.selectionFileSchema import SelectionFile, SelectionFileIn
from tables import selection_files
from token_dependencie import JWTBearer



router = APIRouter()

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
        base64File = sol_file.base64File,
        candidatesFile_id = sol_file.candidatesFile_id,
    )
    record_id = await database.execute(query)

    query = selection_files.select().where(selection_files.c.id == record_id)
    row = await database.fetch_one(query)
    return {**row}


@router.delete("/remove", status_code = status.HTTP_200_OK, dependencies=[Depends(JWTBearer())])
async def delete_selection_file(id:int):
    query = selection_files.delete().where(selection_files.c.id == id)
    await database.execute(query)
    return {
        "removed": True,
        "message": "Opération effectuée avec succès"
    }



