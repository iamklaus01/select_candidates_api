from fastapi import APIRouter, Depends, status
from typing import List
from database import database


from models.integerConstraintSchema import IntegerConstraint, AllIntegerConstraintIn, IntegerConstraintIn
from tables import integer_constraints
from token_dependencie import JWTBearer



router = APIRouter()

@router.get("/iconstraints/", response_model=List[IntegerConstraint], dependencies=[Depends(JWTBearer())])
async def get_all_i_constraints(feature_id :int):
    query = integer_constraints.select().where(integer_constraints.c.feature_id  == feature_id)
    all_i_constraints = await database.fetch_all(query)
    return all_i_constraints

@router.get("/iconstraints/single", response_model=IntegerConstraint, dependencies=[Depends(JWTBearer())])
async def get_single_i_constraints(id:int):
    query = integer_constraints.select().where(integer_constraints.c.id  == id)
    single_constraint = await database.fetch_one(query)
    return {**single_constraint}


@router.post("/iconstraints/add", status_code=status.HTTP_201_CREATED, dependencies=[Depends(JWTBearer())])
async def add_integer_constraint(i_constraints : AllIntegerConstraintIn):

    for constraint in i_constraints.data:
        query = integer_constraints.insert().values(
            min_value = constraint.min_value,
            max_value = constraint.max_value,
            feature_id = constraint.feature_id
        )
        await database.execute(query)

    return {"message" : "Constraints added"}


@router.put("/iconstraints/update/{id}", response_model=IntegerConstraint, status_code=status.HTTP_200_OK, dependencies=[Depends(JWTBearer())])
async def update_i_constraint(id :int, i_constraint: IntegerConstraintIn):

    query = integer_constraints.update().where(integer_constraints.c.id == id).values(
        min_value = i_constraint.min_value,
        max_value = i_constraint.max_value,
        feature_id = i_constraint.feature_id
    )
    await database.execute(query)
    query = integer_constraints.select().where(integer_constraints.c.id  == id)
    single_constraint = await database.fetch_one(query)
    return {**single_constraint}


@router.delete("/iconstraints/remove", status_code = status.HTTP_200_OK, dependencies=[Depends(JWTBearer())])
async def delete_i_constraint(id:int):
    query = integer_constraints.delete().where(integer_constraints.c.id == id)
    await database.execute(query)
    return {
        "removed": True,
        "message": "Constraint removed successfully"
    }



