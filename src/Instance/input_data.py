import sys
sys.path.append('../')
import json
from src.entity.Instance import Instance


def read_input_data(input_path):
    """ read the json file from inputs """
    with open(input_path, 'r') as f:
        json_file = json.load(f)
    order_list = json_file['order_list']
    tote_list = json_file['tote_list']
    station_list = json_file['station_list']
    block_list = json_file['block_list']
    return Instance(order_list, tote_list, station_list, block_list)


if __name__ == "__main__":
    input_path = "myRandomInstanceGurobi.json"
    instance_obj = read_input_data(input_path)
    print('order_list:', instance_obj.order_list)
    print('tote_list:', instance_obj.tote_list)
    print('station_list:', instance_obj.station_list)
    print('block_list:', instance_obj.block_list)
    print('station_buffer_num:', instance_obj.station_buffer_num)
    print('block_storage_num:', instance_obj.block_storage_num)