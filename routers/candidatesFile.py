from operator import and_
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from os import getcwd, remove
from typing import List
from sqlalchemy import select

from database import database
import shutil
from passlib.hash import pbkdf2_sha256


from tables import Role, ValueType, candidates_files, features, users, integer_constraints, enum_constraints
from token_dependencie import JWTBearer
from solver.solver import solve
from models.candidatesFileSchema import CandidateFile, CandidateFileToDelete
from models.featureSchema import AllFeatureIn
from utils.util import check_user, rename_file, get_file_path, extract_features, FileType, format_int_constraints, format_enum_constraints, format_feature_label_id

FILE_NOT_FOUND_MESSAGE = "File not found! Make sure you have the correct ID"
USER_NOT_FOUND_MESSAGE = "User not found! The email address or username is incorrect"

router = APIRouter()

@router.get("/", response_model=List[CandidateFile], dependencies=[Depends(JWTBearer())])
async def get_candidates_files(user_id :int):

    query = users.select().where(users.c.id  == user_id)
    user = await database.fetch_one(query)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if Role[user.role] != Role.admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authorized for such an operation")
    query = candidates_files.select()
    all_files = await database.fetch_all(query)
    return all_files

@router.get("/user", response_model=List[CandidateFile], dependencies=[Depends(JWTBearer())])
async def get_users_candidates_files(user_id:int):

    if not await check_user(user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

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

@router.get("/get_constraints/{c_file_id}", status_code=status.HTTP_200_OK, dependencies=[Depends(JWTBearer())])
async def get_all_constraints(c_file_id : int):
    query = features.select().where(features.c.candidatesFile_id == c_file_id)
    all_features = await database.fetch_all(query)
    int_features_id = []
    enum_features_id = []
    for feature in all_features:
        if(ValueType[feature.valueType] == ValueType.number):
            int_features_id.append(feature.id)
        else:
            enum_features_id.append(feature.id)
    query = select(integer_constraints).where(integer_constraints.c.feature_id.in_(int_features_id)).join(features, integer_constraints.c.feature_id == features.c.id)
    iconstraints = await database.fetch_all(query)   

    query = select(enum_constraints).where(enum_constraints.c.feature_id.in_(enum_features_id)).join(features, enum_constraints.c.feature_id == features.c.id)
    econstraints = await database.fetch_all(query)   
    f_id = format_feature_label_id(all_features)
    return{
        'iconstraints' : format_int_constraints(iconstraints, f_id),
        'econstraints' : format_enum_constraints(econstraints, f_id)
    }

@router.post("/add/{user_id}", status_code=status.HTTP_201_CREATED, dependencies=[Depends(JWTBearer())])
async def store_candidates_files(user_id:int ,c_file:UploadFile = File(...)):
    if not await check_user(user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found. You should have an account to use our services.")

    c_file.filename = rename_file(c_file.filename)
    with open(f'files/candidates/{c_file.filename}', "wb") as buffer:
        shutil.copyfileobj(c_file.file, buffer)

    file_path = get_file_path(FileType.cFile, c_file.filename)
    query = candidates_files.insert().values(
    extension = c_file.filename.split(".")[1],
    path = file_path,
    user_id = user_id
    )
    record_id = await database.execute(query)
    if(record_id):
        c_file_features = extract_features(file_path)
        return {"c_file_id" : record_id, "data": c_file_features}

    return {"c_file_id" : -1, "data": None}

@router.post("/add_features/{user_id}", status_code=status.HTTP_201_CREATED, dependencies=[Depends(JWTBearer())])
async def store_candidates_file_feature(user_id:int , data:AllFeatureIn):
    if not await check_user(user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found. You should have an account to use our services.")
    for feature in data.features:
        query = features.insert().values(
            label = feature.name,
            valueType = ( ValueType.multiple, ValueType.number ) [feature.type == "Number"],
            candidatesFile_id = data.c_file_id
        )
        await database.execute(query)

    
    return {"message" : "Features have been saved successfully"}


@router.post("/remove/{id}", status_code = status.HTTP_200_OK, dependencies=[Depends(JWTBearer())])
async def delete_candidates_file(id:int, data:CandidateFileToDelete):

    query = users.select().where(users.c.id  == data.user_id)
    user = await database.fetch_one(query)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND_MESSAGE)
    if not pbkdf2_sha256.verify(data.user_pwd, user.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND_MESSAGE)

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
            "message" : "The file and its corresponding data have been successfully deleted"
        }   
    except FileNotFoundError:
        return {
            "removed": False,
            "message": "An error occurred while deleting the file"
        }


@router.get("/solve/{file_id}/{limit}", dependencies=[Depends(JWTBearer())])
async def resolve(file_id : int, limit: int):
    query = candidates_files.select().where(candidates_files.c.id == file_id)
    candidate_file = await database.fetch_one(query)
    if not candidate_file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=FILE_NOT_FOUND_MESSAGE)

    query = features.select().where(and_(features.c.candidatesFile_id  == file_id, features.c.valueType == ValueType.number))
    all_int_features = await database.fetch_all(query)

    query = features.select().where(and_(features.c.candidatesFile_id  == file_id, features.c.valueType == ValueType.multiple))
    all_enum_features = await database.fetch_all(query)


    return await solve(candidate_file, all_int_features, all_enum_features, limit)


# from starlette.responses import FileResponse

# return FileResponse(file_location, media_type='application/octet-stream',filename=file_name)