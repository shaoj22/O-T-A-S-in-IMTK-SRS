'''
File: input_data.py
Project: Joint_Optimization_of_Orders_and_Totes_for_WayZim.
Description:
-----------
read the input data (json file) and create the Instance class.
-----------
Author: 626
Created Date: 2023-1109
'''


import sys
sys.path.append('../')
import json
from Joint_Optimization_of_Orders_and_Totes_for_WayZim.src.entity.Instance import Instance


def read_input_data(input_path):
    """ read the json file from inputs """
    with open(input_path, 'r') as f:
        json_file = json.load(f)
    order_list = json_file['order_list']
    tote_list = json_file['tote_list']
    station_list = json_file['station_list']
    return Instance(order_list, tote_list, station_list)


if __name__ == "__main__":
    input_path = "..\\inputs\\myRandomInstance1.json"
    instance_obj = read_input_data(input_path)
    print('order_list:', instance_obj.order_list)
    print('tote_list:', instance_obj.tote_list)
    print('station_list:', instance_obj.station_list)
    print('station_buffer_num:', instance_obj.station_buffer_num)