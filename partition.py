import json
import os
from euler.tools import json2dat


PREFIX = "ppi/ppi"
DAT_PATH = PREFIX + "_data.json"
PARTITION_NUM = 4

output_file = [open(PREFIX + "_data_" + str(i) + ".json", "w") for i in range(PARTITION_NUM)]
cnt = 0
with open(DAT_PATH, "r") as f:
    for line in f:
        output_file[cnt % PARTITION_NUM].write(line)
        cnt += 1
del output_file

for i in range(PARTITION_NUM):
    print "converting:", i
    c = json2dat.Converter(PREFIX + '_meta.json', PREFIX + '_data_%d.json'%i,
                        PREFIX + '_data_%d.dat'%i)
    c.do()