# Conversor leve GeoJSON (OSM) -> CSV u,v,w

from __future__ import annotations
import json, csv, math, sys, argparse
from pathlib import Path

def haversine_m(lat1, lon1, lat2, lon2) -> float:
    R = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dlmb/2)**2
    return 2 * R * math.asin(math.sqrt(a))

def line_length_m(coords) -> float:
    return sum(haversine_m(lat1, lon1, lat2, lon2)
               for (lon1, lat1), (lon2, lat2) in zip(coords, coords[1:]))

def snap_key(lat, lon, step_deg: float):
    # step_deg ~ 4.5e-5 ≈ 5 m; aproximado para latitudes tropicais
    return (round(lat / step_deg), round(lon / step_deg))

def relabel_edges(features, step_deg: float = 5e-5):
    # rotula nós como N1, N2... (extremidades de cada LineString) e consolida arestas paralelas
    idx_by_snap: dict[tuple[int, int], str] = {}
    next_id = 1
    def node_label(lat, lon):
        nonlocal next_id
        k = snap_key(lat, lon, step_deg)
        if k not in idx_by_snap:
            idx_by_snap[k] = f"N{next_id}"
            next_id += 1
        return idx_by_snap[k]
    edges: dict[tuple[str, str], float] = {}
    def add_edge_from_coords(coords):
        nonlocal edges
        if len(coords) < 2:
            return
        (lonA, latA), (lonB, latB) = coords[0], coords[-1]
        u, v = node_label(latA, lonA), node_label(latB, lonB)
        if u == v:
            return
        w = round(line_length_m(coords), 1)
        key = tuple(sorted((u, v)))
        edges[key] = min(w, edges.get(key, w))

    for f in features:
        g = f.get("geometry", {})
        t = g.get("type")
        if t == "LineString":
            add_edge_from_coords(g.get("coordinates", []))
        elif t == "MultiLineString":
            for coords in g.get("coordinates", []):
                add_edge_from_coords(coords)

    return [(u, v, w) for (u, v), w in edges.items()]

def main():
    ap = argparse.ArgumentParser(description="GeoJSON (OSM) -> CSV u,v,w")
    ap.add_argument("input", nargs="?", default="data/osm_subgraph.geojson", help="GeoJSON de entrada")
    ap.add_argument("output", nargs="?", default="data/real_edges.csv", help="CSV de saída u,v,w")
    ap.add_argument("--snap-m", type=float, default=5.0, help="tolerância de junção de nós (metros)")
    args = ap.parse_args()

    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    feats = data.get("features", [])

    # passo angular aproximado (latitude ~ metros/111320)
    step_deg = max(args.snap_m / 111320.0, 1e-6)
    rows = relabel_edges(feats, step_deg=step_deg)

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["u", "v", "w"])
        w.writerows(rows)
    print(f"Wrote {len(rows)} edges to {args.output}")

if __name__ == "__main__":
    main()
