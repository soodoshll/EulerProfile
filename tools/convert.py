from multiprocessing import Process
from euler.tools import json2dat

def do(meta, src, dst):
  c = json2dat.Converter(meta, src, dst)
  c.do()

dest_prefix = "./freebase/metis/freebase"
partition_num = 96
p = [Process(target=do, args=(dest_prefix + '_meta.json', dest_prefix + '_%d.json'%i,
                  dest_prefix + '_%d.dat'%i)) for i in range(partition_num)]
for i in p:
  i.start()

for i in p:
  i.join()