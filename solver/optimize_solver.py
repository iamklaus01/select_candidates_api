from typing import List
import pandas as pd
from models.featureSchema import Feature
from ortools.sat.python import cp_model


from database import database
from models.candidatesFileSchema import CandidateFile
from solver.solution_format import SolutionFormat
from tables import Metric, ValueType, integer_constraints, enum_constraints
from utils.util import read_file

async def get_constraint(feature_id : int, type : ValueType):
    if type == ValueType.number:
        query = integer_constraints.select().where(integer_constraints.c.feature_id == feature_id)
        constraint = await database.fetch_one(query)
    else : 
        query = enum_constraints.select().where(enum_constraints.c.feature_id == feature_id)
        constraint = await database.fetch_all(query)
        
    return constraint


async def solve(c_file : CandidateFile, int_features : List[Feature], enum_features : List[Feature], limit : int):

    datas = read_file(c_file.path)

    # Filtering datas with integer contraints define on integer types features
    datas_filtered = datas.copy(deep=True)
    has_to_solve = False

    for feature in int_features:
        int_constraint = await get_constraint(feature.id, ValueType.number)
        if int_constraint:
            has_to_solve = True
            datas_filtered = datas_filtered[ datas_filtered[feature.label] >= int_constraint.min_value ]
            datas_filtered = datas_filtered[ datas_filtered[feature.label] <= int_constraint.max_value ]

    datas_filtered.reset_index(inplace=True, drop=True)

    # For debugging
    # print("Liste de candidats après filtrage")
    # print(datas_filtered)

    #id_col_name = list(datas_filtered.columns)[0]
    #all_id = datas_filtered[id_col_name].tolist()
    all_id = list(datas_filtered.index)

    model = cp_model.CpModel()
    solver = cp_model.CpSolver()

    selected = []
    for i in range(len(all_id)):
        selected.append(model.NewIntVar(0,1,'Candidat%i' % i))
    
    # Adding each enum constraint
    for feature in enum_features:
        feature_all_values = datas_filtered[feature.label].tolist()
        repeated_values = list(set(feature_all_values))

        # Change enumerations values to integer for a better manipulation
        for i in range(len(feature_all_values)):
            feature_all_values[i] = repeated_values.index(feature_all_values[i]) + 1

        # For each feature value on which constraints has been addded, add this constraint
        enum_c = await get_constraint(feature.id, ValueType.multiple)
        if enum_c:
            has_to_solve = True
            for single_enum_c in enum_c:
                if(single_enum_c.value in repeated_values):
                    corresponding_int = repeated_values.index(single_enum_c.value) + 1
                    s = sum([ selected[i]*feature_all_values[i] for i in range(len(all_id)) if feature_all_values[i]== corresponding_int ])

                    # Adding properly constraint depending of the metric
                    number = corresponding_int * single_enum_c.number

                    if(Metric[single_enum_c.metric] == Metric.lessThan):
                        model.Add(s <= number)
                    elif(Metric[single_enum_c.metric] == Metric.moreThan):
                        model.Add(s >= number)
                    else:
                        model.Add(s == number)

    # Proceed to the resolution
    solution_printer = SolutionFormat(datas_filtered, selected, limit)

    #Enumerate all solutions.
    solver.parameters.enumerate_all_solutions = True

    # Solving properly
    if(has_to_solve):
        status = solver.Solve(model, solution_printer)
        number_of_solutions = solution_printer.solution_count()

        print('Status = %s' % solver.StatusName(status))
        print('Number of solutions found: %i' % number_of_solutions)
        all_solutions = solution_printer.get_all_solutions()
        

        return {
            'status' : solver.StatusName(status),
            'number_of_solutions' : number_of_solutions,
            'columns' : list(datas_filtered.columns),
            'solutions' : all_solutions
        }
    else:
         return {
            'status' : "NOTHING TO SOLVE",
            'number_of_solutions' : 0,
            'columns' : list(datas_filtered.columns),
            'solutions' : []
        }