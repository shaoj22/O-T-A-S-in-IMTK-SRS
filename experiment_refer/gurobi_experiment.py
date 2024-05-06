
"""
"""
import sys
sys.path.append('..')
import xlwt
import time
from src.solver_algorithm.gurobi import IntegratedGurobi
from src.instance.input_data import read_input_data
from src.clustering_algorithm.order_assignment_greedy import OrderAssignmentGreedy
from src.greedy_algorithm.order_sequence_greedy import OrderSequenceGreedy
from src.greedy_algorithm.tote_sequence_greedy import ToteSequenceGreedy
from src.mate_heuristic_algorithm.adaptive_large_scale_neighborhood_search import ALNS

book = xlwt.Workbook(encoding='utf-8')
sheet = book.add_sheet("gurobi_solution")
# 构建excel的表头
sheet.write(0, 0, "ID")
sheet.write(0, 1, "Order")
sheet.write(0, 2, "SKUs")
sheet.write(0, 3, "Station")
sheet.write(0, 4, "Outbound Shipments")
sheet.write(0, 5, "Upper Bound")
sheet.write(0, 6, "Lower Bound")
sheet.write(0, 7, "MIP Gap")
sheet.write(0, 8, "CPU time")

sheet.write(0, 9, "Heuristic Obj")
sheet.write(0, 10, "Gap UB")
sheet.write(0, 11, "Gap LB")
sheet.write(0, 12, "CPU time")

sheet.write(0, 13, "ALNS Obj")
sheet.write(0, 14, "Gap UB")
sheet.write(0, 15, "Gap LB")
sheet.write(0, 16, "CPU time")


for i in range(16, 20):
    input_path = "D:\\Desktop\\python_code\\Joint_Optimization_of_Orders_and_Totes_for_WayZim\\experiment\\small_scale_experiment\\myRandomInstanceGurobi" + str(i) + ".json"
    instance_obj = read_input_data(input_path)
    # gurobi 
    outbound_shipments = 0
    for order in instance_obj.order_list:
        outbound_shipments += len(order['sku'])
    max_T = outbound_shipments//instance_obj.station_num + 10
    print(max_T)
    gurobi_alg = IntegratedGurobi(instance=instance_obj, time_limit=1800, max_T=max_T)
    result_info = gurobi_alg.run_gurobi_model()
    sheet.write(i + 1, 0, i + 1)
    sheet.write(i + 1, 1, instance_obj.order_num)
    sheet.write(i + 1, 2, instance_obj.tote_num)
    sheet.write(i + 1, 3, instance_obj.station_num)
    sheet.write(i + 1, 4, outbound_shipments)
    sheet.write(i + 1, 5, result_info['upper_bound'])
    sheet.write(i + 1, 6, result_info['lower_bound'])
    sheet.write(i + 1, 7, result_info['MIPGap'])  
    sheet.write(i + 1, 8, result_info['CPU_time'])
    # heuristic
    start_time1 = time.time()
    order_assignment_greedy_alg = OrderAssignmentGreedy(instance=instance_obj)
    order_assignment_greedy_solution = order_assignment_greedy_alg.order_assignment_solution
    order_sequence_greedy_alg = OrderSequenceGreedy(instance=instance_obj, order_assignment_solution=order_assignment_greedy_solution)
    order_sequence_greedy_solution = order_sequence_greedy_alg.order_sequence_solution
    tote_sequence_greedy_alg = ToteSequenceGreedy(instance=instance_obj, order_sequence_solution=order_sequence_greedy_solution)
    end_time1 = time.time()
    heuristic_obj = sum(len(row) for row in tote_sequence_greedy_alg.tote_sequence_solution)
    # ALNS
    order_sequence_ALNS_alg = ALNS(instance=instance_obj, iter_num=5000, heuristic=order_sequence_greedy_solution, order_assignment_solution=order_assignment_greedy_solution)
    start_time2 = time.time()
    order_sequence_ALNS_alg.run()
    end_time2 = time.time()
    order_sequence_ALNS_solution = order_sequence_ALNS_alg.best_solution
    ALNS_obj = order_sequence_ALNS_alg.best_obj
    # process data

    sheet.write(i + 1, 9, heuristic_obj)
    sheet.write(i + 1, 10, (heuristic_obj-result_info['upper_bound']))
    sheet.write(i + 1, 11, (heuristic_obj-result_info['lower_bound']))
    sheet.write(i + 1, 12, end_time1-start_time1)

    sheet.write(i + 1, 13, ALNS_obj)
    sheet.write(i + 1, 14, (ALNS_obj-result_info['upper_bound']))
    sheet.write(i + 1, 15, (ALNS_obj-result_info['lower_bound']))
    sheet.write(i + 1, 16, end_time2-start_time2)
     

    # 保存excel文件
    save_path = "D:\\Desktop\\python_code\\Joint_Optimization_of_Orders_and_Totes_for_WayZim\\experiment\\gurobi_small_scale_solution.xls"
    book.save(save_path)


