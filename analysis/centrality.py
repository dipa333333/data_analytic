import networkx as nx
import pandas as pd

def calculate_centrality(G):

    degree = nx.degree_centrality(G)

    betweenness = nx.betweenness_centrality(G)

    closeness = nx.closeness_centrality(G)

    data = []

    for node in G.nodes():

        data.append({
            "city": node,
            "degree": round(degree[node], 4),
            "betweenness": round(betweenness[node], 4),
            "closeness": round(closeness[node], 4)
        })

    df = pd.DataFrame(data)

    df = df.sort_values(
        by="degree",
        ascending=False
    )

    return df