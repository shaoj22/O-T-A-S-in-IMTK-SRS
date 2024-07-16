import sys
sys.path.append('..')
import pandas as pd
import json
import time
from src.heurisitc_algorithm.order_sequence_greedy_fix import GREEDY
from src.heurisitc_algorithm.order_sequence_fcfs_fix import FCFS
from src.alns.tool.alns_main import ALNS
from src.gurobi.model import IntegratedGurobi
from src.alns.alns_args import *

column_name = ['ID', 'Order', 'Tote', 'Station', 'Block', 'Station_buffer', 'Block_storage', 'FCFS', 'CPU Time1', 'Greedy','CPU Time2', 'Gap1', 'ALNS', 'CPU Time3', 'Gap-F', 'Gap-G', 'Gurobi_upper_bound', 'Gurobi_lower_bound', 'MIPGap', 'CPU Time4', 'Gap_ALNS']
df = pd.DataFrame(columns=column_name)

for i in range(20):
    input_path = "/Users/xiekio/Desktop/研一/组会/毕设/My/O-T-A-S-in-IMTK-SRS/experiment/small_scale_experiment/" + "myRandomInstanceGurobi" + str(i) + ".json"
    instance_obj = read_input_data(input_path=input_path)
    id = i
    order = instance_obj.order_num
    tote = instance_obj.tote_num
    station = instance_obj.station_num
    block = instance_obj.block_num
    station_buffer = instance_obj.station_buffer_num
    block_storage = instance_obj.block_storage_num
    max_T = instance_obj.max_T

    # FCFS
    start_fcfs = time.time()
    f_initial = FCFS(input_path, T=max_T)
    # 分配订单到拣选站
    f_initial.order_devide(t=0)
    # 调用主函数，得到料箱出库顺序
    or_final_sku_list = []
    while len(f_initial.un_order_list) != 0:
        sku_list = f_initial.process_orders()
        for sku in sku_list:
            or_final_sku_list.append(sku)
    fcfs = f_initial.variables_to_sequence()
    end_fcfs = time.time()
    cpu_time1 = end_fcfs - start_fcfs

    # Greedy
    start_greedy = time.time()
    g_initial = GREEDY(input_path, T=max_T)
    # 调用主函数，得到料箱出库顺序
    while len(g_initial.un_order_list) != 0:
        # 输出拣选站矩阵
        for station in g_initial.station_list:
            orders_in_station = g_initial.station_matrix[station]
            # print(f"拣选站 {station} 目前处理的订单：{orders_in_station}")
        g_initial.process_orders()
    greedy = g_initial.variables_to_sequence()
    end_greedy = time.time()
    cpu_time2 = end_greedy - start_greedy
    gap1 = (greedy - fcfs)/fcfs

    # AlNS
    start_alns = time.time()
    alns_args = get_common_alns_args(instance_obj=instance_obj)
    alns_algorithm = ALNS(alns_args=alns_args, input_path=input_path)
    best_solution, best_obj = alns_algorithm.run()
    alns = best_obj
    end_alns = time.time()
    cpu_time3 = end_alns - start_alns
    gap_f = (alns - fcfs)/fcfs
    gap_g = (alns - greedy)/greedy

    input_path2 = "/Users/xiekio/Desktop/研一/组会/毕设/My/O-T-A-S-in-IMTK-SRS/src/alns/Initial_gurobi.json"
    with open(input_path2, 'r') as f:
        json_file = json.load(f)
    gurobi_alg = IntegratedGurobi(instance=instance_obj, init_solution=json_file, time_limit=3600, max_T=max_T)
    result_info = gurobi_alg.run_gurobi_model()
    Gurobi_upper_bound = result_info['upper_bound']
    Gurobi_lower_bound = result_info['lower_bound']
    MIPGap = result_info['MIPGap']
    CPU_time = result_info['CPU_time']
    gap_alns = (Gurobi_upper_bound - alns)/alns

    new_date = [id, order, tote, station, block, station_buffer, block_storage, fcfs, cpu_time1, greedy, cpu_time2, gap1, alns, cpu_time3, gap_f, gap_g, Gurobi_upper_bound, Gurobi_lower_bound, MIPGap, CPU_time, gap_alns]
    df.loc[len(df.index)] = new_date
    excel_path = 'Gurobi_ALNS_Heurisitc_small_scale_solution.xlsx'
    df.to_excel(excel_path, index=False)

