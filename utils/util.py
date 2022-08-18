import enum
import pandas as pd

from datetime import datetime
from math import trunc
from models.featureSchema import Feature

from tables import users, candidates_files
from database import database


class FileType(enum.Enum):
    cFile = "CANDIDATE_FILE"
    sFile = "SOLUTION_FILE"


def read_file(path:str):
    if path.split('.')[1] == 'csv':
        return pd.read_csv(path)
    else:
        return pd.read_excel(path)

def rename_file(filename:str):
    name, ext = filename.split('.')
    ts = trunc(datetime.now().timestamp()*1000)

    return name+'_'+str(ts)+'.'+ext

def get_file_path(type:FileType, name:str):
    if type == FileType.cFile:
        return "files/candidates/"+name
    else:
        return "files/selected/"+name


def extract_features(path:str, n_col_to_ignore:int):
    data = read_file(path)
    return list(data.columns)[n_col_to_ignore:], get_features_type(data, n_col_to_ignore)

def get_features_type(data:pd.DataFrame, n:int):
    return list(data.dtypes[n:])

async def check_user(user_id : int):
    query = users.select().where(users.c.id  == user_id)
    user = await database.fetch_one(query)
    if not user:
        return False
    return True

async def add_int_constraint(feature:Feature):
    query = candidates_files.select().where(candidates_files.c.id == feature.candidatesFile_id)
    c_file = await database.fetch_one(query)
    data = read_file(c_file.path)
    values = list(data[feature.label])
    return {
        'min' : min(values),
        'max' : max(values),
        'feature_id' : feature.id
    }

async def add_enum_constraint(feature:Feature):
    query = candidates_files.select().where(candidates_files.c.id == feature.candidatesFile_id)
    c_file = await database.fetch_one(query)
    data = read_file(c_file.path)
    all_values = list(data[feature.label])
    repeated_values = list(set(all_values))
    value_with_count = []
    for val in repeated_values:
        n = all_values.count(val)
        value_with_count.append(
            {
                'value' : val,
                'number' : n
            }
        )
    return value_with_count