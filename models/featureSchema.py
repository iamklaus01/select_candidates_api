from typing import List
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

class FeatureSaveIn(BaseModel):
    name : str
    type : str

class AllFeatureIn(BaseModel):
    features : List[FeatureSaveIn]
    c_file_id : int
