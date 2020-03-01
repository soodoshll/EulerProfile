import threading
import time
import config

import paramiko
import os
import utils

server_num = len(config.server_hosts)
shard_num = server_num
# server_ssh = [paramiko.SSHClient() for host in config.server_hosts]
# for i in range(server_num):
#   ssh = server_ssh[i]
#   ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#   ssh.connect(config.server_hosts[i])

worker_num = len(config.worker_hosts)
worker_ssh = [paramiko.SSHClient() for host in config.worker_hosts]
for i in range(worker_num):
  ssh = worker_ssh[i]
  ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
  ssh.connect(config.worker_hosts[i])

# start_barrier = utils.Barrier(server_num + 1)
# end_barrier = utils.Barrier(server_num + 1)


def server_thread(ssh, host_name, shard_id):
  # print host_name
  script_path = os.path.join(config.experiment_dir, "start_server.py") 
  cmd = "bash -lc \"python %s --shard_idx %d --shard_num %d --directory %s > %s 2> %s\""%(
    script_path, shard_id, shard_num, directory, config.log_dir + "/out.server." + str(host_name),
    config.log_dir + "/err.server." + str(host_name)
  )
  stdin, stdout, stderr = ssh.exec_command(cmd, get_pty = True)
  start_barrier.wait()

  end_barrier.wait()
  ssh.close()

def worker_thread(ssh, worker_id, seed_num, fanout, steps):
  script_path = os.path.join(config.experiment_dir, "sample_test.py")
  cmd = "bash -lc \"python %s --seed_num %d --fanout %d --steps %d --mode multihop 2> %s\""%(
    script_path,
    seed_num, fanout, steps,
    config.log_dir + "/err.worker." + str(worker_id)
  )
  stdin, stdout, stderr = ssh.exec_command(cmd, get_pty = True)
  output = stdout.read()
  err = stderr.read()
  open(config.log_dir + "/out.worker." + str(worker_id), "w").write(output)
  # print output
  consumed_time[worker_id] = float(output.strip().split('\n')[-1].split(' ')[-1])
  worker_barrier.wait()

# server_threads = []
# for i in range(server_num):
#   ssh = server_ssh[i]
#   t = threading.Thread(target=server_thread, args=(ssh, config.server_hosts[i], i))
#   server_threads.append(t)
#   t.start()

# print "start servers"
# start_barrier.wait()
# print "servers started"
# time.sleep(5)

settings = [[64, 2, 4], [64, 2, 8], [64, 2, 16], [64, 4, 4], [64, 4, 8], [64, 8, 4], [64, 16, 4]]

for seed_num, fanout, steps in settings:
  consumed_time = [0 for i in range(worker_num)]
  worker_barrier = utils.Barrier(worker_num + 1)
  for i in range(worker_num):
    ssh = worker_ssh[i]
    t = threading.Thread(target=worker_thread, args=(ssh, i, seed_num, fanout, steps))
    t.start()
  worker_barrier.wait()
  print "seed:", seed_num, "fanout:", fanout, "steps:", steps
  print consumed_time
  

# end_barrier.wait()