import sys, pathlib, pytest
ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from pcc.graph_io import load_graph_from_csv
from pcc.chinese_postman import solve_cpp_undirected

def test_example_cost_and_tour():
    G = load_graph_from_csv(str(ROOT / "data" / "example_edges.csv"))
    cost, tour = solve_cpp_undirected(G)
    assert cost == pytest.approx(16.0, abs=1e-9)
    assert len(tour) >= 2 and tour[0] == tour[-1]
    tour_edges = set(frozenset((a, b)) for a, b in zip(tour, tour[1:]))
    orig_edges = set(frozenset((u, v)) for u, v, _ in G.edges(data=True))
    assert orig_edges.issubset(tour_edges)