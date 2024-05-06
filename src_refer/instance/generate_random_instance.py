'''
File: generate_random_instance.py
Project: Joint_Optimization_of_Orders_and_Totes_for_WayZim.
Description:
-----------
generate random instance for the problem.
-----------
Author: 626
Created Date: 2023-1109
'''


import sys
sys.path.append('..')
import random
import json
from src.entity.Order import Order
from src.entity.Tote import Tote
from src.entity.Station import Station


class genRandomInstance:
    def __init__(self, order_nums=0, tote_nums=0, station_nums=0, station_buffer_num=5, instance_name='myRandomInstance') -> None:
        """ init the instance 
        Args:
            order_nums (int): the number of the orders.
            tote_nums (int): the number of the totes.
            station (int): the number of the stations.
        Return:
            json_file.
        """
        self.order_nums = order_nums
        self.tote_nums = tote_nums
        self.station_nums = station_nums
        self.station_buffer_num = station_buffer_num
        self.instance_name = instance_name
        self.order_list = []
        self.tote_list = []
        self.station_list = []
        self.json_dict = self.gen_json()

    def gen_orders(self):
        """ gen the orders list """
        for order in range(self.order_nums):
            # gen the sku of the order
            sku_nums = random.randint(4, 6) # sku nums
            sku_list = [] # sku list
            for sku in range(sku_nums):
                sku_idx = random.randint(0, self.tote_nums-1) 
                if sku_idx not in sku_list:
                    sku_list.append(sku_idx)
            order_obj = Order(idx=order, sku=sku_list)
            self.order_list.append(order_obj)

    def gen_totes(self):
        """ gen the totes list """
        for tote in range(self.tote_nums):
            tote_obj = Tote(idx=tote)
            self.tote_list.append(tote_obj)

    def gen_stations(self):
        """ gen the stations list """
        for station in range(self.station_nums):
            station_obj = Station(idx=station)
            self.station_list.append(station_obj)

    def gen_json(self):
        """ gen the json file of the instance"""
        # gen the orders, totes, and stations.
        self.gen_orders()
        self.gen_totes()
        self.gen_stations()
        json_dict = {}
        # gen the json file
        order_idx_list = []
        tote_idx_list = []
        station_idx_list = []
        for i in range(self.order_nums):
            order_dict = {}
            order_dict['orderIdx'] = i
            order_dict['sku'] = self.order_list[i].sku
            order_idx_list.append(order_dict)
        for j in range(self.tote_nums):
            tote_idx_list.append(j)
        for k in range(self.station_nums):
            station_idx_list.append(k)
        json_dict['order_list'] = order_idx_list
        json_dict['tote_list'] = tote_idx_list
        json_dict['station_list'] = station_idx_list
        json_dict['station_buffer_num'] = self.station_buffer_num
        json_file_path = self.instance_name + '.json'
        with open(json_file_path, 'w') as f:
            json.dump(json_dict, f, indent=4)
        return json_dict


if "__main__" == __name__:
    order_nums = 30
    tote_nums = 30
    station_nums = 5
    random_instance = genRandomInstance(order_nums=order_nums,\
                    tote_nums=tote_nums, station_nums=station_nums,\
                    instance_name='myRandomInstanceGurobi')
    print("order_list:", random_instance.json_dict['order_list'])
    print("tote_list:", random_instance.json_dict['tote_list'])
    print("station_list:", random_instance.json_dict['station_list'])
    


    