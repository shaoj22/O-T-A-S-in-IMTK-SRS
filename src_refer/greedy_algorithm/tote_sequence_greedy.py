'''
File: input_data.py
Project: Joint_Optimization_of_Order_and_Totes_for_WayZim.
Description:
-----------
read the input data (json file) and create the Instance class.
-----------
Author: 626
Created Date: 2023-1109
'''

import sys
sys.path.append('../')
from src.instance.input_data import read_input_data

class ToteSequenceGreedy:
    def __init__(self, instance, order_sequence_solution=None):
        """ init the ToteSequenceGreedy """
        self.instance = instance
        self.order_sequence_solution = order_sequence_solution
        self.order_list = self.instance.order_list
        self.tote_sequence_solution = []
        self.tote_sequence_greedy()
    
    def tote_sequence_greedy(self):
        """ generate the greedy solution of the tote sequence """
        for station in range(len(self.order_sequence_solution)):
            self.tote_sequence_solution.append(self.tote_sequence_greedy_of_station(self.order_sequence_solution[station]))

    def tote_sequence_greedy_of_station(self, order_sequence_of_station):
        """ generate one station's solution of the tote sequence """
        tote_sequence_of_station = [] # one station's tote sequence
        station_buffer = [] # station order buffer
        station_order_sku_buffer = [] # station order's sku buffer
        for i in range(self.instance.station_buffer_num): # init the station buffer
            if not order_sequence_of_station:
                break
            station_buffer.append(order_sequence_of_station[0])
            station_order_sku_buffer.append(self.order_list[order_sequence_of_station[0]]['sku'])
            order_sequence_of_station.pop(0)
        sku_num_dict = {} # sku num dict
        for order in station_buffer: # init calculate the sku 
            for sku in self.order_list[order]['sku']:
                sku_num_dict[sku] = 1
        while len(station_buffer) > 0: # 只要工作站上还有order就继续添加料箱
            while len(order_sequence_of_station) > 0 and len(station_buffer) < self.instance.station_buffer_num: # 如果还有订单未上工作站且工作站有空分拨口
                station_buffer.append(order_sequence_of_station[0]) # 将第一个order加入工作站
                station_order_sku_buffer.append(self.order_list[order_sequence_of_station[0]]['sku'])
                for sku in self.order_list[order_sequence_of_station[0]]['sku']: # add the sku into the sku num dict
                    sku_num_dict[sku] = 1
                order_sequence_of_station.pop(0) # 删除订单
            max_sku = max(sku_num_dict, key=sku_num_dict.get) # get the greedy max sku of the station buffer
            tote_sequence_of_station.append(max_sku) # add the max sku tote into the sequence
            sku_num_dict[max_sku] = 0
            station_order_sku_buffer = [[value for value in row if value != max_sku] for row in station_order_sku_buffer]
            num = 0
            for row in station_order_sku_buffer:
                if not row:
                    station_order_sku_buffer.remove(row)
                    station_buffer.remove(station_buffer[num])
                num += 1
        
        return tote_sequence_of_station

if "__main__" == __name__:
    input_path = "D:\\Desktop\\python_code\\Joint_Optimization_of_Orders_and_Totes_for_WayZim\\inputs\\myRandomInstance1.json"
    instance_obj = read_input_data(input_path)
    print('order_list:', instance_obj.order_list)
    print('tote_list:', instance_obj.tote_list)
    print('station_list:', instance_obj.station_list)
    print('station_buffer_num:', instance_obj.station_buffer_num)



            


                


        



