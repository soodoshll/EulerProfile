import json
import os
from euler.tools import json2dat
import random
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--mode', type=str, default='random')
parser.add_argument('--prefix', type=str)
parser.add_argument('--dest_prefix', type=str)
parser.add_argument('--num', type=int, default=4)
args = parser.parse_args()

def random_partition(prefix, dest_prefix, num):
    output_file = [open(dest_prefix + "_data_" + str(i) + ".json", "w") for i in range(num)]
    data_path = prefix + "_data.json"
    cnt = 0
    with open(data_path, "r") as f:
        for line in f:
            rand_part = random.randint(0, num - 1)
            output_file[rand_part].write(line)
            cnt += 1
    del output_file

    for i in range(num):
        print "converting:", i
        c = json2dat.Converter(prefix + '_meta.json', dest_prefix + '_data_%d.json'%i,
                        dest_prefix + '_data_%d.dat'%i)
        c.do()

if args.mode == 'metis':
    pass 
else:
    random_partition(args.prefix, args.dest_prefix, args.num)