import subprocess
import psutil
import threading 
import time 
import os
import config 
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('seed_num', type=int)
parser.add_argument('fanout', type=int)
parser.add_argument('steps', type=int)
parser.add_argument('-w', '--workers', type=int, default=12)
parser.add_argument('-s', '--servers', type=int, default=12)
parser.add_argument('-d', '--duration', type=float, default=20)
parser.add_argument('-l', '--local', action='store_true')
parser.add_argument('-f', '--feature', action='store_true')
parser.add_argument('-i', '--id', type=int, default=0)
parser.add_argument('-p', '--partition', type=str, default="random")
parser.add_argument('-t', '--server_thread', type=int, default=12)

args = parser.parse_args()

worker_num = args.workers
server_num = args.servers
duration = args.duration
local = args.local
duplicate = False
server_err_prefix = "log/server.err."

seed_num = args.seed_num
fanout = args.fanout
steps = args.steps

repeat = 3
skip_first = True

feats = args.feature

if local:
  print "local worker:%d"%(worker_num)
else:
  print "remote worker:%d server: p %d t %d"%(worker_num, server_num, args.server_thread)

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
      cmd = "python ./sample_test.py %d %d %d %s -d %f -l -p %s 2>log/client.err.%d"%(
        seed_num, fanout, steps, "-f" if feats else "", 
        args.duration, args.partition, i)
    else:
      cmd = "python ./sample_test.py %d %d %d %s -d %f -p %s 2>log/client.err.%d"%(
        seed_num, fanout, steps, "-f" if feats else "",
        args.duration, args.partition, i)
    workers.append(subprocess.Popen(args=cmd, stdout=subprocess.PIPE, shell=True))
    # time.sleep(0.2)

  throughputs = []
  durations = []
  node_num = 0
  sample_num = 0
  for w in workers:
    output = w.communicate()[0]
    output = output.split('\n')[-2]
    print output
    waiting_worker -= 1
    throughput = float(output.strip().split(' ')[-1])
    throughputs.append(throughput)
    duration = float(output.strip().split(' ')[-2])
    durations.append(duration)
    # node_num += float(output.strip().split(' ')[-2])
    # sample_num += int(output.strip().split(' ')[-3])

  cm.join()
  return sum(throughputs) , sum(durations) / worker_num
  # / worker_num
  # , max(cpu_usage), node_num, sample_num

if local:
  os.system("pkill -9 local_graph_test -f")
else:
  os.system("pkill -9 start_server -f")
  os.system("pkill -9 sample_test -f")

  server_process = []
  directory = config.partition_config[args.partition]['directory']
  for i in range(server_num):
    if duplicate:
      cmd = "python start_server.py --shard_idx %d --shard_num %d --directory %s --thread_num %d\
          >log/server.out.%d 2>%s%d"%(
      0, 1, directory, args.server_thread, i, server_err_prefix, i
      )
    else:
      cmd = "python start_server.py --shard_idx %d --shard_num %d --directory %s --thread_num %d\
          >log/server.out.%d 2>%s%d"%(
      i, server_num, directory, args.server_thread, i, server_err_prefix, i
      )
    p = subprocess.Popen(args=cmd, shell=True)
    server_process.append(p)
  time.sleep(1)
  moniter_server_start(server_num)
  print "service started"
  time.sleep(5)

t_log = []
d_log = []
# c_log = []
# nn_tt = 0
# sn_tt = 0
for i in range(repeat):
  t, d = run()
  print "#", i, "Tput:", t," | Avg RTT(ms):", d * 1000
  # print t, c
  if i > 0 or not skip_first:
    t_log.append(t)
    d_log.append(d)
    # c_log.append(c)
    # nn_tt += nn
    # sn_tt += sn

if repeat > 1:
  print "Avg Tput(KETPS):", sum(t_log) / len(t_log), "| Avg RTT:", sum(d_log)/ len(d_log)

if not local:
  os.system("pkill -9 start_server -f")