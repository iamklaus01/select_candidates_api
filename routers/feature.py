from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from database import database


from models.featureSchema import Feature
from tables import ValueType, features
from token_dependencie import JWTBearer
from utils.util import add_int_constraint, add_enum_constraint


router = APIRouter()

@router.get("/features", response_model=List[Feature], dependencies=[Depends(JWTBearer())])
async def get_file_features(cd_file_id :int):
    query = features.select().where(features.c.candidatesFile_id  == cd_file_id)
    all_features = await database.fetch_all(query)
    return all_features

@router.get("/features/single", response_model=Feature, dependencies=[Depends(JWTBearer())])
async def get_single_file_feature(id:int):
    query = features.select().where(features.c.id == id)
    single_feature = await database.fetch_one(query)
    if not single_feature:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Caractéristique introuvable ou non prise en compte.")
    return single_feature

@router.get("/features/add/constraints", dependencies=[Depends(JWTBearer())])
async def get_details_on_feature_values(feature_id:int):
    query = features.select().where(features.c.id == feature_id)
    single_feature = await database.fetch_one(query)
    if not single_feature:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Caractéristique introuvable ou non prise en compte.")

    if ValueType[single_feature.valueType] == ValueType.integer:
        return await add_int_constraint(single_feature)
    else:
        return await add_enum_constraint(single_feature)

