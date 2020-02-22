import subprocess
import psutil
import threading 
import time 
import os

worker_num = 12

def run():
  waiting_worker = worker_num
  duration = 20
  cpu_usage = []

  def cpu_monitor(interval = 2):
    while waiting_worker > 0:
      cpu_usage.append(psutil.cpu_percent(interval = interval))

  cmd = "python ./sample_test.py 64 2 2 %f 2>/dev/null"%(duration)

  cm = threading.Thread(target=cpu_monitor)
  cm.start()

  workers = []
  for i in range(worker_num):
    workers.append(subprocess.Popen(args=cmd, stdout=subprocess.PIPE, shell=True))
    # time.sleep(0.2)

  throughputs = []
  for w in workers:
    waiting_worker -= 1
    output = w.communicate()[0].split('\n')[-2]
    throughput = float(output.strip().split(' ')[-1])
    throughputs.append(throughput)

  cm.join()
  print sum(throughputs) / worker_num, sum(cpu_usage) / len(cpu_usage)

server_num = 8
server_process = []
for i in range(server_num):
  cmd = "python start_server.py --shard_idx %d --shard_num %d --directory %s \
         >log/server.out.%d 2>log/server.err.%d"%(
    0, 1, "/data/reddit48", i, i
  )
  p = subprocess.Popen(args=cmd, shell=True)
  server_process.append(p)

raw_input("press to start")

for i in range(5):
  run()

os.system("pkill -9 start_server -f")