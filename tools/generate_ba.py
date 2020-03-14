import random
import argparse
import numpy

def random_subset(seq, m):
    targets = set()
    while len(targets) < m:
        x = random.choice(seq)
        targets.add(x)
    return targets

def gen_ba(n, m, filename):
  G = {}
    target = list(range(m))
    repeated_nodes = []
    source = m 
    while source < n:
      if source % 1000 == 0:
        print(source)
      repeated_nodes.extend(target)
      repeated_nodes.extend([source]*m)
      for d in target:
        w = random.random()
        f.write("%d %d %f\n"%(source, d, w))
        f.write("%d %d %f\n"%(d, source, w))
      target = random_subset(repeated_nodes, m)
      source += 1


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Generate a BA graph')
  parser.add_argument("n", type=int)
  parser.add_argument("m", type=int)
  parser.add_argument("filename", type=str)
  parser.add_argument("-f", "--feat_dim", type=int, default=602)
  parser.add_argument("-p", "--partition", type=int, default=1)

  args = parser.parse_args()
  gen_ba(args.n, args.m, args.filename)
