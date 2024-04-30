'''
File: Instance.py
Project: Joint_Optimization_of_Order_and_Totes_for_WayZim.
Description:
-----------
read the input data (json file) and create the Instance class.
-----------
Author: 626
Created Date: 2023-1110
'''


class Instance:
    def __init__(self, order_list=None, tote_list=None, station_list=None, station_buffer_num=5):
        self.order_list = order_list # 订单列表
        self.tote_list = tote_list # 料箱列表
        self.station_list = station_list # 工作站列表
        self.order_num = len(self.order_list) # 订单数量
        self.tote_num = len(self.tote_list) # 料箱数量
        self.station_num = len(self.station_list) # 工作站数量
        self.station_buffer_num = station_buffer_num # 工作站订单缓存数量
        self.to_matrix = self.gen_tote_and_order_matrix()

    def gen_tote_and_order_matrix(self):
        """ generate the tote and order's matrix """
        to_matrix = [[0 for i in range(self.order_num)] for j in range(self.tote_num)]
        for order in self.order_list:
            for sku in order['sku']:
                to_matrix[sku][order['orderIdx']] = 1
        return to_matrix


