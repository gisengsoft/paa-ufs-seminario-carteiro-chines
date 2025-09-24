# filepath: Makefile
.PHONY: run test

run:
    python -m src.pcc.solve_cli --edgelist data/example_edges.csv --draw

test:
    python -m pytest -q
