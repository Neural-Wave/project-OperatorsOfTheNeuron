import numpy as np
import pandas as pd
import networkx as nx
from dowhy import gcm

special = "Station5_mp_85"

low_data = pd.read_csv("res/low_scrap.csv")
high_data = pd.read_csv("res/high_scrap.csv")

# average value of special
special_avg_low = low_data[special].mean()
special_avg_high = high_data[special].mean()
print(special_avg_low, special_avg_high)

adjmat = pd.read_csv("res/our_dag.csv", header=None)
adjmat = adjmat.to_numpy()

dag = nx.DiGraph()
dag.add_nodes_from(low_data.columns)

# add edges to graph
for i in range(len(adjmat)):
    for j in range(len(adjmat[i])):
        if adjmat[i][j] == 1:
            dag.add_edge(low_data.columns[i], low_data.columns[j])


# Step 1: Model our system:
causal_model = gcm.StructuralCausalModel(dag)
gcm.auto.assign_causal_mechanisms(causal_model, low_data)

# Step 2: Train our causal model with the data from above:
gcm.fit(causal_model, low_data)

anomaly_attribution = gcm.attribute_anomalies(causal_model, special, high_data)

import pickle
pickle.dump(anomaly_attribution, open("out/anomaly_attribution_our.pkl", "wb"))
