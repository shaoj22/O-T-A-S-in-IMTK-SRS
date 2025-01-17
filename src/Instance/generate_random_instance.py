import sys

<<<<<<< HEAD
sys.path.append('../../../..')
=======
sys.path.append('..')
>>>>>>> f2fa453c1cd9227e2431a9a49fc79f776f26b991
import random
import json
from src.entity.Order import Order
from src.entity.Tote import Tote
from src.entity.Station import Station
from src.entity.Block import Block


class genRandomInstance:
<<<<<<< HEAD
<<<<<<< HEAD
    def __init__(self, order_nums=0, tote_nums=0, station_nums=0, block_nums=0, station_buffer_num=5, block_storage_num=4, instance_name='myRandomInstance') -> None:
=======
    def __init__(self, order_nums=0, tote_nums=0, station_nums=0, block_nums=0, station_buffer_num=2, block_storage_num=2, instance_name='myRandomInstance') -> None:
>>>>>>> f2fa453c1cd9227e2431a9a49fc79f776f26b991
=======
    def __init__(self, order_nums=0, tote_nums=0, station_nums=0, block_nums=0, station_buffer_num=0, block_storage_num=0, instance_name='myRandomInstance') -> None:
>>>>>>> f64ba4a82e9f5fd2069c4a76ee951eeac10c5df6
        """ init the instance
        Args:
            order_nums (int): the number of the orders.
            tote_nums (int): the number of the totes.
            station_nums (int): the number of the stations.
            block_nums (int): the number of the blocks.
        Return:
            json_file.
        """
        self.order_nums = order_nums
        self.tote_nums = tote_nums
        self.station_nums = station_nums
        self.block_nums = block_nums
        self.station_buffer_num = station_buffer_num
        self.block_storage_num = block_storage_num
        self.instance_name = instance_name
        self.order_list = []
        self.tote_list = []
        self.station_list = []
        self.block_list = []
        self.json_dict = self.gen_json()

    def gen_orders(self):
        """ gen the orders list """
        for order in range(self.order_nums):
            # gen the sku of the order
<<<<<<< HEAD
<<<<<<< HEAD
            sku_nums = random.randint(4, 6)  # sku nums
=======
            sku_nums = random.randint(2, 3)  # sku nums
>>>>>>> f2fa453c1cd9227e2431a9a49fc79f776f26b991
=======
            sku_nums = random.randint(5, 8)  # sku nums
>>>>>>> b4a75b2bab41d51532cfdf1b3e00575e192b524f
            sku_list = []  # sku list
            for sku in range(sku_nums):
                accept = False
                while not accept:
                    sku_idx = random.randint(0, self.tote_nums - 1)
                    if sku_idx not in sku_list:
                        sku_list.append(sku_idx)
                        accept = True
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

    def gen_blocks(self):
        """ gen the blocks list """
        sku_list = []
        for block in range(self.block_nums):
            sku_list.append([])
        for i in range(tote_nums):
            delete = False
            while not delete:
                block = random.randint(0, block_nums - 1)
                if len(sku_list[block]) < 2:
                    sku_list[block].append(i)
                    delete = True
        for block in range(self.block_nums):
            block_obj = Block(idx=block, sku=sku_list[block])
            self.block_list.append(block_obj)

    def gen_json(self):
        """ gen the json file of the instance"""
        # gen the orders, totes, and stations.
        self.gen_orders()
        self.gen_totes()
        self.gen_stations()
        self.gen_blocks()
        json_dict = {}
        # gen the json file
        order_idx_list = []
        tote_idx_list = []
        station_idx_list = []
        block_idx_list = []
        for i in range(self.order_nums):
            order_dict = {}
            order_dict['orderIdx'] = i
            order_dict['sku'] = self.order_list[i].sku
            order_idx_list.append(order_dict)
        for j in range(self.tote_nums):
            tote_idx_list.append(j)
        for k in range(self.station_nums):
            station_idx_list.append(k)
        for b in range(self.block_nums):
            block_dict = {}
            block_dict['blockIdx'] = b
            block_dict['sku'] = self.block_list[b].sku
            block_idx_list.append(block_dict)
        json_dict['order_list'] = order_idx_list
        json_dict['tote_list'] = tote_idx_list
        json_dict['station_list'] = station_idx_list
        json_dict['block_list'] = block_idx_list
        json_dict['station_buffer_num'] = self.station_buffer_num
        json_dict['block_storage_num'] = self.block_storage_num
        json_file_path = self.instance_name + '.json'
        with open(json_file_path, 'w') as f:
            json.dump(json_dict, f, indent=4)
        return json_dict


if "__main__" == __name__:
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
    order_nums = 30
    tote_nums = 30
    station_nums = 5
    block_nums = 4
=======
    order_nums = 4
    tote_nums = 8
    station_nums = 1
    block_nums = 1
>>>>>>> f2fa453c1cd9227e2431a9a49fc79f776f26b991
    random_instance = genRandomInstance(order_nums=order_nums, tote_nums=tote_nums, station_nums=station_nums, block_nums=block_nums,
=======
    order_nums = 50
    tote_nums = 8
=======
    order_nums = 11
    tote_nums = 10
>>>>>>> b4a75b2bab41d51532cfdf1b3e00575e192b524f
    station_nums = 3
    block_nums = 5
    station_buffer_num = 4
    block_storage_num = 3
    random_instance = genRandomInstance(order_nums=order_nums, tote_nums=tote_nums, station_nums=station_nums, block_nums=block_nums, station_buffer_num=station_buffer_num, block_storage_num=block_storage_num,
>>>>>>> f64ba4a82e9f5fd2069c4a76ee951eeac10c5df6
                                        instance_name='myRandomInstanceGurobi')
    print("order_list:", random_instance.json_dict['order_list'])
    print("tote_list:", random_instance.json_dict['tote_list'])
    print("station_list:", random_instance.json_dict['station_list'])
    print("block_list:", random_instance.json_dict['block_list'])
