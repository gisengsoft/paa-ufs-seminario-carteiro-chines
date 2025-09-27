#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Problema do Carteiro Chinês (Não direccionado) - execução mínima do trabalho (Python puro)
Etapas:

1) Verifica conectividade.
2) Identifica vértices de grau ímpar.
3) Dijkstra entre vértices ímpares.
4) Emparelhamento perfeito mínimo (DP por bitmask).
5) Duplica arestas ao longo dos caminhos mínimos.
6) Constrói circuito euleriano (Hierholzer).
"""

from collections import defaultdict, deque
import heapq

class Graph:
    def __init__(self):
        self.adj = defaultdict(list)   # u -> list of (v, w, edge_id)
        self.edges = []                # list of (u, v, w)
        self._edge_id = 0

    def add_edge(self, u, v, w: float):
        assert w >= 0, "Pesos não negativos são exigidos"
        eid = self._edge_id
        self._edge_id += 1
        self.edges.append((u, v, w))
        self.adj[u].append((v, w, eid))
        self.adj[v].append((u, w, eid))

    def vertices(self):
        return list(self.adj.keys())

    def degree(self, u):
        return len(self.adj[u])

    def is_connected_ignoring_isolated(self):
        start = None
        for u in self.adj:
            if self.degree(u) > 0:
                start = u
                break
        if start is None:
            return True
        seen = set([start])
        dq = deque([start])
        while dq:
            u = dq.popleft()
            for v, _, _ in self.adj[u]:
                if v not in seen:
                    seen.add(v)
                    dq.append(v)
        for u in self.adj:
            if self.degree(u) > 0 and u not in seen:
                return False
        return True

    def dijkstra(self, src):
        dist = {src: 0.0}
        prev = {}
        pq = [(0.0, src)]
        while pq:
            d, u = heapq.heappop(pq)
            if d > dist[u]:
                continue
            for v, w, _ in self.adj[u]:
                nd = d + w
                if v not in dist or nd < dist[v]:
                    dist[v] = nd
                    prev[v] = u
                    heapq.heappush(pq, (nd, v))
        return dist, prev

    def shortest_path(self, s, t):
        dist, prev = self.dijkstra(s)
        if t not in dist:
            return float('inf'), []
        path = [t]
        while path[-1] != s:
            path.append(prev[path[-1]])
        path.reverse()
        return dist[t], path

def chinese_postman_undirected(g: Graph):
    if not g.is_connected_ignoring_isolated():
        raise ValueError("O grafo não é conexo (desconsidere vértices isolados).")

    base_cost = sum(w for (_, _, w) in g.edges)
    odd = [u for u in g.vertices() if g.degree(u) % 2 == 1]
    if len(odd) == 0:
        tour = eulerian_circuit(g)
        return base_cost, tour

    k = len(odd)
    pair_dist = [[0.0]*k for _ in range(k)]
    pair_path = [[[] for _ in range(k)] for _ in range(k)]
    for i, u in enumerate(odd):
        for j, v in enumerate(odd):
            if i < j:
                d, p = g.shortest_path(u, v)
                pair_dist[i][j] = pair_dist[j][i] = d
                pair_path[i][j] = pair_path[j][i] = p

    # DP por bitmask
    INF = 1e100
    dp = {0: 0.0}
    choice = {}
    full = (1 << k) - 1
    for mask in range(1, full+1):
        if bin(mask).count("1") % 2 == 1:
            continue
        dp[mask] = INF
        i = (mask & -mask).bit_length() - 1
        rest = mask ^ (1 << i)
        jmask = rest
        while jmask:
            j = (jmask & -jmask).bit_length() - 1
            new_mask = rest ^ (1 << j)
            cost = dp.get(new_mask, INF) + pair_dist[i][j]
            if cost < dp[mask]:
                dp[mask] = cost
                choice[mask] = (i, j, new_mask)
            jmask ^= (1 << j)

    added_cost = dp[full]

    # Reconstruir matching
    mask = full
    matched_pairs = []
    while mask:
        i, j, new_mask = choice[mask]
        matched_pairs.append((odd[i], odd[j]))
        mask = new_mask

    # Duplicar arestas ao longo das menores rotas
    multigraph = duplicate_along_paths(g, matched_pairs, pair_path, odd)

    tour = eulerian_circuit(multigraph)
    total_cost = base_cost + added_cost
    return total_cost, tour

def duplicate_along_paths(g: Graph, matched_pairs, pair_path, odd_list):
    mg = Graph()
    for u, v, w in g.edges:
        mg.add_edge(u, v, w)
    idx = {u: i for i, u in enumerate(odd_list)}
    for u, v in matched_pairs:
        i, j = idx[u], idx[v]
        path = pair_path[i][j]
        for a, b in zip(path, path[1:]):
            w = min(w for x, w, _ in g.adj[a] if x == b)
            mg.add_edge(a, b, w)
    return mg

def eulerian_circuit(g: Graph):
    adj = {u: g.adj[u][:] for u in g.adj}
    used = set()

    def get_unused_edge(u):
        while adj[u]:
            v, w, eid = adj[u].pop()
            if eid not in used:
                used.add(eid)
                for idx, (vv, ww, ee) in enumerate(adj[v]):
                    if vv == u and ee == eid:
                        adj[v].pop(idx)
                        break
                return v
        return None

    start = None
    for u in adj:
        if len(adj[u]) > 0:
            start = u
            break
    if start is None:
        return []

    stack = [start]
    circuit = []
    while stack:
        u = stack[-1]
        v = get_unused_edge(u)
        if v is not None:
            stack.append(v)
        else:
            circuit.append(stack.pop())
    circuit.reverse()
    return circuit

def example_graph():
    g = Graph()
    g.add_edge("A", "B", 2)
    g.add_edge("A", "C", 3)
    g.add_edge("B", "C", 1)
    g.add_edge("B", "D", 4)
    g.add_edge("C", "E", 2)
    g.add_edge("D", "E", 3)
    return g

def main():
    g = example_graph()
    total_cost, tour = chinese_postman_undirected(g)
    print("Problema do Carteiro Chinês (Não Direccionado)")
    print("Custo Total:", total_cost)
    print("Circuito Euleriano (sequência de vértices):")
    print(" -> ".join(map(str, tour)))

if __name__ == "__main__":
    main()
