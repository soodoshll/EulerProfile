import threading
import time
import config

import paramiko
import os
import utils

directory="/data/ppi_random/"
shard_num = 2

server_num = len(config.server_hosts)
server_ssh = [paramiko.SSHClient() for host in config.server_hosts]
for i in range(server_num):
  ssh = server_ssh[i]
  ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
  ssh.connect(config.server_hosts[i])

worker_num = len(config.worker_hosts)
worker_ssh = [paramiko.SSHClient() for host in config.worker_hosts]
for i in range(worker_num):
  ssh = worker_ssh[i]
  ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
  ssh.connect(config.worker_hosts[i])

start_barrier = utils.Barrier(server_num + 1)
end_barrier = utils.Barrier(server_num + 1)

worker_barrier = utils.Barrier(worker_num + 1)
consumed_time = [0 for i in range(worker_num)]

def server_thread(ssh, host_name, shard_id):
  # print host_name
  script_path = os.path.join(config.experiment_dir, "start_server.py") 
  cmd = "bash -lc \"python %s --shard_idx %d --shard_num %d --directory %s\""%(
    script_path, shard_id, shard_num, directory
  )
  stdin, stdout, stderr = ssh.exec_command(cmd, get_pty = True)
  start_barrier.wait()

  end_barrier.wait()
  ssh.close()

def worker_thread(ssh, worker_id):
  script_path = os.path.join(config.experiment_dir, "sample_test.py")
  cmd = "bash -lc \"python " + script_path + "\""
  stdin, stdout, stderr = ssh.exec_command(cmd, get_pty = True)
  output = stdout.read()
  # print output
  consumed_time[worker_id] = float(output.strip().split('\n')[-1].split(' ')[-1])
  worker_barrier.wait()

server_threads = []
for i in range(server_num):
  ssh = server_ssh[i]
  t = threading.Thread(target=server_thread, args=(ssh, config.server_hosts[i], i))
  server_threads.append(t)
  t.start()

print "start servers"
start_barrier.wait()
print "servers started"
time.sleep(2)
print "start workers"

for i in range(worker_num):
  ssh = worker_ssh[i]
  t = threading.Thread(target=worker_thread, args=(ssh, i))
  t.start()

worker_barrier.wait()

print "finish"
print consumed_time
end_barrier.wait()