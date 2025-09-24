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
