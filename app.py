from flask import Flask, render_template, request

from analysis.load_data import load_flight_data
from analysis.graph_builder import (
    build_graph,
    generate_network_html
)

from analysis.centrality import calculate_centrality
from analysis.shortest_path import find_shortest_path
from analysis.pricing_analysis import analyze_ticket_prices

app = Flask(__name__)

# LOAD DATA

df = load_flight_data()

# BUILD GRAPH

G = build_graph(df)

# GENERATE NETWORK HTML

generate_network_html(G)

# BASIC STATS

total_data = len(df)

total_nodes = G.number_of_nodes()

total_edges = G.number_of_edges()

# CENTRALITY

centrality_df = calculate_centrality(G)

top_centrality = centrality_df.head(10).to_dict(
    orient="records"
)

# PRICING

pricing_data = analyze_ticket_prices(df)

# CITY LIST

cities = sorted(list(G.nodes()))

# =========================
# DASHBOARD
# =========================

@app.route("/")
def dashboard():

    return render_template(
        "dashboard.html",

        total_data=total_data,
        total_nodes=total_nodes,
        total_edges=total_edges,

        pricing_data=pricing_data
    )

# =========================
# GRAPH PAGE
# =========================

@app.route("/graph")
def graph():

    return render_template(
        "graph.html"
    )

# =========================
# CENTRALITY PAGE
# =========================

@app.route("/centrality")
def centrality():

    return render_template(
        "centrality.html",

        top_centrality=top_centrality
    )

# =========================
# SHORTEST PATH PAGE
# =========================

@app.route(
    "/shortest_path",
    methods=["GET", "POST"]
)
def shortest_path():

    path_result = None

    total_cost = None

    if request.method == "POST":

        source = request.form["source"]

        target = request.form["target"]

        weight_type = request.form["weight_type"]

        try:

            path_result, total_cost = find_shortest_path(
                G,
                source,
                target,
                weight_type
            )

        except:

            path_result = ["No Path Found"]

    return render_template(
        "shortest_path.html",

        cities=cities,
        path_result=path_result,
        total_cost=total_cost
    )

# =========================
# PRICING PAGE
# =========================

@app.route("/pricing")
def pricing():

    return render_template(
        "pricing.html",

        pricing_data=pricing_data
    )

# =========================

if __name__ == "__main__":

    app.run(debug=True)