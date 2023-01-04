from typing import List
from pydantic import BaseModel

from tables import OptimizeType


class IntegerConstraintIn(BaseModel):
    min_value : int
    max_value : int
    feature_id : int

class OptIntegerConstraintIn(BaseModel):
    min_value : int
    max_value : int
    feature_id : int
    coefficient : float
    optimize : OptimizeType

class IntegerConstraint(BaseModel):
    id : int
    min_value : int
    max_value : int
    feature_id : int
    coefficient : float
    optimize : OptimizeType

class AllIntegerConstraintIn(BaseModel):
    data : List[IntegerConstraintIn]

class AllOptIntegerConstraintIn(BaseModel):
    data : List[OptIntegerConstraintIn]