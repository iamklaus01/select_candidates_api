from pydantic import BaseModel


class SolverStatIn(BaseModel):
    status : str
    solutions : int
    selectionFile_id : int

class SolverStat(BaseModel):
    id : int
    status : str
    solutions : int
    selectionFile_id : int