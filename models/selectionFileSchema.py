from pydantic import BaseModel


class SelectionFileIn(BaseModel):
    base64File : str
    candidatesFile_id : int

class SelectionFile(BaseModel):
    id : int
    base64File : str
    candidatesFile_id : int