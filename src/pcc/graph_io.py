# filepath: src/pcc/graph_io.py
import csv
import networkx as nx

def read_graph_from_csv(path):
    """
    Lê CSV com cabeçalho u,v,w e retorna networkx.Graph com atributo 'weight'.
    """
    G = nx.Graph()
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            u = row["u"].strip()
            v = row["v"].strip()
            w = float(row.get("w", 1.0))
            G.add_edge(u, v, weight=w)
    return G
