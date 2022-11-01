import enum
from numpy import dtype
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


def extract_features(path:str):
    data = read_file(path)
    features = get_features_and_type(list(data.columns), list(data.dtypes))
    return features

def get_features_and_type(columns, types):
    features_types = {}
    for col, type in zip(columns, types):
        features_types[col] = ( "Enumeration", "Entier" ) [type == dtype('int64')]

    return features_types

async def check_user(user_id : int):
    query = users.select().where(users.c.id  == user_id)
    user = await database.fetch_one(query)
    if not user:
        return False
    return True

async def get_details_on_int_feature(feature:Feature):
    query = candidates_files.select().where(candidates_files.c.id == feature.candidatesFile_id)
    c_file = await database.fetch_one(query)
    data = read_file(c_file.path)
    values = list(data[feature.label])
    return {
        "label" : feature.label,
        'min' : min(values),
        'max' : max(values),
        'feature_id' : feature.id
    }

async def get_details_on_enum_feature(feature:Feature):
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
                'number' : n,
                'feature_id' : feature.id
            }
        )
    return {feature.label : value_with_count}