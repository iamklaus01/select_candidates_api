from pydantic import BaseModel

from tables import ValueType

class FeatureIn(BaseModel):
    label : str
    valueType : ValueType
    candidatesFile_id : int


class Feature(BaseModel):
    id : int
    label : str
    valueType : ValueType
    candidatesFile_id : int