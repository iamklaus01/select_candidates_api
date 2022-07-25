from pydantic import BaseModel

class CandidateFileIn(BaseModel):
    extension : str
    path : str
    user_id : int

class CandidateFile(BaseModel):
    id : int
    extension : str
    path : str
    user_id : int