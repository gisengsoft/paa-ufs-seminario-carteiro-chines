from __future__ import annotations
r"""
Gera um "card" compacto do caso real: usa a imagem existente (ex.: out/real_solution.png)
e sobrepõe um pequeno box com Custo Total, Ruas repetidas e início do Tour.

Uso (PowerShell):
  $env:PYTHONPATH='src'
  python tools\\real_card_visual.py `
    --input data\\real_edges.csv `
    --background out\\real_solution.png `
    --out slides\\img\\real_card.png
"""

import argparse
from pathlib import Path
from typing import Dict, Tuple, List
import sys

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.patches import FancyBboxPatch
import numpy as np
import networkx as nx


def ensure_src_on_path():
    root = Path(__file__).resolve().parents[1]
    src = root / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))


def _format_distance_assuming_meters(total: float) -> str:
    try:
        m = float(total)
    except Exception:
        return str(total)
    if m < 1000.0:
        return f"{m:.0f} m"
    km = m / 1000.0
    return f"{km:.2f}".replace(".", ",") + " km"


def _duplicate_counts_from_tour(G: nx.Graph, tour: List[str]) -> Dict[Tuple[str, str], int]:
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


def main():
    ap = argparse.ArgumentParser(description="Compor card compacto sobre imagem do caso real")
    ap.add_argument("--input", default="data/real_edges.csv", help="CSV u,v,w da instância real")
    ap.add_argument("--background", required=True, help="PNG de fundo (ex.: out/real_solution.png)")
    ap.add_argument("--out", default="slides/img/real_card.png", help="Imagem de saída do card")
    ap.add_argument("--corner", choices=["tl","tr","bl","br"], default="tl", help="Posição do card: top-left/right, bottom-left/right")
    args = ap.parse_args()

    ensure_src_on_path()
    from pcc.graph_io import load_graph_from_csv
    from pcc.chinese_postman import solve_cpp_undirected

    # Solver no maior componente para evitar erro de conectividade
    G = load_graph_from_csv(args.input)
    if G.number_of_nodes() > 0:
        comps = list(nx.connected_components(G))
        if comps:
            biggest = max(comps, key=len)
            G = G.subgraph(biggest).copy()
    total, tour = solve_cpp_undirected(G)
    distancia_fmt = _format_distance_assuming_meters(total)
    dup_counts = _duplicate_counts_from_tour(G, tour)
    ruas_repetidas = int(sum(max(c, 0) for c in dup_counts.values()))
    head = " -> ".join(map(str, tour[:5])) + (" -> …" if len(tour) > 5 else "") if tour else "(vazio)"

    # Fundo
    bg_path = Path(args.background)
    img = mpimg.imread(str(bg_path))
    # Garantir fundo opaco (remover alpha se existir)
    if isinstance(img, np.ndarray) and img.ndim == 3 and img.shape[2] == 4:
        rgb = img[..., :3].astype(float)
        a = img[..., 3:4].astype(float)
        # Composição sobre branco: out = a*rgb + (1-a)*1
        img = rgb * a + (1.0 - a)
    h, w = img.shape[:2]
    dpi = 150.0
    fig_w, fig_h = w / dpi, h / dpi
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=dpi)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis('off')
    ax.imshow(img, interpolation='none')

    # Card
    pad = 0.03
    card_w, card_h = 0.46, 0.22
    if args.corner in ("tl", "tr"):
        y = 1 - pad - card_h
    else:
        y = pad
    if args.corner in ("tl", "bl"):
        x = pad
    else:
        x = 1 - pad - card_w

    # sombra leve
    shadow = FancyBboxPatch((x+0.006, y-0.006), card_w, card_h,
                            boxstyle="round,pad=0.012,rounding_size=10",
                            linewidth=0, edgecolor="none", facecolor="#000000",
                            alpha=0.10, transform=ax.transAxes, zorder=9)
    ax.add_patch(shadow)

    box = FancyBboxPatch((x, y), card_w, card_h,
                         boxstyle="round,pad=0.012,rounding_size=10",
                         linewidth=1.0, edgecolor="#7FA2C3", facecolor="#FFFFFF",
                         alpha=1.0, transform=ax.transAxes, zorder=10)
    ax.add_patch(box)

    # Textos dentro do card
    tx = x + 0.02
    ty = y + card_h - 0.04
    ax.text(tx, ty, "Caso real — resumo", transform=ax.transAxes,
            fontsize=14, color="#0f2942", weight="bold", va='top', zorder=11)
    ty -= 0.055
    ax.text(tx, ty, f"Custo total: {distancia_fmt}", transform=ax.transAxes,
            fontsize=12.5, color="#1b3a57", va='top', zorder=11)
    ty -= 0.042
    ax.text(tx, ty, f"Ruas repetidas: {ruas_repetidas} segmento(s)", transform=ax.transAxes,
            fontsize=12.5, color="#1b3a57", va='top', zorder=11)
    ty -= 0.042
    ax.text(tx, ty, f"Tour (início): {head}", transform=ax.transAxes,
            fontsize=12.2, color="#1b3a57", va='top', zorder=11)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(str(out_path), facecolor='#FFFFFF')
    plt.close(fig)
    print(f"Card salvo em: {out_path}")


if __name__ == "__main__":
    main()
