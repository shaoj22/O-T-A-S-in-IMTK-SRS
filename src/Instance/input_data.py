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
    station_buffer_num = json_file['station_buffer_num']
    block_storage_num = json_file['block_storage_num']
    max_T = json_file['max_T']
    return Instance(order_list, tote_list, station_list, block_list, station_buffer_num, block_storage_num, max_T)

def read_input_data_initial(input_path):
    with open(input_path, 'r') as f:
        json_file = json.load(f)
    x_op = json_file['x_op']
    x_itb_1 = json_file['x_itb_1']
    x_it_2 = json_file['x_it_2']
    x_itp_2 = json_file['x_itp_2']
    x_it_3 = json_file['x_it_3']
    x_itb_4 = json_file['x_itb_4']
    y_it_2 = json_file['y_it_2']
    y_itb_2 = ['y_itb_2']
    y_it_3 = ['y_it_3']
    y_it_4 = json_file['y_it_4']
    z_oit_p = json_file['z_oit_p']
    z_ot_p = json_file['z_ot_p']
    return x_op, x_itb_1, x_it_2, x_itp_2, x_it_3, x_itb_4, y_it_2, y_itb_2, y_it_3, y_it_4, z_oit_p, z_ot_p

if __name__ == "__main__":
    input_path = "myRandomInstanceGurobi.json"
    instance_obj = read_input_data(input_path)
    print('order_list:', instance_obj.order_list)
    print('tote_list:', instance_obj.tote_list)
    print('station_list:', instance_obj.station_list)
    print('block_list:', instance_obj.block_list)
    print('station_buffer_num:', instance_obj.station_buffer_num)
    print('block_storage_num:', instance_obj.block_storage_num)
    print('max_T:', instance_obj.max_T)