import networkx as nx

def find_shortest_path(G, source, target, weight_type):

    path = nx.shortest_path(
        G,
        source=source,
        target=target,
        weight=weight_type
    )

    total_cost = nx.shortest_path_length(
        G,
        source=source,
        target=target,
        weight=weight_type
    )

    return path, total_cost