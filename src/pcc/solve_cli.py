"""
CLI do CPP (não dirigido).
Uso:
  PYTHONPATH=src python -m pcc.solve_cli --input data/example_edges.csv [--plot] [--save-tour tour.txt]
"""
from __future__ import annotations
import argparse
from typing import List, Tuple, Dict
import networkx as nx
import matplotlib.pyplot as plt
from .graph_io import load_graph_from_csv
from .chinese_postman import solve_cpp_undirected

def _build_multigraph_with_solution(G: nx.Graph) -> Tuple[float, List[str], nx.MultiGraph]:
    from .chinese_postman import (
        _assert_connected_ignoring_isolated,
        _all_pairs_shortest_paths_among,
        _minimum_weight_perfect_matching_dp,
        _duplicate_along_paths,
        _eulerian_tour_vertices,
    )
    _assert_connected_ignoring_isolated(G)
    base_cost = float(sum(d.get("weight", 1.0) for _, _, d in G.edges(data=True)))
    odd_nodes = [n for n in G.nodes if G.degree(n) % 2 == 1]
    if len(odd_nodes) == 0:
        MG = nx.MultiGraph()
        MG.add_nodes_from(G.nodes)
        for u, v, d in G.edges(data=True):
            MG.add_edge(u, v, **d)
        return base_cost, _eulerian_tour_vertices(MG), MG
    dist_mat, path_mat = _all_pairs_shortest_paths_among(G, odd_nodes)
    pairs, added_cost = _minimum_weight_perfect_matching_dp(odd_nodes, dist_mat)
    MG = _duplicate_along_paths(G, odd_nodes, pairs, path_mat)
    tour_vertices = _eulerian_tour_vertices(MG)
    return base_cost + added_cost, tour_vertices, MG

def _compute_duplicate_counts(G: nx.Graph, MG: nx.MultiGraph) -> Dict[Tuple[str, str], int]:
    dup: Dict[Tuple[str, str], int] = {}
    for u, v in G.edges():
        a, b = sorted((u, v))
        multi_count = MG.number_of_edges(u, v)
        d = max(0, multi_count - 1)
        if d > 0:
            dup[(a, b)] = d
    return dup

def main(argv: List[str] | None = None) -> None:
    p = argparse.ArgumentParser(description="Resolver o Problema do Carteiro Chinês (CPP) não dirigido.")
    p.add_argument("--input", default="data/example_edges.csv", help="CSV (u,v,w).")
    p.add_argument("--plot", action="store_true", help="Plota o grafo e destaca arestas duplicadas.")
    p.add_argument("--save-tour", dest="save_tour", default=None, help="Salvar tour em .txt")
    args = p.parse_args(argv)

    G = load_graph_from_csv(args.input)
    total, tour = solve_cpp_undirected(G)
    print(f"Total cost: {total}")
    print("Tour:", " -> ".join(map(str, tour)))

    if args.save_tour:
        with open(args.save_tour, "w", encoding="utf-8") as f:
            f.write(" -> ".join(map(str, tour)) + "\n")
        print(f"Tour salvo em: {args.save_tour}")

    if args.plot:
        total2, tour2, MG = _build_multigraph_with_solution(G)
        assert abs(total2 - total) < 1e-9
        dup_counts = _compute_duplicate_counts(G, MG)
        pos = nx.spring_layout(G, seed=42)
        plt.figure(figsize=(8, 6))
        nx.draw_networkx_nodes(G, pos, node_size=600, node_color="#f0f8ff", edgecolors="#333")
        nx.draw_networkx_labels(G, pos)
        nx.draw_networkx_edges(G, pos, edge_color="#bbb", width=2)
        nx.draw_networkx_edge_labels(G, pos, edge_labels={(u, v): f"{d['weight']}" for u, v, d in G.edges(data=True)})
        if dup_counts:
            for (a, b), c in dup_counts.items():
                nx.draw_networkx_edges(G, pos, edgelist=[(a, b)], edge_color="#e74c3c", width=2 + 1.5 * c)
            plt.plot([], [], color="#bbb", linewidth=2, label="Arestas originais")
            plt.plot([], [], color="#e74c3c", linewidth=3.5, label="Duplicadas")
            plt.legend(loc="best")
        plt.title(f"CPP – custo total = {total:.1f}")
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    main()