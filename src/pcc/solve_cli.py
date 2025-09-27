from __future__ import annotations
"""
CLI do CPP (não dirigido) para:
- Resolver instância CSV u,v,w.
- Plotar solução (default) ou apenas o tour (style=tour).
- Exportar tour em TXT, GeoJSON e GPX (quando houver --nodes id,lat,lon).
"""
import argparse
from typing import List, Tuple, Dict, Optional
from collections import defaultdict
import os, csv, json, math
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.lines import Line2D
from .graph_io import load_graph_from_csv
from .chinese_postman import solve_cpp_undirected


class BasemapUnavailableError(RuntimeError):
    """Erro disparado quando os tiles do basemap não podem ser obtidos."""
    pass


def _group_nodes_for_labels(
    pos: Dict[str, Tuple[float, float]],
    nodes: List[str],
    decimals: int = 6,
) -> List[Tuple[List[str], Tuple[float, float]]]:
    """Agrupa nós que compartilham praticamente a mesma posição para evitar sobreposição de rótulos."""
    buckets: Dict[Tuple[int, int], List[str]] = defaultdict(list)
    for n in nodes:
        if n not in pos:
            continue
        x, y = pos[n]
        key = (round(x, decimals), round(y, decimals))
        buckets[key].append(str(n))
    groups: List[Tuple[List[str], Tuple[float, float]]] = []
    for key, members in buckets.items():
        first = members[0]
        x, y = pos[first]
        groups.append((sorted(members), (x, y)))
    return groups

def _largest_connected_component(G: nx.Graph) -> nx.Graph:
    if G.number_of_nodes() == 0:
        return G.copy()
    comps = list(nx.connected_components(G))
    if not comps:
        return G.copy()
    biggest = max(comps, key=len)
    return G.subgraph(biggest).copy()

def _export_tour_geojson(tour: List[str], pos_geo: Optional[Dict[str, Tuple[float, float]]], path: str, total: float) -> None:
    if not pos_geo:
        print("Aviso: --save-geojson requer --nodes (id,lat,lon). Ignorando.")
        return
    coords = []
    for n in tour:
        if n in pos_geo:
            lat, lon = pos_geo[n]
            coords.append([float(lon), float(lat)])  # GeoJSON: [lon, lat]
    if not coords:
        print("Aviso: sem coordenadas válidas para GeoJSON.")
        return
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    doc = {"type": "FeatureCollection",
           "features": [{"type": "Feature",
                         "properties": {"name": "CPP tour", "total_cost_m": float(total)},
                         "geometry": {"type": "LineString", "coordinates": coords}}]}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False)
    print(f"GeoJSON salvo em: {path}")

def _export_tour_gpx(tour: List[str], pos_geo: Optional[Dict[str, Tuple[float, float]]], path: str, total: float) -> None:
    if not pos_geo:
        print("Aviso: --save-gpx requer --nodes (id,lat,lon). Ignorando.")
        return
    pts = []
    for n in tour:
        if n in pos_geo:
            lat, lon = pos_geo[n]
            pts.append((lat, lon))
    if not pts:
        print("Aviso: sem coordenadas válidas para GPX.")
        return
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<gpx version="1.1" creator="pcc.solve_cli" xmlns="http://www.topografix.com/GPX/1/1">\n')
        f.write(f'  <trk><name>CPP tour (custo {total:.1f} m)</name><trkseg>\n')
        for lat, lon in pts:
            f.write(f'    <trkpt lat="{lat:.7f}" lon="{lon:.7f}"></trkpt>\n')
        f.write('  </trkseg></trk>\n</gpx>\n')
    print(f"GPX salvo em: {path}")

def _project_positions(G: nx.Graph, pos_geo: Optional[Dict[str, Tuple[float, float]]], layout_k: Optional[float]) -> Dict[str, Tuple[float, float]]:
    if not pos_geo:
        return nx.spring_layout(G, seed=42, k=layout_k) if layout_k else nx.spring_layout(G, seed=42)
    lats = [lat for n,(lat,lon) in pos_geo.items() if n in G.nodes]
    lons = [lon for n,(lat,lon) in pos_geo.items() if n in G.nodes]
    if not lats or not lons:
        return nx.spring_layout(G, seed=42, k=layout_k) if layout_k else nx.spring_layout(G, seed=42)
    lat0, lon0 = sum(lats)/len(lats), sum(lons)/len(lons)
    R, cos0 = 111320.0, math.cos(math.radians(lat0))
    pos_m = {n: ((lon-lon0)*cos0*R, (lat-lat0)*R) for n,(lat,lon) in pos_geo.items() if n in G.nodes}
    missing = [n for n in G.nodes if n not in pos_m]
    if missing:
        spring = nx.spring_layout(G, seed=42, k=layout_k) if layout_k else nx.spring_layout(G, seed=42)
        spring.update(pos_m)
        return spring
    return pos_m

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


def _draw_aligned_edge_labels(ax, pos: Dict[str, Tuple[float, float]], labels: Dict[Tuple[str, str], str],
                              font_size: int = 8, offset: float = 0.02) -> None:
    """
    Desenha rótulos de arestas com rotação alinhada ao segmento e um pequeno deslocamento
    perpendicular (offset) para melhorar a legibilidade e reduzir sobreposição.
    """
    for (u, v), text in labels.items():
        if u not in pos or v not in pos:
            continue
        x1, y1 = pos[u]
        x2, y2 = pos[v]
        mx, my = (x1 + x2) / 2.0, (y1 + y2) / 2.0
        dx, dy = x2 - x1, y2 - y1
        ang = math.degrees(math.atan2(dy, dx))
        # Normal unitária para deslocamento (perpendicular)
        nxp, nyp = -dy, dx
        norm = math.hypot(nxp, nyp) or 1.0
        mx += offset * (nxp / norm)
        my += offset * (nyp / norm)
        # Normaliza o ângulo para ficar mais horizontal
        if ang > 90:
            ang -= 180
        if ang < -90:
            ang += 180
        ax.text(
            mx,
            my,
            text,
            fontsize=font_size,
            rotation=ang,
            rotation_mode="anchor",
            ha="center",
            va="center",
            color="#34495e",
            bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="none", alpha=0.78),
            zorder=6,
        )


def _plot_with_basemap(
    G: nx.Graph,
    tour: List[str],
    pos_geo: Dict[str, Tuple[float, float]],
    total: float,
    args,
    node_size: float,
    fs_node: float,
    labels_nodes: List[str],
):
    try:
        import contextily as ctx
        import numpy as np
        from pyproj import Transformer
    except ImportError as exc:
        raise RuntimeError("O uso de --basemap requer a instalação do pacote 'contextily'.") from exc

    def _resolve_provider(path: str):
        current = ctx.providers
        for part in path.split('.'):
            if not hasattr(current, part):
                raise ValueError(f"Provider '{path}' não encontrado em contextily.providers")
            current = getattr(current, part)
        return current

    provider = _resolve_provider(args.basemap_provider)

    lats = [pos_geo[n][0] for n in G.nodes if n in pos_geo]
    lons = [pos_geo[n][1] for n in G.nodes if n in pos_geo]
    if not lats or not lons:
        raise RuntimeError("Para usar --basemap é necessário fornecer --nodes com lat/lon válidos.")

    lat_pad = max((max(lats) - min(lats)) * 0.12, 0.0015)
    lon_pad = max((max(lons) - min(lons)) * 0.12, 0.0015)
    west, east = min(lons) - lon_pad, max(lons) + lon_pad
    south, north = min(lats) - lat_pad, max(lats) + lat_pad

    try:
        img, extent = ctx.bounds2img(west, south, east, north, zoom=args.basemap_zoom, source=provider)
    except Exception as exc:
        raise BasemapUnavailableError(
            f"Falha ao obter tiles do provedor '{args.basemap_provider}'."
        ) from exc

    # Alguns provedores podem responder com imagem sólida (tiles indisponíveis).
    img_variation = float(np.std(img[..., :3])) if img.size else 0.0
    if img_variation < 28.0:
        raise BasemapUnavailableError(
            f"Tiles do provedor '{args.basemap_provider}' retornaram imagem vazia."
        )

    transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)

    fig, ax = plt.subplots(figsize=(args.fig_width, args.fig_height))
    ax.imshow(img, extent=extent, origin="upper", zorder=0)

    mercator: Dict[str, Tuple[float, float]] = {}
    for n, (lat, lon) in pos_geo.items():
        if n in G:
            x, y = transformer.transform(float(lon), float(lat))
            mercator[n] = (float(x), float(y))

    base_segments = []
    for u, v in G.edges():
        if u in mercator and v in mercator:
            base_segments.append([mercator[u], mercator[v]])
    if base_segments:
        lc_base = LineCollection(base_segments, colors="#64b5f6", linewidths=args.edge_width, alpha=max(0.05, min(1.0, args.edge_alpha)), zorder=2)
        ax.add_collection(lc_base)

    tour_segments = []
    for a, b in zip(tour, tour[1:]):
        if a in mercator and b in mercator:
            tour_segments.append([mercator[a], mercator[b]])
    if tour_segments:
        lc_tour = LineCollection(tour_segments, colors="#e74c3c", linewidths=args.edge_width * 2.4, alpha=0.95, zorder=3, capstyle="round")
        ax.add_collection(lc_tour)

    xs = [mercator[n][0] for n in G.nodes if n in mercator]
    ys = [mercator[n][1] for n in G.nodes if n in mercator]
    if xs and ys:
        ax.scatter(xs, ys, s=max(node_size * 0.9, 80), c="#fefefe", edgecolors="#253238", linewidths=1.2, zorder=4)

    label_groups = _group_nodes_for_labels(mercator, labels_nodes, decimals=2)
    for members, (x, y) in label_groups:
        text = "\n".join(members)
        ax.text(
            x,
            y,
            text,
            fontsize=max(fs_node, 9),
            color="#1f2d3d",
            ha="center",
            va="center",
            bbox=dict(boxstyle="round,pad=0.16", fc="white", ec="#607d8b", alpha=0.85),
            zorder=5,
        )

    if args.edge_labels:
        edge_lbls = {}
        for u, v, data in G.edges(data=True):
            if u in mercator and v in mercator:
                weight = data.get("weight")
                if weight is None:
                    continue
                edge_lbls[(u, v)] = f"{float(weight):.1f}"
        if edge_lbls:
            span = max(extent[1] - extent[0], extent[3] - extent[2]) or 1.0
            _draw_aligned_edge_labels(
                ax,
                mercator,
                edge_lbls,
                font_size=max(int(fs_node), 9),
                offset=span * 0.012,
            )

    start_node = tour[0] if tour else None
    if args.show_start and start_node and start_node in mercator:
        sx, sy = mercator[start_node]
        ax.scatter([sx], [sy], marker="*", s=max(node_size * 2.2, 300), c="#f4b400", edgecolors="#1f252f", linewidths=1.2, zorder=6)
        ax.text(
            sx,
            sy - max(node_size * 0.002, 30),
            "Início/Fim",
            fontsize=max(fs_node, 10),
            color="#0c1d2c",
            ha="center",
            va="top",
            bbox=dict(boxstyle="round,pad=0.14", fc="white", ec="#37474f", alpha=0.9),
            zorder=7,
        )

    ax.set_xlim(extent[0], extent[1])
    ax.set_ylim(extent[2], extent[3])
    ax.set_axis_off()
    ax.set_title(f"CPP – custo total = {total:.1f} m", fontsize=12)

    legend_handles = [
        Line2D([0], [0], color="#64b5f6", lw=3, label="Rede original"),
        Line2D([0], [0], color="#e74c3c", lw=4, label="Tour ótimo"),
    ]
    ax.legend(handles=legend_handles, loc="upper right")

    fig.tight_layout()
    return fig

def main(argv: Optional[List[str]] = None) -> None:
    p = argparse.ArgumentParser(description="Resolver o CPP (não dirigido) a partir de CSV u,v,w.")
    p.add_argument("--input", "--edgelist", dest="input", default="data/example_edges.csv", help="CSV u,v,w")
    p.add_argument("--plot", "--draw", action="store_true", help="Plota o grafo")
    p.add_argument("--save-plot", default=None, help="Salvar figura (PNG/SVG)")
    p.add_argument("--save-tour", default=None, help="Salvar tour em texto")
    p.add_argument("--nodes", dest="nodes_csv", default=None, help="CSV de nós (id,lat,lon) para plot/export")
    p.add_argument("--largest-component", action="store_true", help="Usar apenas a maior componente conexa")
    # Estilo
    p.add_argument("--style", choices=["default", "tour"], default="default", help="Estilo do gráfico: default ou tour")
    p.add_argument("--node-size", type=int, default=0, help="Tamanho dos nós (auto se 0)")
    p.add_argument("--label-size", type=int, default=0, help="Tamanho da fonte (auto se 0)")
    p.add_argument("--edge-alpha", type=float, default=0.35, help="Opacidade das arestas originais [0..1]")
    p.add_argument("--edge-width", type=float, default=2.0, help="Espessura das arestas originais")
    p.add_argument("--label-mode", choices=["all", "junctions", "odd", "endpoints", "none"], default="junctions",
                   help="Quais nós rotular: all, junctions(!=2), odd, endpoints(grau<=1), none")
    p.add_argument("--edge-labels", action="store_true", help="Exibir pesos nas arestas")
    p.add_argument("--show-start", action="store_true", help="Destacar nó inicial/final com marcador")
    p.add_argument("--layout-k", type=float, default=None, help="Força do spring_layout (maior = mais espaçado)")
    p.add_argument("--dpi", type=int, default=240, help="DPI ao salvar figura")
    p.add_argument("--fig-width", type=float, default=14.0, help="Largura (in)")
    p.add_argument("--fig-height", type=float, default=10.0, help="Altura (in)")
    p.add_argument("--basemap", action="store_true", help="Renderiza com mapa de fundo (requer --nodes e contextily)")
    p.add_argument("--basemap-provider", default="OpenStreetMap.Mapnik", help="Provider do mapa base (ctx.providers.*)")
    p.add_argument("--basemap-zoom", type=int, default=16, help="Zoom do mapa base (12-19). Padrão: 16")
    # Export geoespacial
    p.add_argument("--save-geojson", default=None, help="Exportar tour em GeoJSON (requer --nodes)")
    p.add_argument("--save-gpx", default=None, help="Exportar tour em GPX (requer --nodes)")
    args = p.parse_args(argv)

    G = load_graph_from_csv(args.input)
    if args.largest_component:
        G = _largest_connected_component(G)

    total, tour = solve_cpp_undirected(G)
    print(f"Custo Total: {total}")
    print("Tour:", " -> ".join(map(str, tour)))

    pos_geo: Optional[Dict[str, Tuple[float, float]]] = None
    if args.nodes_csv:
        try:
            pos_geo = {}
            with open(args.nodes_csv, newline="", encoding="utf-8") as f:
                r = csv.DictReader(f)
                for row in r:
                    nid, lat, lon = row.get("id"), row.get("lat"), row.get("lon")
                    if nid and lat and lon:
                        pos_geo[nid] = (float(lat), float(lon))
        except Exception as e:
            print(f"Aviso: falha ao ler --nodes: {e} (prosseguindo sem georreferência)")
            pos_geo = None

    if args.save_tour:
        os.makedirs(os.path.dirname(args.save_tour) or ".", exist_ok=True)
        with open(args.save_tour, "w", encoding="utf-8") as f:
            f.write(" -> ".join(map(str, tour)) + "\n")
        print(f"Tour salvo em: {args.save_tour}")

    if args.save_geojson:
        _export_tour_geojson(tour, pos_geo, args.save_geojson, total)
    if args.save_gpx:
        _export_tour_gpx(tour, pos_geo, args.save_gpx, total)

    if not args.plot:
        return

    pos = _project_positions(G, pos_geo, args.layout_k)
    n_nodes, n_edges = G.number_of_nodes(), G.number_of_edges()
    node_size = args.node_size if args.node_size > 0 else (520 if n_nodes <= 30 else (340 if n_nodes <= 80 else 240))
    fs_node = args.label_size if args.label_size > 0 else (10 if n_nodes <= 30 else (9 if n_nodes <= 80 else 8))

    labels_nodes = list(G.nodes())
    if args.label_mode == "none":
        labels_nodes = []
    elif args.label_mode == "odd":
        labels_nodes = [n for n in G if G.degree(n) % 2 == 1]
    elif args.label_mode == "junctions":
        labels_nodes = [n for n in G if G.degree(n) != 2]
    elif args.label_mode == "endpoints":
        labels_nodes = [n for n in G if G.degree(n) <= 1]

    if args.basemap and pos_geo:
        try:
            fig = _plot_with_basemap(G, tour, pos_geo, total, args, node_size, fs_node, labels_nodes)
        except BasemapUnavailableError as exc:
            print(f"Aviso: {exc} Renderizando sem mapa de fundo.")
        else:
            if args.save_plot:
                os.makedirs(os.path.dirname(args.save_plot) or ".", exist_ok=True)
                fig.savefig(args.save_plot, dpi=args.dpi)
                print(f"Figura salva em: {args.save_plot}")
            else:
                plt.show()
            plt.close(fig)
            return

    plt.figure(figsize=(args.fig_width, args.fig_height))

    # Estilo TOUR: apenas o caminho em vermelho, ruas em cinza claro
    if args.style == "tour":
        # base (todas as ruas)
        nx.draw_networkx_edges(G, pos, edge_color="#d0d0d0", width=max(0.8, args.edge_width*0.7), alpha=0.25)
        # tour em vermelho contínuo
        xs, ys = [], []
        for a, b in zip(tour, tour[1:]):
            if a in pos and b in pos:
                xa, ya = pos[a]
                xb, yb = pos[b]
                xs += [xa, xb, None]  # None separa segmentos
                ys += [ya, yb, None]
        plt.plot(xs, ys, color="#e74c3c", linewidth=3.5, solid_capstyle="round", alpha=0.95, label="Tour")
        # nós só em interseções
        sel = [n for n in G if G.degree(n) != 2]
        nx.draw_networkx_nodes(G.subgraph(sel), pos, node_size=node_size*0.7, node_color="#f0f8ff", edgecolors="#333")
        ax = plt.gca()
        for members, (x, y) in _group_nodes_for_labels(pos, sel if labels_nodes else [], decimals=4):
            text = "\n".join(members)
            ax.text(
                x,
                y,
                text,
                fontsize=fs_node,
                color="#1f2d3d",
                ha="center",
                va="center",
                bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="#999", alpha=0.85),
                zorder=5,
            )
        plt.legend(loc="best", frameon=True)
    else:
        # Estilo DEFAULT (mantido)
        nx.draw_networkx_nodes(G, pos, node_size=node_size, node_color="#f0f8ff", edgecolors="#333")
        if labels_nodes:
            ax = plt.gca()
            for members, (x, y) in _group_nodes_for_labels(pos, labels_nodes, decimals=4):
                text = "\n".join(members)
                ax.text(
                    x,
                    y,
                    text,
                    fontsize=fs_node,
                    color="#1f2d3d",
                    ha="center",
                    va="center",
                    bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="#999", alpha=0.85),
                    zorder=5,
                )
        nx.draw_networkx_edges(G, pos, edge_color="#c0c0c0", width=args.edge_width, alpha=max(0.0, min(1.0, args.edge_alpha)))
        if args.edge_labels:
            edge_lbls = {(u, v): f"{float(d.get('weight', 0)):.1f}" for u, v, d in G.edges(data=True)}
            _draw_aligned_edge_labels(plt.gca(), pos, edge_lbls, font_size=8, offset=0.02)
        # destacar duplicadas a partir do tour
        dup_counts = _duplicate_counts_from_tour(G, tour)
        for (a, b), c in dup_counts.items():
            nx.draw_networkx_edges(G, pos, edgelist=[(a, b)], edge_color="#e74c3c", width=3.0 + 2.0 * c)
        plt.plot([], [], color="#bbb", linewidth=args.edge_width, label="Arestas originais")
        plt.plot([], [], color="#e74c3c", linewidth=4.0, label="Duplicadas")
        plt.legend(loc="best", frameon=True)

    plt.title(f"CPP – custo total = {total:.1f} m", fontsize=11)
    ax = plt.gca()
    ax.set_aspect("equal", adjustable="datalim")
    ax.axis("off")
    plt.margins(0.06)
    plt.subplots_adjust(left=0.06, right=0.96, top=0.93, bottom=0.08)

    # Marca início/fim do tour, se solicitado
    start_node = tour[0] if tour else None
    if args.show_start and start_node and start_node in pos:
        sx, sy = pos[start_node]
        plt.scatter([sx], [sy], marker="*", s=max(node_size * 1.6, 260), c="#f39c12", edgecolors="#333", zorder=7)
        plt.text(
            sx,
            sy,
            "Início/Fim",
            fontsize=max(9, fs_node),
            color="#2c3e50",
            ha="center",
            va="bottom",
            bbox=dict(boxstyle="round,pad=0.16", fc="white", ec="#666", alpha=0.85),
            zorder=8,
        )
    if args.save_plot:
        os.makedirs(os.path.dirname(args.save_plot) or ".", exist_ok=True)
        plt.savefig(args.save_plot, dpi=args.dpi, bbox_inches=None, pad_inches=0.22)
        print(f"Figura salva em: {args.save_plot}")
    else:
        plt.show()

if __name__ == "__main__":
    main()