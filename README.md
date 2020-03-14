This is some profiling script for the Euler graph computing system.

### Usage

1. Download reddit dataset and put it in the directory `reddit`.
1. Run `convert_reddit.py` to convert the dataset into Euler format.
1. Put the dataset (`.dat` files) into HDFS.
1. Use `start_server.py` to start a server.  
1. Use `sample_test.py` to run the test.

### Distributed setting

1. Run `python server_control.py start` to start servers.
1. Run `python server_control.py test` to run profiling.
1. Run `python server_control.py stop` to stop servers.

**local experiment**

1. `python server_control.py start -p local` to start server processes.
1. `python server_control.py test -p local` to run profiling.

**metis partition**

1. `python server_control.py start -p metis` to start server processes.
1. `python server_control.py test -p metis` to run profiling.

### Partition

- See `partition.py`
- It has to be run under python3 environment with networkx-metis.