from src.heurisitc_algorithm.order_sequence_greedy_fix import GREEDY
from src.Instance.input_data import read_input_data
from src.alns.tool.evaluator import EVALUATOR


class AdaptiveGreedyInitial:
    def __init__(self, input_path):
        self.input_path = input_path
        self.instance_obj = read_input_data(input_path)
        self.num_stations = self.instance_obj.station_num
        self.num_orders = self.instance_obj.order_num
        self.T = self.instance_obj.max_T
        # self.T = T

    def run(self):
        g_initial = GREEDY(self.input_path, self.T)
        # 调用主函数，得到料箱出库顺序
        while len(g_initial.un_order_list) != 0:
            # 输出拣选站矩阵
            # for station in g_initial.station_list:
            #     orders_in_station = g_initial.station_matrix[station]
            #     print(f"拣选站 {station} 目前处理的订单：{orders_in_station}")
            g_initial.process_orders()
        # print(g_initial.x_op)
        # 得到x_otp
        greedy_op_matrix = []
        for p in range(self.num_stations):
            greedy_op_matrix.append([])
        for t in range(self.T):
            for p in range(self.num_stations):
                for o in range(self.num_orders):
                    if g_initial.z_ot_p[o][t][p] == 1 and o not in greedy_op_matrix[p]:
                        greedy_op_matrix[p].append(o)
        print(greedy_op_matrix)
        return greedy_op_matrix

# test code
# input_path = "/Users/xiekio/Desktop/研一/组会/毕设/My/O-T-A-S-in-IMTK-SRS/src/Instance/Instance-small-2.json"
# T = 90
# agi = AdaptiveGreedyInitial(input_path, T=T)
# mat = agi.run()
# print(mat)
# ev = EVALUATOR(input_path, mat, T)
# tt = ev.evaluate_solution()
# print(tt)