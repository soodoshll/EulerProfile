import tf_euler
import tensorflow as tf
import config
import time
import argparse
import numpy as np
import random 

parser = argparse.ArgumentParser()
parser.add_argument('seed_num', type=int)
parser.add_argument('fanout', type=int)
parser.add_argument('steps', type=int)
parser.add_argument('duration', type=float)
args = parser.parse_args()

tf_euler.initialize_embedded_graph('reddit/48', graph_type='fast')
