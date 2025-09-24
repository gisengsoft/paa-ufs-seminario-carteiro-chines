"""
CPP não dirigido (pesos >= 0) usando networkx internamente.

Passos:
1) Verificar conectividade ignorando vértices isolados.
2) Identificar vértices de grau ímpar.
3) Distâncias de caminhos mínimos (Dijkstra).
4) Emparelhamento perfeito mínimo (DP por bitmask) – O(k^2 · 2^k).
5) Duplicar arestas ao longo dos caminhos mínimos emparelhados.
6) Gerar circuito euleriano (Hierholzer / networkx.eulerian_circuit).

Complexidades:
- Dijkstra por fonte: O(m log n)
- DP do matching: O(k^2 · 2^k)
"""
from __future__ import annotations
from typing import List, Tuple, Dict
import math
import networkx as nx

def build_graph_from_edges(edges: List[Tuple[str, str, float]]) -> nx.Graph:
    G = nx.Graph()
    for u, v, w in edges:
        w = float(w)
        if not (w >= 0) or math.isnan(w):
            raise ValueError(f"Peso inválido em ({u},{v},{w})")
        G.add_edge(str(u), str(v), weight=w)
    return G

def solve_cpp_undirected(G: nx.Graph) -> Tuple[float, List[str]]:
    _assert_connected_ignoring_isolated(G)
    base_cost = float(sum(d.get("weight", 1.0) for _, _, d in G.edges(data=True)))
    odd_nodes = [n for n in G.nodes if G.degree(n) % 2 == 1]

    if len(odd_nodes) == 0:
        MG = nx.MultiGraph()
        MG.add_nodes_from(G.nodes)
        for u, v, d in G.edges(data=True):
            MG.add_edge(u, v, **d)
        tour_vertices = _eulerian_tour_vertices(MG)
        return base_cost, tour_vertices

    dist_mat, path_mat = _all_pairs_shortest_paths_among(G, odd_nodes)
    pairs, added_cost = _minimum_weight_perfect_matching_dp(odd_nodes, dist_mat)
    MG = _duplicate_along_paths(G, odd_nodes, pairs, path_mat)
    tour_vertices = _eulerian_tour_vertices(MG)
    return base_cost + added_cost, tour_vertices

def _assert_connected_ignoring_isolated(G: nx.Graph) -> None:
    H = G.copy()
    isolates = [n for n in H.nodes if H.degree(n) == 0]
    H.remove_nodes_from(isolates)
    if H.number_of_nodes() == 0 or H.number_of_edges() == 0:
        return
    if not nx.is_connected(H):
        raise ValueError("O grafo não é conexo (ignorando vértices isolados).")

def _all_pairs_shortest_paths_among(
    G: nx.Graph, nodes: List[str]
) -> Tuple[List[List[float]], List[List[List[str]]]]:
    k = len(nodes)
    dist_mat = [[0.0] * k for _ in range(k)]
    path_mat: List[List[List[str]]] = [[[] for _ in range(k)] for _ in range(k)]
    for i, s in enumerate(nodes):
        lengths, paths = nx.single_source_dijkstra(G, s, weight="weight")
        for j, t in enumerate(nodes):
            if i == j:
                dist_mat[i][j] = 0.0
                path_mat[i][j] = [s]
            else:
                if t not in lengths:
                    raise ValueError(f"Vértice ímpar '{t}' é inalcançável a partir de '{s}'.")
                dist_mat[i][j] = float(lengths[t])
                path_mat[i][j] = list(map(str, paths[t]))
    return dist_mat, path_mat

def _minimum_weight_perfect_matching_dp(
    odd_nodes: List[str], dist_mat: List[List[float]]
) -> Tuple[List[Tuple[int, int]], float]:
    k = len(odd_nodes)
    if k % 2 != 0:
        raise ValueError("Quantidade de vértices ímpares deve ser par.")
    full = (1 << k) - 1
    memo: Dict[int, float] = {0: 0.0}
    choice: Dict[int, Tuple[int, int, int]] = {}
    def solve(mask: int) -> float:
        if mask in memo:
            return memo[mask]
        i = (mask & -mask).bit_length() - 1
        best = float("inf"); best_choice = None
        rest = mask ^ (1 << i)
        jmask = rest
        while jmask:
            j = (jmask & -jmask).bit_length() - 1
            next_mask = rest ^ (1 << j)
            cost = dist_mat[i][j] + solve(next_mask)
            if cost < best:
                best = cost
                best_choice = (i, j, next_mask)
            jmask ^= (1 << j)
        memo[mask] = best
        choice[mask] = best_choice  # type: ignore
        return best
    total_cost = solve(full)
    pairs: List[Tuple[int, int]] = []
    mask = full
    while mask:
        i, j, next_mask = choice[mask]
        pairs.append((i, j))
        mask = next_mask
    return pairs, total_cost

def _duplicate_along_paths(
    G: nx.Graph,
    odd_nodes: List[str],
    pairs: List[Tuple[int, int]],
    path_mat: List[List[List[str]]],
) -> nx.MultiGraph:
    MG = nx.MultiGraph()
    MG.add_nodes_from(G.nodes)
    for u, v, d in G.edges(data=True):
        MG.add_edge(u, v, **d)
    for i, j in pairs:
        path = path_mat[i][j]
        for a, b in zip(path, path[1:]):
            w = float(G[a][b]["weight"])
            MG.add_edge(a, b, weight=w)
    return MG

def _eulerian_tour_vertices(MG: nx.MultiGraph) -> List[str]:
    if not nx.is_eulerian(MG):
        raise ValueError("O multigrafo não é euleriano após duplicação de arestas.")
    edges = list(nx.eulerian_circuit(MG))
    if not edges:
        return []
    tour_vertices: List[str] = [edges[0][0]]
    for u, v in edges:
        tour_vertices.append(v)
    if tour_vertices and tour_vertices[0] != tour_vertices[-1]:
        tour_vertices.append(tour_vertices[0])
    return tour_vertices