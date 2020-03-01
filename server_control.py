import threading
import time
import config

import paramiko
import os
import utils

server_num = len(config.server_hosts)
shard_num = len(config.partition_nodes_num)
server_ssh = [paramiko.SSHClient() for host in config.server_hosts]

duration = 30
clients_per_machine = 12

seed_num = 1024
fanout = 10
steps = 2

for i in range(server_num):
  ssh = server_ssh[i]
  ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
  ssh.connect(config.server_hosts[i])

def stop_server(ssh):
  cmd = "rm %s/server* ; pkill -f -9 start_server.py"%(config.log_dir)
  stdin, stdout, stderr = ssh.exec_command(cmd)
  result = stdout.read()

def start_server(ssh, host_name, shard_ids):
  stop_server(ssh)
  time.sleep(5)
  script_path = os.path.join(config.experiment_dir, "start_server.py") 
  for shard_id in shard_ids:
    print "starting server", shard_id
    cmd = "bash -lc \"python %s --shard_idx %d --shard_num %d --directory %s > %s 2> %s &\""%(
      script_path, shard_id, shard_num, config.directory, 
      config.log_dir + "/server.out." + str(shard_id),
      config.log_dir + "/server.err." + str(shard_id)
    )
    # cmd = "ls"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    # result = stdout.read()

def wait_server(ssh, shard_ids):
  for shard_id in shard_ids:
    print "waiting server", shard_id
    result = ""
    while result.find("service start") < 0:
      cmd = "tail -n 1 %s/server.err.%d"%(config.log_dir, shard_id)
      stdin, stdout, stderr = ssh.exec_command(cmd)
      result = stdout.read()

def test(ssh, node_ids):
  script_path = os.path.join(config.experiment_dir, "sample_test.py") 
  for i in range(clients_per_machine):
    cmd = "bash -lc \"python %s %d %d %d -d %f -i %d > %s 2> %s &\""%(
      script_path, seed_num, fanout, steps, duration, node_ids, 
      config.log_dir + "/client.out." + str(i),
      config.log_dir + "/client.err." + str(i)
    )
    # time.sleep(0.1)
    # cmd = "ls"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    # result = stdout.read()

def wait_client(ssh):
  results = []
  for i in range(clients_per_machine):
    result = ""
    while result.find("result") < 0:
      cmd = "tail -n 1 %s/client.out.%d"%(config.log_dir, i)
      stdin, stdout, stderr = ssh.exec_command(cmd)
      result = stdout.read()
    results.append(result)
  return results

import sys 
if len(sys.argv) > 1 and sys.argv[1] == 'start':
  partition_num_per_machine = shard_num / server_num
  for server_id in range(server_num):
    partitions = [server_id + i * server_num for i in range(partition_num_per_machine)]
    start_server(server_ssh[server_id], config.server_hosts[server_id], partitions)
    wait_server(server_ssh[server_id], partitions)
elif len(sys.argv) > 1 and sys.argv[1] == 'stop':
  for i in server_ssh:
    stop_server(i)
else:
  client_num = len(config.worker_hosts)
  client_ssh = [paramiko.SSHClient() for host in config.worker_hosts]
  for i in range(client_num):
    ssh = client_ssh[i]
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(config.server_hosts[i])
    ssh.exec_command("rm %s/client* ; pkill -f -9 sample_test.py"%(config.log_dir))
  
  client_thread = [threading.Thread(target=test, args=(client_ssh[i], i)) for i in range(client_num)]
  for t in client_thread:
    t.start()
  
  time.sleep(2)
  print "waiting for results"
  for i in range(client_num):
    machine_name = config.worker_hosts[i]
    result = wait_client(client_ssh[i])
    result = [float(x.strip().split(" ")[-1]) for x in result]
    print machine_name, sum(result)/len(result)

  for t in client_thread:
    t.join()