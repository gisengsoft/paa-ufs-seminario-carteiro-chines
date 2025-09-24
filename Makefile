.PHONY: install run plot test slides clean

install:
	python -m pip install -r requirements.txt

run:
	PYTHONPATH=src python -m pcc.solve_cli --input data/example_edges.csv

plot:
	PYTHONPATH=src python -m pcc.solve_cli --input data/example_edges.csv --plot

test:
	pytest -q

slides:
	npx @marp-team/marp-cli slides/seminario.md -o slides/seminario.pdf

clean:
	rm -rf __pycache__ */__pycache__ .pytest_cache .mypy_cache *.pyc *.pyo *.pyd *.tmp *.log .coverage dist build *.egg-info
