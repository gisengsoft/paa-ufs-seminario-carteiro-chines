# filepath: tests/test_example.py
from src.pcc.graph_io import read_graph_from_csv
from src.pcc.chinese_postman import solve_chinese_postman

def test_example():
    G = read_graph_from_csv("data/example_edges.csv")
    base_cost = sum(d.get("weight",1.0) for u,v,d in G.edges(data=True))
    total_cost, circuit = solve_chinese_postman(G)
    assert total_cost >= base_cost
    assert len(circuit) > 0
