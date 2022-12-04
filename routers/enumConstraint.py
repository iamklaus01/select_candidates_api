from fastapi import APIRouter, Depends, status
from typing import List
from database import database

from models.enumConstraintSchema import EnumConstraint, EnumConstraintIn, AllEnumConstraintIn
from tables import enum_constraints
from token_dependencie import JWTBearer



router = APIRouter()

@router.get("/econstraints", response_model=List[EnumConstraint], dependencies=[Depends(JWTBearer())])
async def get_all_e_constraints(feature_id :int):
    query = enum_constraints.select().where(enum_constraints.c.feature_id  == feature_id)
    all_e_constraints = await database.fetch_all(query)
    return all_e_constraints

@router.get("/econstraints/single", response_model=EnumConstraint, dependencies=[Depends(JWTBearer())])
async def get_single_i_constraints(id:int):
    query = enum_constraints.select().where(enum_constraints.c.id  == id)
    single_constraint = await database.fetch_one(query)
    return {**single_constraint}


@router.post("/econstraints/add", status_code=status.HTTP_201_CREATED, dependencies=[Depends(JWTBearer())])
async def add_enum_constraint(e_constraints : AllEnumConstraintIn):

    for constraint in e_constraints.data:
        query = enum_constraints.insert().values(
            value  = constraint.value,
            number  = constraint.number,
            metric  = constraint.metric,
            feature_id = constraint.feature_id
        )
        await database.execute(query)

    return {"message" : "Constraints Created"}


@router.put("/econstraints/update/{id}", response_model=EnumConstraint, status_code=status.HTTP_200_OK, dependencies=[Depends(JWTBearer())])
async def update_e_constraint(id:int, e_constraint: EnumConstraintIn):

    query = enum_constraints.update().where(enum_constraints.c.id == id).values(
        value  = e_constraint.value,
        number  = e_constraint.number,
        metric  = e_constraint.metric,
        feature_id = e_constraint.feature_id
    )
    await database.execute(query)
    query = enum_constraints.select().where(enum_constraints.c.id  == id)
    single_constraint = await database.fetch_one(query)
    return {**single_constraint}


@router.delete("/econstraints/remove", status_code = status.HTTP_200_OK, dependencies=[Depends(JWTBearer())])
async def delete_e_constraint(id:int):
    query = enum_constraints.delete().where(enum_constraints.c.id == id)
    await database.execute(query)
    return {
        "removed": True,
        "message": "Constraint removed successfully"
    }



