"""
Leitura de CSV (u,v,w) e construção do grafo networkx.
"""
from __future__ import annotations
from typing import List, Tuple
import csv, os, math
import networkx as nx
from .chinese_postman import build_graph_from_edges

def read_csv_edges(path: str) -> List[Tuple[str, str, float]]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")
    edges: List[Tuple[str, str, float]] = []
    with open(path, "r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        req = {"u", "v", "w"}
        if r.fieldnames is None or not req.issubset({h.strip() for h in r.fieldnames}):
            raise ValueError(f"CSV deve conter cabeçalho u,v,w. Encontrado: {r.fieldnames}")
        for i, row in enumerate(r, start=2):
            u = str(row["u"]).strip()
            v = str(row["v"]).strip()
            w_str = str(row["w"]).strip()
            if not u or not v:
                raise ValueError(f"Linha {i}: vértices vazios.")
            try:
                w = float(w_str)
            except Exception:
                raise ValueError(f"Linha {i}: peso inválido '{w_str}'.")
            if math.isnan(w) or w < 0:
                raise ValueError(f"Linha {i}: peso inválido '{w_str}'. Deve ser >= 0.")
            edges.append((u, v, w))
    return edges

def load_graph_from_csv(path: str) -> nx.Graph:
    return build_graph_from_edges(read_csv_edges(path))