from __future__ import annotations
r"""
Gera uma imagem "dashboard" para o slide "Interpretando a Saída",
alinhada ao projeto real: mostra custo total, tour (resumo) e artefatos,
usando como fundo a imagem real_solution.png (ou outra indicada).

Uso sugerido (Windows, PowerShell):
    $env:PYTHONPATH='src'
    python tools\\slide_visual_from_outputs.py `
        --input data\\real_edges.csv --nodes data\\real_nodes.csv `
        --background out\\real_solution.png --out slides\\img\\interpretando_saida.png
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Dict, Tuple, List
import networkx as nx

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.patches import FancyBboxPatch


def _format_distance_assuming_meters(total: float) -> str:
    try:
        m = float(total)
    except Exception:
        return str(total)
    if m < 1000.0:
        return f"{m:.0f} m"
    km = m / 1000.0
    return f"{km:.2f}".replace(".", ",") + " km"


def _duplicate_counts_from_tour(G, tour: List[str]) -> Dict[Tuple[str, str], int]:
    base_edges = set(frozenset((u, v)) for u, v in G.edges())
    used_counts: Dict[frozenset, int] = {}
    for a, b in zip(tour, tour[1:]):
        key = frozenset((a, b))
        if key in base_edges:
            used_counts[key] = used_counts.get(key, 0) + 1
    dup: Dict[Tuple[str, str], int] = {}
    for u, v in G.edges():
        key = frozenset((u, v))
        c = used_counts.get(key, 0)
        if c > 1:
            dup[(u, v)] = c - 1
    return dup


def ensure_src_on_path():
    here = Path(__file__).resolve()
    root = here.parents[1]
    src = root / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))


def main():
    ap = argparse.ArgumentParser(description="Compor visual de interpretação da saída para slides (Gamma)")
    ap.add_argument("--input", default="data/real_edges.csv", help="CSV u,v,w da instância")
    ap.add_argument("--nodes", default=None, help="CSV id,lat,lon (opcional, só para coerência do caso real)")
    ap.add_argument("--background", required=True, help="PNG de fundo (ex.: out/real_solution.png)")
    ap.add_argument("--out", default="slides/img/interpretando_saida.png", help="Imagem composta de saída")
    args = ap.parse_args()

    ensure_src_on_path()
    from pcc.graph_io import load_graph_from_csv
    from pcc.chinese_postman import solve_cpp_undirected

    G = load_graph_from_csv(args.input)
    # Usar apenas a maior componente conexa para evitar erro de conectividade
    if G.number_of_nodes() > 0:
        comps = list(nx.connected_components(G))
        if comps:
            biggest = max(comps, key=len)
            G = G.subgraph(biggest).copy()

    total, tour = solve_cpp_undirected(G)
    distancia_fmt = _format_distance_assuming_meters(total)
    dup_counts = _duplicate_counts_from_tour(G, tour)
    ruas_repetidas = int(sum(max(c, 0) for c in dup_counts.values()))

    # Carregar fundo (se disponível)
    bg_img = None
    bg_path = Path(args.background)
    if bg_path.exists():
        try:
            bg_img = mpimg.imread(str(bg_path))
        except Exception:
            bg_img = None

    # Figura 16:9 com margens estáveis
    from matplotlib.gridspec import GridSpec
    fig = plt.figure(figsize=(16, 9), dpi=120)
    gs = GridSpec(
        1,
        2,
        figure=fig,
        width_ratios=[1.15, 1.0],
        left=0.05,
        right=0.97,
        top=0.93,
        bottom=0.08,
        wspace=0.06,
    )
    ax_left = fig.add_subplot(gs[0, 0])
    ax_right = fig.add_subplot(gs[0, 1])

    # Fundo da esquerda
    ax_left.set_axis_off()
    ax_left.set_xlim(0, 1)
    ax_left.set_ylim(0, 1)

    # Painel com fundo suave
    panel = FancyBboxPatch((0.00, 0.00), 1.00, 1.00, boxstyle="round,pad=0.012,rounding_size=12",
                           linewidth=0.8, edgecolor="#D6E3F1", facecolor="#F6FAFF", alpha=1.0)
    ax_left.add_patch(panel)

    # Título geral
    ax_left.text(0.02, 0.98, "Interpretando a Saída", fontsize=22, color="#0f2942", weight="bold", va="top")

    def section(y_top: float, title: str, lines: List[str]) -> float:
        ax_left.text(0.03, y_top, title, fontsize=16, color="#0f2942", weight="bold", va="top")
        y = y_top - 0.06
        for ln in lines:
            ax_left.text(0.03, y, ln, fontsize=13, color="#1b3a57", va="top")
            y -= 0.05
        # separador
        ax_left.plot([0.02, 0.98], [y, y], color="#C9D8E8", lw=1.0)
        return y - 0.04

    # Seções do texto (com quebras controladas)
    y_cursor = 0.92
    y_cursor = section(y_cursor, '"Custo Total"', [
        f"Distância total percorrida: {distancia_fmt}",
        "Assumindo pesos em metros nas arestas",
    ])

    if tour:
        k = min(6, len(tour))
        head = " -> ".join(map(str, tour[:k])) + (" -> …" if len(tour) > k else "")
    else:
        head = "(vazio)"
    y_cursor = section(y_cursor, '"Tour"', [
        f"Sequência de nós (início): {head}",
        f"Ruas repetidas: {ruas_repetidas} segmento(s)",
    ])

    _ = section(y_cursor, "Artefatos Gerados", [
        "• PNG da rota visualizada (out/*.png)",
        "• TXT com sequência de nós (out/*_tour.txt)",
        "• GeoJSON/GPX (se houver coordenadas)",
    ])

    # Lado direito (imagem de fundo)
    ax_right.set_axis_off()
    if bg_img is not None:
        ax_right.imshow(bg_img, aspect='equal')
        ax_right.set_title("Caso real – caminho ótimo (vermelho)", fontsize=13, color="#0f2942")
    else:
        ax_right.text(0.5, 0.5, "Imagem não encontrada:\n" + str(bg_path), ha="center", va="center", fontsize=12)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(str(out_path))
    plt.close(fig)
    print(f"Imagem composta salva em: {out_path}")


if __name__ == "__main__":
    main()
