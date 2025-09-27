# Conversor leve GeoJSON (OSM) -> CSV u,v,w (+ nodes opcional)
from __future__ import annotations
import json, csv, math, argparse
from pathlib import Path
from typing import Dict, Tuple, List, Iterable

def haversine_m(lat1, lon1, lat2, lon2) -> float:
    R = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dlmb/2)**2
    return 2 * R * math.asin(math.sqrt(a))

def line_length_m(coords: List[Tuple[float, float]]) -> float:
    if len(coords) < 2: return 0.0
    acc = 0.0
    for (lon1, lat1), (lon2, lat2) in zip(coords, coords[1:]):
        acc += haversine_m(lat1, lon1, lat2, lon2)
    return acc

def snap_key(lat: float, lon: float, step_deg: float):
    return (round(lat / step_deg), round(lon / step_deg))

def relabel_edges(features: Iterable[dict], step_deg: float = 5e-5) -> Tuple[List[Tuple[str, str, float]], Dict[str, Tuple[float, float]]]:
    idx_by_snap: Dict[Tuple[int, int], str] = {}
    accum: Dict[Tuple[int, int], Tuple[float, float, int]] = {}
    next_id = 1
    def node_label(lat: float, lon: float) -> str:
        nonlocal next_id
        k = snap_key(lat, lon, step_deg)
        if k not in idx_by_snap:
            idx_by_snap[k] = f"N{next_id}"
            accum[k] = (lat, lon, 1)
            next_id += 1
        else:
            la, lo, c = accum[k]
            accum[k] = (la + lat, lo + lon, c + 1)
        return idx_by_snap[k]
    edges: Dict[Tuple[str, str], float] = {}

    def clean_coords(coords_raw):
        # mantém apenas pares [lon, lat] numéricos
        out = []
        for c in coords_raw or []:
            if isinstance(c, (list, tuple)) and len(c) == 2:
                lon, lat = c
                if isinstance(lon, (int, float)) and isinstance(lat, (int, float)):
                    out.append((lon, lat))
        return out

    def add_edge_from_coords(coords_raw):
        coords = clean_coords(coords_raw)
        if len(coords) < 2:
            return
        lat1, lon1 = coords[0][1], coords[0][0]
        lat2, lon2 = coords[-1][1], coords[-1][0]
        u, v = node_label(lat1, lon1), node_label(lat2, lon2)
        if u == v:
            return
        w = line_length_m(coords)
        a, b = (u, v) if u < v else (v, u)
        edges[(a, b)] = edges.get((a, b), 0.0) + w

    dropped = 0
    for f in features:
        g = f.get("geometry", {}) or {}
        t = g.get("type")
        if t == "LineString":
            c = g.get("coordinates", [])
            if len([1 for x in c if isinstance(x, (list, tuple)) and len(x) == 2]) < 2:
                dropped += 1
                continue
            add_edge_from_coords(c)
        elif t == "MultiLineString":
            ok_seg = 0
            for coords in g.get("coordinates", []):
                if len([1 for x in coords if isinstance(x, (list, tuple)) and len(x) == 2]) >= 2:
                    add_edge_from_coords(coords); ok_seg += 1
            if ok_seg == 0:
                dropped += 1
        else:
            dropped += 1

    nodes_pos: Dict[str, Tuple[float, float]] = {}
    for k, nid in idx_by_snap.items():
        la, lo, c = accum[k]
        nodes_pos[nid] = (la / c, lo / c)

    if dropped:
        print(f"Aviso: {dropped} features ignoradas por coordenadas inválidas.")

    edges_list = [(u, v, w) for (u, v), w in edges.items()]
    return edges_list, nodes_pos

def _touches_bbox(coords: List[Tuple[float, float]], bbox: Tuple[float, float, float, float]) -> bool:
    minlon, minlat, maxlon, maxlat = bbox
    return any((minlon <= lon <= maxlon) and (minlat <= lat <= maxlat) for lon, lat in coords)

def main():
    ap = argparse.ArgumentParser(description="GeoJSON (LineString/MultiLineString) -> CSV u,v,w (+ nodes opcional)")
    ap.add_argument("input", nargs="?", default="data/osm_subgraph.geojson", help="GeoJSON de entrada")
    ap.add_argument("output", nargs="?", default="data/real_edges.csv", help="CSV de arestas u,v,w")
    ap.add_argument("--snap-m", type=float, default=8.0, help="Snap espacial (m) para mesclar nós próximos")
    ap.add_argument("--nodes-out", type=str, default=None, help="CSV de nós (id,lat,lon); padrão: 'real_nodes.csv'")
    ap.add_argument("--include-name-substr", type=str, default=None, help="Filtra por substrings no 'name' (separadas por vírgula)")
    ap.add_argument("--bbox", type=str, default=None, help="Filtra por bbox lon/lat: minlon,minlat,maxlon,maxlat")
    args = ap.parse_args()

    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    feats = data.get("features", [])

    subs = [s.strip().lower() for s in (args.include_name_substr or "").split(",") if s.strip()]
    bbox = None
    if args.bbox:
        parts = [float(x) for x in args.bbox.split(",")]
        if len(parts) == 4:
            bbox = (parts[0], parts[1], parts[2], parts[3])

    def filter_feats():
        filtered = []
        kept, total = 0, 0
        def coords_any_ok(geom):
            t = geom.get("type")
            if t == "LineString":
                c = geom.get("coordinates", [])
                return any(isinstance(x, (list, tuple)) and len(x) == 2 for x in c)
            if t == "MultiLineString":
                return any(any(isinstance(x, (list, tuple)) and len(x) == 2 for x in seg) for seg in geom.get("coordinates", []))
            return False
        for f in feats:
            total += 1
            g = f.get("geometry", {}) or {}
            if not coords_any_ok(g):
                continue
            if subs:
                nm = ((f.get("properties") or {}).get("name") or "").lower()
                if not any(s in nm for s in subs):
                    continue
            if bbox:
                def touches(g):
                    if g.get("type") == "LineString":
                        return _touches_bbox([tuple(x) for x in g.get("coordinates", []) if isinstance(x,(list,tuple)) and len(x)==2], bbox)
                    else:
                        return any(_touches_bbox([tuple(x) for x in seg if isinstance(x,(list,tuple)) and len(x)==2], bbox) for seg in g.get("coordinates", []))
                if not touches(g):
                    continue
            filtered.append(f); kept += 1
        return filtered, kept, total
    feats, kept, total = filter_feats()
    print(f"Features válidas: {kept}/{total}")

    step_deg = max(args.snap_m / 111320.0, 1e-6)
    edges_rows, nodes_pos = relabel_edges(feats, step_deg=step_deg)

    out_edges = Path(args.output)
    out_nodes = Path(args.nodes_out) if args.nodes_out else out_edges.with_name(out_edges.stem.replace("edges", "nodes") + ".csv")

    out_edges.parent.mkdir(parents=True, exist_ok=True)
    with open(out_edges, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["u", "v", "w"])
        for u, v, wgt in edges_rows:
            w.writerow([u, v, f"{wgt:.1f}"])

    out_nodes.parent.mkdir(parents=True, exist_ok=True)
    with open(out_nodes, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["id", "lat", "lon"])
        def num(nid: str):
            body = nid[1:] if nid and nid[0] in ("N", "n") else nid
            return int(body) if isinstance(body, str) and body.isdigit() else float("inf")
        for nid, (lat, lon) in sorted(nodes_pos.items(), key=lambda x: num(x[0])):
            w.writerow([nid, f"{lat:.7f}", f"{lon:.7f}"])

    print(f"Wrote {len(edges_rows)} edges to {out_edges}")
    print(f"Wrote {len(nodes_pos)} nodes to {out_nodes}")

if __name__ == "__main__":
    main()