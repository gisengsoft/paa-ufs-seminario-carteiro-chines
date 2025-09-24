Como executar no VS Code (PowerShell)

Selecionar interpretador da venv (Ctrl+Shift+P → Python: Select Interpreter).
Ativar venv e instalar:
python -m venv .venv
. Activate.ps1
pip install -r requirements.txt
Rodar a CLI:
$env:PYTHONPATH="src"; python -m pcc.solve_cli --input example_edges.csv --plot
Testes:
python -m pytest -q
Se preferir usar seu script isolado atual, rode: python .\cpp_solver.py.
