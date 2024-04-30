'''
File: Order.py
Project: Joint_Optimization_of_Orders_and_Totes_for_WayZim.
Description:
-----------
Order class.
-----------
Author: 626
Created Date: 2023-1109
'''


class Order:
    def __init__(self, idx=None, sku=None):
        self.idx = idx # 订单编号
        if sku is None: # 订单包括的sku列表
            self.sku = []
        else:
            self.sku = sku
        
