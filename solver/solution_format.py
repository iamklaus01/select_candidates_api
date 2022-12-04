import pandas as pd
from ortools.sat.python import cp_model


class SolutionFormat(cp_model.CpSolverSolutionCallback):
    """Print intermediate solutions."""
    
    
    def __init__(self, datas, variables, limit:int):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.__data = datas
        self.__variables = variables
        self.__all_solutions = []
        self.__solution_count = 0
        self.__solution_limit = limit

    def on_solution_callback(self):
        one_list = []
        self.__solution_count += 1
        for v in self.__variables:
            if(self.Value(v) == 1):
                one_list.append(v.Index())
            #print('%s=%i' % (v, self.Value(v)), end=' ')
        self.__all_solutions.append(pd.DataFrame(self.__data.iloc[one_list]))
        if self.__solution_limit > 0 and self.__solution_count >= self.__solution_limit:
            # print('Stop search after %i solutions' % self.__solution_limit)
            self.StopSearch()
        # print("Liste n°%i de Candidats sélectionnés " % (self.__solution_count))
        # print(self.__data.iloc[one_list])
        # print()

    def solution_count(self):
        return self.__solution_count

    def get_data(self):
        return self.__data

    def get_all_solutions(self):
        for i in range(len(self.__all_solutions)):
            self.__all_solutions[i] = self.__all_solutions[i].to_dict(orient = "records")
        return self.__all_solutions