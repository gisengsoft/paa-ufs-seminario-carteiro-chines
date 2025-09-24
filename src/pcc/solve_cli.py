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
