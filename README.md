This is some profiling script for the Euler graph computing system.

### Usage

1. Download reddit dataset and put it in the directory `reddit`.
1. Run `convert_reddit.py` to convert the dataset into Euler format.
1. Put the dataset (`.dat` files) into HDFS.
1. Use `start_server.py` to start a server.  
1. Use `sample_test.py` to run the test.


### TODO

1. Run metis partition before converting
