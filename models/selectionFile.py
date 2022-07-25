from pydantic import BaseModel


class SelectionFileIn(BaseModel):
    path : str
    candidatesFile_id : int

class SelectionFile(BaseModel):
    id : int
    path : str
    candidatesFile_id : int