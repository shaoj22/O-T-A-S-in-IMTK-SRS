import json
import time
input_path2 = "/Users/xiekio/Desktop/研一/组会/毕设/My/O-T-A-S-in-IMTK-SRS/src/alns/Initial_variables.json"
start = time.time()
with open(input_path2, 'r') as f:
    json_file = json.load(f)
end = time.time()
x_op = json_file['x_op']

print("时长；", end - start)
print(x_op)