import enum
import pandas as pd

from datetime import datetime
from math import trunc


class FileType(enum.Enum):
    cFile = "CANDIDATE_FILE"
    sFile = "SOLUTION_FILE"


def rename_file(filename:str):
    name, ext = filename.split('.')
    ts = trunc(datetime.now().timestamp()*1000)

    return name+'_'+str(ts)+'.'+ext

def get_file_path(type:FileType, name:str):
    if type == FileType.cFile:
        return "files/candidates/"+name
    else:
        return "files/selected/"+name


def extract_features(path:str):
    data = pd.read_csv(path)
    return list(data.columns), get_features_type(data)

def get_features_type(data:pd.DataFrame):
    return list(data.dtypes)

