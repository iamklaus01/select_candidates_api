from fastapi import APIRouter, Depends
from typing import List
from database import database


from models.featureSchema import Feature
from tables import features
from token_dependencie import JWTBearer

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
    return single_feature
