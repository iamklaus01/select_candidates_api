from pydantic import BaseModel


class SelectionFileIn(BaseModel):
    base64File : str
    status : str
    n_sol : int
    satisfaction : int
    candidatesFile_id : int

class SelectionFile(BaseModel):
    id : int
    base64File : str
    status : str
    n_sol : int
    satisfaction : int
    candidatesFile_id : int