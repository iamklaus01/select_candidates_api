from ortools.sat.python import cp_model

class SolutionFormat(cp_model.CpSolverSolutionCallback):
    """Print intermediate solutions."""
    
    
    def __init__(self, datas, variables):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.__data = datas
        self.__variables = variables
        self.__solution_count = 0

    def on_solution_callback(self):
        one_list = []
        self.__solution_count += 1
        for v in self.__variables:
            if(self.Value(v) == 1):
                one_list.append(v.Index())
            #print('%s=%i' % (v, self.Value(v)), end=' ')
        # print("Liste n°%i de Candidats sélectionnés " % (self.__solution_count))
        # print(self.__data.iloc[one_list])
        # print()

    def solution_count(self):
        return self.__solution_count