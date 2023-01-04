from pydantic import BaseModel


class SelectionFileIn(BaseModel):
    encodedFile : str
    status : str
    n_sol : int
    satisfaction : int
    features : str
    candidatesFile_id : int

class SelectionFile(BaseModel):
    id : int
    encodedFile : str
    status : str
    nbre_sol : int
    satisfaction : int
    features: str
    candidatesFile_id : int

class SelectionFileToDelete(BaseModel):
    user_pwd : str
    user_id : int