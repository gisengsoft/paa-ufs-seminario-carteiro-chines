#!/usr/bin/env bash
set -e

# diretórios
mkdir -p src/pcc data slides tests out

# src package
cat > src/__init__.py <<'PY'
# filepath: src/__init__.py
# package marker
PY

# pacote pcc
cat > src/pcc/__init__.py <<'PY'
# filepath: src/pcc/__init__.py
__all__ = ["chinese_postman", "graph_io", "solve_cli"]
PY

cat > src/pcc/graph_io.py <<'PY'
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
PY

cat > src/pcc/chinese_postman.py <<'PY'
# filepath: src/pcc/chinese_postman.py
import networkx as nx
from itertools import combinations

def solve_chinese_postman(G):
    """
    Recebe G (networkx.Graph com 'weight') e retorna (total_cost, circuit_edges_list).
    Implementação simples: eulerização por pareamento mínimo entre nós de grau ímpar.
    """
    # custo base (soma das arestas do grafo simples)
    base_cost = sum(data.get("weight", 1.0) for u, v, data in G.edges(data=True))

    # encontrar nós de grau ímpar
    odd = [n for n, d in G.degree() if d % 2 == 1]

    MG = nx.MultiGraph(G)  # começamos com multigrafo contendo as arestas originais
    if odd:
        # distâncias entre nós ímpares
        dist = dict(nx.all_pairs_dijkstra_path_length(G, weight="weight"))
        # grafo completo com pesos = distâncias
        K = nx.Graph()
        for u, v in combinations(odd, 2):
            K.add_edge(u, v, weight=dist[u][v])
        # pareamento mínimo com peso
        matching = nx.algorithms.matching.min_weight_matching(K, maxcardinality=True, weight="weight")
        # duplicar arestas ao longo dos caminhos mínimos para cada par pareado
        for u, v in matching:
            path = nx.shortest_path(G, u, v, weight="weight")
            for a, b in zip(path, path[1:]):
                w = G[a][b].get("weight", 1.0)
                MG.add_edge(a, b, weight=w)

    # agora MG deve ser euleriano; extrair circuito de Euler
    circuit = list(nx.eulerian_circuit(MG))
    # custo total = soma de pesos das arestas no multigrafo (cada ocorrência conta)
    total_cost = sum(data.get("weight", 1.0) for u, v, data in MG.edges(data=True))
    return total_cost, circuit
PY

cat > src/pcc/solve_cli.py <<'PY'
# filepath: src/pcc/solve_cli.py
import argparse
from .graph_io import read_graph_from_csv
from .chinese_postman import solve_chinese_postman
import os

def main(argv=None):
    parser = argparse.ArgumentParser(description="Resolver o PCC a partir de um CSV u,v,w")
    parser.add_argument("--edgelist", required=True, help="Caminho para CSV com u,v,w")
    parser.add_argument("--draw", action="store_true", help="Salvar figura em out/solution.png")
    args = parser.parse_args(argv)

    G = read_graph_from_csv(args.edgelist)
    cost, circuit = solve_chinese_postman(G)
    print(f"Custo total: {cost}")
    print("Circuito (aresta por aresta):")
    for u, v in circuit:
        print(f"{u} -> {v}")

    if args.draw:
        try:
            import networkx as nx
            import matplotlib.pyplot as plt
            os.makedirs("out", exist_ok=True)
            pos = nx.spring_layout(G)
            plt.figure(figsize=(8,6))
            nx.draw(G, pos, with_labels=True, node_color="lightblue")
            nx.draw_networkx_edges(G, pos, edgelist=[(u,v) for u,v in circuit], edge_color="r", width=2)
            plt.savefig("out/solution.png")
            print("Figura salva em out/solution.png")
        except Exception as e:
            print("Erro ao gerar figura:", e)

if __name__ == "__main__":
    main()
PY

# exemplo de dados
cat > data/example_edges.csv <<'CSV'
# filepath: data/example_edges.csv
u,v,w
A,B,2
A,C,3
B,C,1
B,D,2
C,D,4
C,E,2
D,E,3
CSV

# teste mínimo
cat > tests/test_example.py <<'PY'
# filepath: tests/test_example.py
from src.pcc.graph_io import read_graph_from_csv
from src.pcc.chinese_postman import solve_chinese_postman

def test_example():
    G = read_graph_from_csv("data/example_edges.csv")
    base_cost = sum(d.get("weight",1.0) for u,v,d in G.edges(data=True))
    total_cost, circuit = solve_chinese_postman(G)
    assert total_cost >= base_cost
    assert len(circuit) > 0
PY

# Makefile
cat > Makefile <<'MK'
# filepath: Makefile
.PHONY: run test

run:
    python -m src.pcc.solve_cli --edgelist data/example_edges.csv --draw

test:
    python -m pytest -q
MK

# .gitignore
cat > .gitignore <<'GI'
# filepath: .gitignore
.venv/
__pycache__/
out/
*.pyc
*.pkl
GI

echo "Estrutura criada. Execute: git add . && git commit -m 'Criar estrutura inicial do projeto' && git push"