from pydantic import BaseModel


class IntegerConstraintIn(BaseModel):
    min_value : int
    max_value : int
    feature_id : int

class IntegerConstraint(BaseModel):
    id : int
    min_value : int
    max_value : int
    feature_id : int