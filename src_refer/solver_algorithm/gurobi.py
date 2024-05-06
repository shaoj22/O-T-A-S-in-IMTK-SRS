'''
File: gurobi.py
Project: Joint_Optimization_of_Orders_and_Totes_for_WayZim.
Description:
-----------
use gurobi to get the solution of the problem.
-----------
Author: 626
Created Date: 2023-1109
'''


import sys
sys.path.append('..')
from Joint_Optimization_of_Orders_and_Totes_for_WayZim.src.instance.input_data import read_input_data
import gurobipy as gp
import time
from gurobipy import GRB


class IntegratedGurobi:
    def __init__(self, instance, time_limit=None, init_solution=None, max_T=100):
        self.instance = instance
        self.time_limit = time_limit
        self.init_solution = init_solution
        # set
        self.I = self.instance.tote_num
        self.O = self.instance.order_num
        self.P = self.instance.station_num
        self.to_matrix = self.instance.to_matrix
        self.buffer = self.instance.station_buffer_num # station buffer num
        self.T = max_T # max t set 
        self.bigM = 100 # big M
        self.time_matrix = self.gen_time_matrix()

    def gen_time_matrix(self):
        """ generate the time matrix """
        time_matrix = [[0 for t1 in range(self.T)] for t2 in range(self.T)]
        for t1 in range(self.T):
            for t2 in range(self.T):
                if t1 > t2:
                    time_matrix[t1][t2] = 1
        return time_matrix   

    def set_time_limit(self, Model):
        """ set the time limit for gurobi model """

    def set_init_solution(self, Model):
        """ use greedy or other algorithm to set the init solution for gurobi model """
        
        pass

    def build_gurobi_model(self, Model):
        """ set the obj and the constraint for the gurobi model """
        # set the variable
        x_list = [(i,p,t) for i in range(self.I) for p in range(self.P) for t in range(self.T)]
        x = Model.addVars(x_list, vtype=GRB.BINARY, name="x")
        y_list = [(o,p,t) for o in range(self.O) for p in range(self.P) for t in range(self.T)]
        y = Model.addVars(y_list, vtype=GRB.BINARY, name="y")
        z_list = [(i,o,p,t) for i in range(self.I) for o in range(self.O) for p in range(self.P) for t in range(self.T)]
        z = Model.addVars(z_list, vtype=GRB.BINARY, name="z")
        # a_list = [(i,t) for i in range(self.I) for t in range(self.T)]
        # a = Model.addVars(a_list, vtype=GRB.BINARY, name="a")
        b_list = [(o,p) for o in range(self.O) for p in range(self.P)]
        b = Model.addVars(b_list, vtype=GRB.BINARY, name="b")
        # set the obj
        Model.modelSense = GRB.MINIMIZE
        Model.setObjective(gp.quicksum(x[i,p,t] for i in range(self.I) for p in range(self.P) for t in range(self.T))) 
        # set the constraints
        # 约束1：每个拣选单的料箱都需要完成约束。
        Model.addConstrs(gp.quicksum(z[i,o,p,t] for p in range(self.P) for t in range(self.T)) == self.to_matrix[i][o] for i in range(self.I) for o in range(self.O))
        # 约束2：每个工作站每个时间执行的拣选单数量上限约束。
        Model.addConstrs(gp.quicksum(y[o,p,t] for o in range(self.O)) <= self.buffer for p in range(self.P) for t in range(self.T))
        # 约束3：每个顺序时刻每个工作站到达的料箱数量上限约束：
        Model.addConstrs(gp.quicksum(x[i,p,t] for i in range(self.I)) <= 1 for p in range(self.P) for t in range(self.T))
        # 约束4：每个拣选单都需要完成：
        Model.addConstrs(gp.quicksum(y[o,p,t] for t in range(self.T) for p in range(self.P)) == gp.quicksum(self.to_matrix[i][o] for i in range(self.I)) for o in range(self.O))
        # 约束5：每个拣选单是否完成约束：
        Model.addConstrs(x[i,p,t] + y[o,p,t] - 1 <= z[i,o,p,t] for i in range(self.I) for o in range(self.O) for p in range(self.P) for t in range(self.T))
        Model.addConstrs(z[i,o,p,t] <= x[i,p,t] for i in range(self.I) for o in range(self.O) for p in range(self.P) for t in range(self.T))
        Model.addConstrs(gp.quicksum(z[i,o,p,t] for i in range(self.I)) <= y[o,p,t] for o in range(self.O) for p in range(self.P) for t in range(self.T))
        # 约束6：每个拣选单只能在一个工作站完成约束：
        Model.addConstrs(b[o,p] >= y[o,p,t] for o in range(self.O) for p in range(self.P) for t in range(self.T))
        Model.addConstrs(gp.quicksum(b[o,p] for p in range(self.P)) == 1 for o in range(self.O))
        # 约束7：每个拣选单在工作站上执行的时间必须连续约束：
        Model.addConstrs(y[o,p,t2] >= y[o,p,t1] + y[o,p,t3] + self.time_matrix[t2][t1] + self.time_matrix[t3][t2] - 3 for t1 in range(self.T) for t2 in range(self.T) for t3 in range(self.T) for o in range(self.O) for p in range(self.P))
        # 约束8：工作站平衡约束：
        Model.addConstrs((gp.quicksum(x[i,p1,t] for i in range(self.I) for t in range(self.T)) - gp.quicksum(x[i,p2,t] for i in range(self.I) for t in range(self.T))) <= 3 for p1 in range(self.P) for p2 in range(self.P))


        Model.update()
        result_info = {
            'x': x,
            'y': y,
            'z': z,
        }
        return result_info
    
    def run_gurobi_model(self):
        Model = gp.Model('IntegratedGurobiModel')
        self.build_gurobi_model(Model=Model)
        if self.time_limit is not None:
            Model.setParam('TimeLimit', self.time_limit)
        start_Time = time.time()
        Model.optimize()
        end_Time = time.time()
        # get the variable's value
        result_info = {}
        # get x
        info_x = []
        for i in range(self.I):
            x_i = []
            for p in range(self.P):
                x_i_p = []   
                for t in range(self.T):
                    var_name_x = f"x[{i},{p},{t}]"
                    x_i_p_t = Model.getVarByName(var_name_x).X
                    x_i_p.append(x_i_p_t)
                x_i.append(x_i_p)
            info_x.append(x_i)
        result_info['info_x'] = info_x
        # get y
        info_y = []
        for o in range(self.O):
            y_o = []
            for p in range(self.P):
                y_o_p = []   
                for t in range(self.T):
                    var_name_y = f"y[{o},{p},{t}]"
                    y_o_p_t = Model.getVarByName(var_name_y).X
                    y_o_p.append(y_o_p_t)
                y_o.append(y_o_p)
            info_y.append(y_o)
        result_info['info_y'] = info_y

        upper_bound = Model.objVal
        lower_bound = Model.objBound
        MIPGap = Model.MIPGap
        CPU_Time = end_Time - start_Time
        result_info['upper_bound'] = upper_bound
        result_info['lower_bound'] = lower_bound
        result_info['MIPGap'] = MIPGap
        result_info['CPU_time'] = CPU_Time

        return result_info

if __name__ == "__main__":
    input_path = "D:\\Desktop\\python_code\\Joint_Optimization_of_Orders_and_Totes_for_WayZim\\src\\instance\\myRandomInstanceGurobi.json"
    instance_obj = read_input_data(input_path)
    gurobi_alg = IntegratedGurobi(instance=instance_obj, time_limit=3600, max_T=10)
    result_info = gurobi_alg.run_gurobi_model()







