import subprocess
import psutil
import threading 
import time 
import os
import config 

worker_num = 12
server_num = 1
duration = 20
local = False
duplicate = False
server_err_prefix = "log/server.err."

seed_num = 1000
fanout = 10
steps = 4

repeat = 3
skip_first = True

feats = False

if local:
  print "local worker:%d"%(worker_num)
else:
  print "remote worker:%d server: p %d t %d"%(worker_num, server_num, config.server_thread_num)

def moniter_server_start(server_num):
  for i in range(server_num):
    addr = "n/a"
    with open("%s%d"%(server_err_prefix, i)) as f:
      while True:
        new_line = f.readline()
        if new_line.find("service start") > -1:
          break
        elif new_line.find("bound port") > -1:
          addr = new_line.strip().split(" ")[-1]
        elif new_line == "":
          time.sleep(1)
    print "server %d started at %s"%(i, addr)

def run():
  waiting_worker = worker_num
  cpu_usage = []

  def cpu_monitor(interval = 2):
    while waiting_worker == worker_num:
      cpu_usage.append(psutil.cpu_percent(interval = interval))

  cm = threading.Thread(target=cpu_monitor)
  cm.start()

  workers = []
  for i in range(worker_num):
    if local:
      cmd = "python ./sample_test.py %d %d %d %s -d %f -l 2>log/worker.err.%d"%(
        seed_num, fanout, steps, "-f" if feats else "", 
        duration, i)
    else:
      cmd = "python ./sample_test.py %d %d %d %s -d %f 2>log/worker.err.%d"%(
        seed_num, fanout, steps, "-f" if feats else "",
        duration, i)
    workers.append(subprocess.Popen(args=cmd, stdout=subprocess.PIPE, shell=True))
    # time.sleep(0.2)

  throughputs = []
  node_num = 0
  sample_num = 0
  for w in workers:
    output = w.communicate()[0]
    # print output
    output = output.split('\n')[-2]
    waiting_worker -= 1
    throughput = float(output.strip().split(' ')[-1])
    throughputs.append(throughput)
    # node_num += float(output.strip().split(' ')[-2])
    # sample_num += int(output.strip().split(' ')[-3])

  cm.join()
  return sum(throughputs) 
  # / worker_num
  # , max(cpu_usage), node_num, sample_num

if local:
  os.system("pkill -9 local_graph_test -f")
else:
  os.system("pkill -9 start_server -f")
  os.system("pkill -9 sample_test -f")

  server_process = []
  for i in range(server_num):
    if duplicate:
      cmd = "python start_server.py --shard_idx %d --shard_num %d --directory %s \
          >log/server.out.%d 2>%s%d"%(
      0, 1, "/data/reddit48", i, server_err_prefix, i
      )
    else:
      cmd = "python start_server.py --shard_idx %d --shard_num %d --directory %s \
          >log/server.out.%d 2>%s%d"%(
      i, server_num, "/data/reddit48", i, server_err_prefix, i
      )
    p = subprocess.Popen(args=cmd, shell=True)
    server_process.append(p)
  time.sleep(1)
  moniter_server_start(server_num)
  print "service started"
  time.sleep(5)

t_log = []
# c_log = []
# nn_tt = 0
# sn_tt = 0
for i in range(repeat):
  t = run()
  print "#", i, "Tput:", t
  # print t, c
  if i > 0 or not skip_first:
    t_log.append(t)
    # c_log.append(c)
    # nn_tt += nn
    # sn_tt += sn

if repeat > 1:
  print "avg Tput(KETPS):", sum(t_log) / len(t_log)

if not local:
  os.system("pkill -9 start_server -f")