import gurobipy as gp
import time
from gurobipy import GRB
from src.Instance.input_data import read_input_data
# from src.Instance.input_data import read_input_data_initial
import json


class IntegratedGurobi:
    def __init__(self, instance, time_limit=None, init_solution=None, max_T=100, sita=3):
        self.instance = instance
        self.time_limit = time_limit
        self.init_solution = init_solution
        # set
        self.I = self.instance.tote_num
        self.O = self.instance.order_num
        self.P = self.instance.station_num
        self.B = self.instance.block_num
        self.to_matrix_oi = self.instance.to_matrix_oi
        self.to_matrix_ib = self.instance.to_matrix_ib
        self.C = self.instance.station_buffer_num # 拣选站同时处理订单最大数
        # self.C = 1 # 拣选站同时处理订单最大数
        self.K = self.instance.block_storage_num# 暂存区的最大储位
        # self.K = 1# 暂存区的最大储位
        self.T = max_T # max t set
        self.sita = sita
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
        op_list = [(o, p) for o in range(self.O) for p in range(self.P)]
        x_op = Model.addVars(op_list, vtype=GRB.BINARY, name="x_op")
        itb_list = [(i, t, b) for i in range(self.I) for t in range(self.T) for b in range(self.B)]
        x_itb_1 = Model.addVars(itb_list, vtype=GRB.BINARY, name="x_itb_1")
        it_list = [(i, t) for i in range(self.I) for t in range(self.T)]
        x_it_2 = Model.addVars(it_list, vtype=GRB.BINARY, name="x_it_2")
        itp_list = [(i, t, p) for i in range(self.I) for t in range(self.T) for p in range(self.P)]
        x_itp_2 = Model.addVars(itp_list, vtype=GRB.BINARY, name="x_itp_2")
        x_it_3 = Model.addVars(it_list, vtype=GRB.BINARY, name="x_it_3")
        x_itb_4 = Model.addVars(itb_list, vtype=GRB.BINARY, name="x_itb_4")
        y_it_2 = Model.addVars(it_list, vtype=GRB.BINARY, name="y_it_2")
        y_itb_2 = Model.addVars(itb_list, vtype=GRB.BINARY, name="y_itb_2")
        y_it_3 = Model.addVars(it_list, vtype=GRB.BINARY, name="y_it_3")
        y_it_4 = Model.addVars(it_list, vtype=GRB.BINARY, name="y_it_4")
        oitp_list = [(o, i, t, p) for o in range(self.O) for i in range(self.I) for t in range(self.T) for p in range(self.P)]
        z_oit_p = Model.addVars(oitp_list, vtype=GRB.BINARY, name="z_oit_p")
        otp_list = [(o, t, p) for o in range(self.O) for t in range(self.T) for p in range(self.P)]
        z_ot_p = Model.addVars(otp_list, vtype=GRB.BINARY, name="z_ot_p")
        # set the obj
        Model.modelSense = GRB.MINIMIZE
        sum1 = gp.quicksum(x_itb_1[i, t, b] for i in range(self.I) for t in range(self.T) for b in range(self.B))
        sum2 = gp.quicksum(x_itb_4[i, t, b] for i in range(self.I) for t in range(self.T) for b in range(self.B))
        sum3 = gp.quicksum(x_it_2[i, t] for i in range(self.I) for t in range(self.T))
        sum4 = gp.quicksum(x_it_3[i, t] for i in range(self.I) for t in range(self.T))
        Model.setObjective(sum1 + sum2 + sum3 + sum4)
        # set the constraints
        # 约束1：每个订单的料箱都需要完成
        Model.addConstrs(gp.quicksum(z_oit_p[o, i, t, p] for p in range(self.P) for t in range(self.T)) == self.to_matrix_oi[o][i] for o in range(self.O) for i in range(self.I))
        # 约束2：每个工作站每个时刻同时执行的订单数量上限
        Model.addConstrs(gp.quicksum(z_ot_p[o, t, p] for o in range(self.O)) <= self.C for p in range(self.P) for t in range(self.T))
        # 约束3：每个订单都需要完成
        Model.addConstrs(x_itp_2[i, t, p] + z_ot_p[o, t, p] + self.to_matrix_oi[o][i] - 2 <= z_oit_p[o, i, t, p] for o in range(self.O) for i in range(self.I) for t in range(self.T) for p in range(self.P))
        Model.addConstrs(z_oit_p[o, i, t, p] <= x_itp_2[i, t, p] for o in range(self.O) for i in range(self.I) for t in range(self.T) for p in range(self.P))
        Model.addConstrs(gp.quicksum(z_oit_p[o, i, t, p] for i in range(self.I)) <= z_ot_p[o, t, p] for o in range(self.O) for t in range(self.T) for p in range(self.P))
        # 约束4：每个订单只能在一个拣选站完成
        Model.addConstrs(gp.quicksum(x_op[o, p] for p in range(self.P)) == 1 for o in range(self.O))
        Model.addConstrs(x_op[o, p] >= z_ot_p[o, t, p] for o in range(self.O) for t in range(self.T) for p in range(self.P))
        # 约束5：每个订单在拣选站上执行的时间必须连续
        Model.addConstrs(z_ot_p[o, t2, p] >= z_ot_p[o, t1, p] + z_ot_p[o, t3, p] + self.time_matrix[t2][t1] + self.time_matrix[t3][t2] - 3 for t1 in range(self.T) for t2 in range(self.T) for t3 in range(self.T) for o in range(self.O) for p in range(self.P))
        # 约束6：工作站平衡约束
        Model.addConstrs(gp.quicksum(x_itp_2[i, t, p1] for i in range(self.I) for t in range(self.T)) - gp.quicksum(x_itp_2[i, t, p2] for i in range(self.I) for t in range(self.T)) <= self.sita for p1 in range(self.P) for p2 in range(self.P))
        # 下架决策有关约束
        # 约束1：每个时刻下，每个Block中只能下架一个料箱
        Model.addConstrs(gp.quicksum(x_itb_1[i, t, b] for i in range(self.I)) <= 1 for t in range(self.T) for b in range(self.B))
        # 约束2：当料箱在架上时才能下架，下架后在暂存区（回库以后也在存储区）
        # Model.addConstrs(y_it_4[i, t+1] + y_it_2[i, t+2] <= y_it_4[i, t] + gp.quicksum(x_itb_4[i, t, b] for b in range(self.B)) for i in range(self.I) for t in range(self.T - 2))
        Model.addConstrs(x_itb_1[i, t, b] <= y_it_4[i, t] for i in range(self.I) for t in range(self.T) for b in range(self.B))
        Model.addConstrs(y_it_4[i, t+1] <= 1 - gp.quicksum(x_itb_1[i, t, b] for b in range(self.B)) for i in range(self.I) for t in range(self.T - 1))
        # Model.addConstrs(y_it_2[i, t+1] + y_it_3[i, t+2] + y_it_4[i, t+2] <= y_it_2[i, t] + gp.quicksum(x_itb_1[i, t, b] for b in range(self.B)) + x_it_3[i, t] for i in range(self.I) for t in range(self.T - 2))
        Model.addConstrs(y_it_2[i, t+1] <= y_it_2[i, t] + gp.quicksum(x_itb_1[i, t, b] for b in range(self.B)) + x_it_3[i, t] for i in range(self.I) for t in range(self.T - 1))
        # 约束3：料箱在Block b中才能下架
        Model.addConstrs(x_itb_1[i, t, b] <= self.to_matrix_ib[i][b] for i in range(self.I) for t in range(self.T) for b in range(self.B))
        # 出库决策有关约束：
        # 约束1：每个时刻下，只能有一个料箱出库
        Model.addConstrs(gp.quicksum(x_it_2[i, t] for i in range(self.I)) <= 1 for t in range(self.T))
        # 约束2：每次出库的料箱可以去多个拣选站
        Model.addConstrs(x_itp_2[i, t, p] <= x_it_2[i, t] for i in range(self.I) for t in range(self.T) for p in range(self.P))
        # 约束3：当拣选站上的订单需要料箱i时，该料箱才会去到该拣选站
        Model.addConstrs(x_itp_2[i, t, p] <= gp.quicksum(self.to_matrix_oi[o][i] * z_ot_p[o, t, p] for o in range(self.O)) for i in range(self.I) for t in range(self.T) for p in range(self.P))
        # 约束4：料箱在暂存区时才能出库
        Model.addConstrs(x_it_2[i, t] <= y_it_2[i, t] for i in range(self.I) for t in range(self.T))
        # 约束5：料箱出库后，料箱在拣选站
        # Model.addConstrs(y_it_3[i, t+1] + y_it_2[i, t+2] <= y_it_3[i, t] + x_it_2[i, t] for i in range(self.I) for t in range(self.T - 2))
        Model.addConstrs(y_it_3[i, t+1] <= y_it_3[i, t] + x_it_2[i, t] for i in range(self.I) for t in range(self.T - 1))
        # 约束6：出库后，料箱不在暂存区：
        Model.addConstrs(y_it_2[i, t+1] <= 1 - x_it_2[i, t] for i in range(self.I) for t in range(self.T - 1))
        # 入库决策有关约束
        # 约束1：入库的顺序时刻为出库顺序时刻+访问的拣选站的数量
        Model.addConstrs(t2 - t1 - gp.quicksum(x_itp_2[i, t1, p] for p in range(self.P)) >= self.bigM * (x_it_3[i, t2] + x_it_2[i, t1] - 2) for i in range(self.I) for t1 in range(self.T) for t2 in range(t1, self.T))
        # Model.addConstrs(t2 - t1 - gp.quicksum(x_itp_2[i, t1, p] for p in range(self.P)) >= self.bigM * (x_it_3[i, t2] + x_it_2[i, t1] - 2) for i in range(self.I) for t1 in range(self.T-3) for t2 in range(t1, t1+3))
        # 约束2：料鲜在拣选站才能出库
        Model.addConstrs(x_it_3[i, t] <= y_it_3[i, t] for i in range(self.I) for t in range(self.T))
        # 入库后，料箱存储在暂存区，不在拣选站
        Model.addConstrs(y_it_3[i, t + 1] <= 1 - x_it_3[i, t] for i in range(self.I) for t in range(self.T - 1))
        # 上架决策有关约束
        # 约束1：是否上架
        Model.addConstrs(x_itb_4[i, t, b] <= y_it_2[i, t] for i in range(self.I) for t in range(self.T) for b in range(self.B))
        # 约束2：每个时刻下，每个Block中只能上架一个料箱
        Model.addConstrs(
            gp.quicksum(x_itb_4[i, t, b] for i in range(self.I)) <= 1 for t in range(self.T) for b in range(self.B))
        # 约束3：料箱i属于Block B才能上架和暂存
        Model.addConstrs(x_itb_4[i, t, b] <= self.to_matrix_ib[i][b] for i in range(self.I) for t in range(self.T) for b in range(self.B))
        # 约束4：同一时间在暂存区的料箱数量有限
        Model.addConstrs(gp.quicksum(y_itb_2[i, t, b] for b in range(self.B)) == y_it_2[i, t] for i in range(self.I) for t in range(self.T))
        Model.addConstrs(gp.quicksum(y_itb_2[i, t, b] for i in range(self.I)) <= self.K for t in range(self.T) for b in range(self.B))
        Model.addConstrs(y_itb_2[i, t, b] <= self.to_matrix_ib[i][b] for i in range(self.I) for t in range(self.T) for b in range(self.B))
        # 约束5：料箱上架后，料箱在架上，不在暂存区
        Model.addConstrs(y_it_2[i, t + 1] <= 1 - gp.quicksum(x_itb_4[i, t, b] for b in range(self.B)) for i in range(self.I) for t in range(self.T - 1))
        Model.addConstrs(y_it_4[i, t+1] <= y_it_4[i, t] + gp.quicksum(x_itb_4[i, t, b] for b in range(self.B)) for i in range(self.I) for t in range(self.T - 1))
        # 状态约束
        # 约束1：初始状态下，料箱都在货架上
        Model.addConstrs(y_it_4[i, 0] == 1 for i in range(self.I))
        # 约束2：结束时，料箱都在货架上
        Model.addConstrs(y_it_4[i, self.T-1] == 1 for i in range(self.I))
        # 约束3：同一时刻，料箱只处于一种状态
        Model.addConstrs(y_it_2[i, t] + y_it_3[i, t] + y_it_4[i, t] == 1 for i in range(self.I) for t in range(self.T))
        # 约束4：同一时刻，料箱中最多有一种动作
        Model.addConstrs(gp.quicksum(x_itb_1[i, t, b] for b in range(self.B)) + x_it_2[i, t] + x_it_3[i, t] + gp.quicksum(x_itb_4[i, t, b] for b in range(self.B)) <= 1 for i in range(self.I) for t in range(self.T))
        # Model.optimize()
        Model.update()

        # 设置初始解
        for o, p in op_list:
            x_op[o, p].start = self.init_solution['x_op'][o][p]

        for i, t, b in itb_list:
            x_itb_1[i, t, b].start = self.init_solution['x_itb_1'][i][t][b]

        for i, t in it_list:
            x_it_2[i, t].start = self.init_solution['x_it_2'][i][t]

        for i, t, p in itp_list:
            x_itp_2[i, t, p].start = self.init_solution['x_itp_2'][i][t][p]

        for i, t in it_list:
            x_it_3[i, t].start = self.init_solution['x_it_3'][i][t]

        for i, t, b in itb_list:
            x_itb_4[i, t, b].start = self.init_solution['x_itb_4'][i][t][b]

        for i, t in it_list:
            y_it_2[i, t].start = self.init_solution['y_it_2'][i][t]

        for i, t, b in itb_list:
            y_itb_2[i, t, b].start = self.init_solution['y_itb_2'][i][t][b]

        for i, t in it_list:
            y_it_3[i, t].start = self.init_solution['y_it_3'][i][t]

        for i, t in it_list:
            y_it_4[i, t].start = self.init_solution['y_it_4'][i][t]

        for o, i, t, p in oitp_list:
            z_oit_p[o, i, t, p].start = self.init_solution['z_oit_p'][o][i][t][p]

        for o, t, p in otp_list:
            z_ot_p[o, t, p].start = self.init_solution['z_ot_p'][o][t][p]


        # result_info = {
        #     'x_op': x_op,
        #     'x_itb_1': x_itb_1,
        #     'x_it_2': x_it_2,
        #     'x_itp_2': x_itp_2,
        #     'x_it_3': x_it_3,
        #     'x_itb_4': x_itb_4,
        #     'y_it_2': y_it_2,
        #     'y_itb_2': y_itb_2,
        #     'y_it_3': y_it_3,
        #     'y_it_4': y_it_4,
        #     'z_oit_p': z_oit_p,
        #     'z_ot_p': z_ot_p,
        # }
        result_info = {
            'x_it_3': x_it_3,
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

        # x_op
        info_x_op = []
        info_xop = []
        for o in range(self.O):
            x_o = []
            for p in range(self.P):
                var_name_x = f"x_op[{o},{p}]"
                x_o_p = Model.getVarByName(var_name_x).X
                if x_o_p > 0:
                    info_xop.append([o, p])
                x_o.append(x_o_p)
            info_x_op.append(x_o)
        result_info['info_x_op'] = info_x_op
        # result_info['info_xop'] = info_xop
        # x_itb_1
        info_x_itb_1 = []
        info_xitb1= []
        for i in range(self.I):
            x_i = []
            for t in range(self.T):
                x_i_t = []
                for b in range(self.B):
                    var_name_x = f"x_itb_1[{i},{t},{b}]"
                    x_i_t_b_1 = Model.getVarByName(var_name_x).X
                    if x_i_t_b_1 > 0:
                        info_xitb1.append([i, t, b])
                    x_i_t.append(x_i_t_b_1)
                x_i.append(x_i_t)
            info_x_itb_1.append(x_i)
        result_info['info_x_itb_1'] = info_x_itb_1
        # result_info['info_xitb1'] = info_xitb1
        # x_it_2
        info_x_it_2 = []
        info_xit2 = []
        for i in range(self.I):
            x_i = []
            for t in range(self.T):
                var_name_x = f"x_it_2[{i},{t}]"
                x_i_t_2 = Model.getVarByName(var_name_x).X
                if x_i_t_2 > 0:
                    info_xit2.append([i, t])
                x_i.append(x_i_t_2)
            info_x_it_2.append(x_i)
        result_info['info_x_it_2'] = info_x_it_2
        # result_info['info_xit2'] = info_xit2
        # x_itp_2
        info_x_itp_2 = []
        info_xitp2 = []
        for i in range(self.I):
            x_i = []
            for t in range(self.T):
                x_i_t = []
                for p in range(self.P):
                    var_name_x = f"x_itp_2[{i},{t},{p}]"
                    x_i_t_p_2 = Model.getVarByName(var_name_x).X
                    if x_i_t_p_2 > 0:
                        info_xitp2.append([i, t, p])
                    x_i_t.append(x_i_t_p_2)
                x_i.append(x_i_t)
            info_x_itp_2.append(x_i)
        result_info['info_x_itp_2'] = info_x_itp_2
        # result_info['info_xitp2'] = info_xitp2
        # x_it_3
        info_x_it_3 = []
        info_xit3 = []
        for i in range(self.I):
            x_i = []
            for t in range(self.T):
                var_name_x = f"x_it_3[{i},{t}]"
                x_i_t_3 = Model.getVarByName(var_name_x).X
                if x_i_t_3 > 0:
                    info_xit3.append(x_i_t_3)
                x_i.append(x_i_t_3)
            info_x_it_3.append(x_i)
        result_info['info_x_it_3'] = info_x_it_3
        # result_info['info_xit3'] = info_xit3
        # x_itb_4
        info_x_itb_4 = []
        info_xitb4 = []
        for i in range(self.I):
            x_i = []
            for t in range(self.T):
                x_i_t = []
                for b in range(self.B):
                    var_name_x = f"x_itb_4[{i},{t},{b}]"
                    x_i_t_b_4 = Model.getVarByName(var_name_x).X
                    if x_i_t_b_4 > 0:
                        info_xitb4.append([i, t, b])
                    x_i_t.append(x_i_t_b_4)
                x_i.append(x_i_t)
            info_x_itb_4.append(x_i)
        result_info['info_x_itb_4'] = info_x_itb_4
        # result_info['info_xitb4'] = info_xitb4
        # y_it_2
        info_y_it_2 = []
        info_yit2 = []
        for i in range(self.I):
            y_i = []
            for t in range(self.T):
                var_name_y = f"y_it_2[{i},{t}]"
                y_i_t_2 = Model.getVarByName(var_name_y).X
                if y_i_t_2 > 0:
                    info_yit2.append([i, t])
                y_i.append(y_i_t_2)
            info_y_it_2.append(y_i)
        result_info['info_y_it_2'] = info_y_it_2
        # result_info['info_yit2'] = info_yit2
        # y_itb_2
        info_y_itb_2 = []
        info_yitb2 = []
        for i in range(self.I):
            y_i = []
            for t in range(self.T):
                y_i_t = []
                for b in range(self.B):
                    var_name_y = f"y_itb_2[{i},{t},{b}]"
                    y_i_t_b_2 = Model.getVarByName(var_name_y).X
                    if y_i_t_b_2 > 0:
                        info_yitb2.append([i, t, b])
                    y_i_t.append(y_i_t_b_2)
                y_i.append(y_i_t)
            info_y_itb_2.append(y_i)
        result_info['info_y_itb_2'] = info_y_itb_2
        # result_info['info_yitb2'] = info_yitb2
        # y_it_3
        info_y_it_3 = []
        info_yit3 = []
        for i in range(self.I):
            y_i = []
            for t in range(self.T):
                var_name_y = f"y_it_3[{i},{t}]"
                y_i_t_3 = Model.getVarByName(var_name_y).X
                if y_i_t_3 > 0:
                    info_yit3.append([i, t])
                y_i.append(y_i_t_3)
            info_y_it_3.append(y_i)
        result_info['info_y_it_3'] = info_y_it_3
        # result_info['info_yit3'] = info_yit3
        # y_it_4
        info_y_it_4 = []
        info_yit4 = []
        for i in range(self.I):
            y_i = []
            for t in range(self.T):
                var_name_y = f"y_it_4[{i},{t}]"
                y_i_t_4 = Model.getVarByName(var_name_y).X
                if y_i_t_4 > 0:
                    info_yit4.append([i, t])
                y_i.append(y_i_t_4)
            info_y_it_4.append(y_i)
        result_info['info_y_it_4'] = info_y_it_4
        # result_info['info_yit4'] = info_yit4
        # z_oit_p
        info_z_oit_p = []
        info_zoitp = []
        for o in range(self.O):
            z_o = []
            for i in range(self.I):
                z_o_i = []
                for t in range(self.T):
                    z_o_i_t = []
                    for p in range(self.P):
                        var_name_z = f"z_oit_p[{o},{i},{t},{p}]"
                        z_o_i_t_p = Model.getVarByName(var_name_z).X
                        if z_o_i_t_p > 0:
                            info_zoitp.append([o, i, t, p])
                        z_o_i_t.append(z_o_i_t_p)
                    z_o_i.append(z_o_i_t)
                z_o.append(z_o_i)
            info_z_oit_p.append(z_o)
        result_info['info_z_oit_p'] = info_z_oit_p
        # result_info['info_zoitp'] = info_zoitp
        # z_ot_p
        info_z_ot_p = []
        info_zotp = []
        for o in range(self.O):
            z_o = []
            for t in range(self.T):
                z_o_t = []
                for p in range(self.P):
                    var_name_z = f"z_ot_p[{o},{t},{p}]"
                    z_o_t_p = Model.getVarByName(var_name_z).X
                    if z_o_t_p > 0:
                        info_zotp.append([o, t, p])
                    z_o_t.append(z_o_t_p)
                z_o.append(z_o_t)
            info_z_ot_p.append(z_o)
        result_info['info_z_ot_p'] = info_z_ot_p
        # result_info['info_zotp'] = info_zotp


        upper_bound = Model.ObjVal
        lower_bound = Model.ObjBound
        MIPGap = Model.MIPGap
        CPU_Time = end_Time - start_Time
        result_info['upper_bound'] = upper_bound
        result_info['lower_bound'] = lower_bound
        result_info['MIPGap'] = MIPGap
        result_info['CPU_time'] = CPU_Time

        return result_info

if __name__ == "__main__":
    input_path = "/Users/xiekio/Desktop/研一/组会/毕设/My/O-T-A-S-in-IMTK-SRS/src/Instance/myRandomInstanceGurobi.json"
    instance_obj = read_input_data(input_path)
    input_path2 = "/Users/xiekio/Desktop/研一/组会/毕设/My/O-T-A-S-in-IMTK-SRS/src/gurobi/Initial_gurobi.json"
    with open(input_path2, 'r') as f:
        json_file = json.load(f)
    # Initial_solution = read_input_data_initial("/src/gurobi/Initial_gurobi.json")
    gurobi_alg = IntegratedGurobi(instance=instance_obj, init_solution=json_file, time_limit=9600, max_T=20)
    # Model = gp.Model('IntegratedGurobiModel')
    # result_info = gurobi_alg.build_gurobi_model(Model=Model)
    result_info = gurobi_alg.run_gurobi_model()

    print(result_info)