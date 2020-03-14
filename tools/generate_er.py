import random
import argparse

def gen_er(n, p, filename):
  with open(filename, "w") as f:
    for i in range(0, n):
      if i % 1000 == 0 :
        print(i)
      for j in range(i+1, n):
        if random.random() < p:
          w = random.random()
          f.write("%d %d %f\n"%(i, j, w))
          f.write("%d %d %f\n"%(j, i, w))

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Generate a ER graph')
  parser.add_argument("n", type=int)
  parser.add_argument("p", type=float)
  parser.add_argument("filename", type=str)
  args = parser.parse_args()
  gen_er(args.n, args.p, args.filename)
