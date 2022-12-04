from operator import and_
from fastapi import APIRouter, Depends, HTTPException, status, Form
from typing import List
from database import database


from models.featureSchema import Feature
from tables import ValueType, features
from token_dependencie import JWTBearer
from utils.util import get_details_on_int_feature, get_details_on_enum_feature


router = APIRouter()


@router.get("/features/int/{cd_file_id}", response_model=List[Feature], dependencies=[Depends(JWTBearer())])
async def get_file_enum_features(cd_file_id :int):
    query = features.select().where(and_(features.c.candidatesFile_id  == cd_file_id, features.c.valueType == ValueType.number))
    all_int_features = await database.fetch_all(query)
    return all_int_features

@router.get("/features/enum/{cd_file_id}", response_model=List[Feature], dependencies=[Depends(JWTBearer())])
async def get_file_enum_features(cd_file_id :int):
    query = features.select().where(and_(features.c.candidatesFile_id  == cd_file_id, features.c.valueType == ValueType.multiple))
    all_enum_features = await database.fetch_all(query)
    return all_enum_features

@router.get("/features/single", response_model=Feature, dependencies=[Depends(JWTBearer())])
async def get_single_file_feature(id:int):
    query = features.select().where(features.c.id == id)
    single_feature = await database.fetch_one(query)
    if not single_feature:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feature not found or not taken into account.")
    return single_feature


@router.get("/features/int/details/{cd_file_id}", dependencies=[Depends(JWTBearer())])
async def get_details_int_features(cd_file_id :int):
    query = features.select().where(and_(features.c.candidatesFile_id  == cd_file_id, features.c.valueType == ValueType.number))
    all_int_features = await database.fetch_all(query)

    if not all_int_features:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Features not found or not taken into account.")

    details = []
    for feature in all_int_features:
        details.append(await get_details_on_int_feature(feature))
    
    return details

@router.get("/features/enum/details/{cd_file_id}", dependencies=[Depends(JWTBearer())])
async def get_details_enum_features(cd_file_id :int):
    query = features.select().where(and_(features.c.candidatesFile_id  == cd_file_id, features.c.valueType == ValueType.multiple))
    all_int_features = await database.fetch_all(query)

    if not all_int_features:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Features not found or not taken into account.")

    details = []
    for feature in all_int_features:
        details.append(await get_details_on_enum_feature(feature))
    
    return details
