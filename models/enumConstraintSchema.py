from typing import List
from pydantic import BaseModel

from tables import Metric


class EnumConstraintIn(BaseModel):
    value : str
    number : int
    metric : Metric
    feature_id : int

class EnumConstraint(BaseModel):
    id : int
    value : str
    number : int
    metric : Metric
    feature_id : int


class AllEnumConstraintIn(BaseModel):
    data : List[EnumConstraintIn]