import networkx as nx
import random

parser = argparse.ArgumentParser(description='Generate a ER graph')


er = nx.erdos_renyi_graph(10000, 0.15)
# for (u,v,w) in er.edges(data=True):
    # w['weight'] = random.random()
# er = nx.DiGraph(er)
# nx.write_edgelist(er, "out.txt")
