from typing import List
from pydantic import BaseModel

from tables import Metric, OptimizeType


class EnumConstraintIn(BaseModel):
    value : str
    number : int
    metric : Metric
    feature_id : int

class OptEnumConstraintIn(BaseModel):
    value : str
    number : int
    metric : Metric
    feature_id : int
    weight : int
    optimize : OptimizeType

class EnumConstraint(BaseModel):
    id : int
    value : str
    number : int
    metric : Metric
    feature_id : int
    weight : int
    optimize : OptimizeType


class AllEnumConstraintIn(BaseModel):
    data : List[EnumConstraintIn]

class AllOptEnumConstraintIn(BaseModel):
    data : List[OptEnumConstraintIn]