import numpy as np
import networkx as nx
from scipy import stats
import pandas as pd
from pywhy_graphs.viz import draw
from dodiscover import make_context
from dodiscover.toporder import NoGAM
from dowhy.gcm.util.general import set_random_seed
from timeit import default_timer as timer

score = NoGAM()


d1 = pd.read_csv("dataset/low_scrap.csv")
d2 = pd.read_csv("dataset/high_scrap.csv")
data = d1
# data = data.sample(frac=0.4) # should have been used
stations = data.keys()

stations = [station[7:] for station in stations]
data.columns = stations
station_pairs = [(station.split("_")[0], station.split("_")[2]) for station in stations]

excluded_edges = []
for s in station_pairs:
    for t in station_pairs:
        if s[0] < t[0]:
            excluded_edges.append((str(t[0]) + "_mp_" + str(t[1]), str(s[0]) + "_mp_" + str(s[1])))

excluded_edges = nx.DiGraph(excluded_edges)
context = make_context().variables(data=data).edges(exclude=excluded_edges).build()

start = timer()
score.learn_graph(data, context)
end = timer()
print("took", end - start)

graph = score.graph_
dot_graph = draw(graph, name="DAG with (z, y) directed edge")
dot_graph.render(outfile=f"est_dag.png", format="png", cleanup=True)

A = nx.adjacency_matrix(graph).todense().astype(int)

np.savetxt(f"adj.csv", A, delimiter=",")