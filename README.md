# Seminário — Problema do Carteiro Chinês (PCC)

Repositório para o seminário da disciplina **Projeto e Análise de Algoritmos (PAA/UFS)** sobre o **Problema do Carteiro Chinês** (versão não dirigida). Contém código Python reprodutível, dados de exemplo, slides e instruções de execução.

---

## Objetivos
- Contextualizar o Problema do Carteiro Chinês (PCC) em grafos, abordando a roteirização e a inspeção de arestas.
- Apresentar a formulação do problema e seus objetivos.
- Explicar a solução ótima para grafos não dirigidos, utilizando **eulerização por pareamento mínimo** e **circuito de Euler**.
- Demonstrar uma implementação prática da solução em Python.

---

## Estrutura do repositório

pcc-ufs-seminario-carteiro-chines/

├── src/  
│   └── pcc/  
│       ├── __init__.py                # inicialização do pacote  
│       ├── chinese_postman.py         # algoritmo do PCC (não dirigido)  
│       ├── graph_io.py                # carregamento de grafo a partir de CSV u,v,w  
│       └── solve_cli.py               # interface de linha de comando (execução/demonstração)  
├── data/  
│   └── example_edges.csv              # instância de exemplo (u,v,w)  
├── slides/  
│   ├── seminario.md                   # slides em Markdown (Marp)  
│   └── seminario.pdf                  # PDF exportado  
├── tests/  
│   └── test_example.py                # teste mínimo do exemplo  
├── README.md                          # este arquivo  
├── requirements.txt                   # dependências (networkx, matplotlib, etc.)  
├── Makefile                           # atalhos (run, test, slides)  
└── .gitignore                         # arquivos/pastas ignorados pelo git

---

## Pré‑requisitos
- Python 3.11+  
- pip (gerenciador de pacotes do Python)

---

## Instalação (rápida)
1. Criar ambiente virtual:
   python -m venv .venv

2. Ativar:
   - Linux/macOS:
     . .venv/bin/activate
   - Windows (PowerShell):
     .venv\Scripts\Activate.ps1

3. Instalar dependências:
   pip install -r requirements.txt

Dependências principais:
- networkx~=3.3
- matplotlib~=3.9

---

## Executar o exemplo (CLI)
A interface de linha de comando (CLI) lê um arquivo CSV com as colunas u,v,w em data/example_edges.csv, resolve o PCC e imprime o custo e o circuito Euleriano. Use a opção --draw para salvar uma figura em out/solution.png.

- Usando Makefile:
  make run

- Diretamente:
  python -m pcc.solve_cli --edgelist data/example_edges.csv --draw

Saída esperada:
- Custo mínimo total da rota que cobre todas as arestas ao menos uma vez.
- Sequência de arestas do circuito euleriano após eulerização.
- Arquivo `out/solution.png` com o grafo e o circuito destacado (caso o `--draw` seja usado).

---

## Como o algoritmo funciona (resumo)
1. Verifica se o grafo é Euleriano (todos os vértices possuem grau par). Caso afirmativo, extrai o circuito de Euler.
2. Se não for Euleriano, identifica os vértices de grau ímpar.
3. Calcula as distâncias mínimas entre todos os pares de vértices ímpares e resolve o pareamento perfeito mínimo.
4. Duplica as arestas ao longo dos caminhos mínimos dos pares selecionados (eulerização).
5. No multigrafo resultante, extrai um circuito de Euler — solução ótima para grafos não dirigidos.

Arquivos relevantes:
- `src/pcc/chinese_postman.py`
- `src/pcc/solve_cli.py`
- `src/pcc/graph_io.py`

---

## Dados do exemplo
Instância de exemplo `data/example_edges.csv` (formato CSV: u,v,w)

```
u,v,w
A,B,2
A,C,3
B,C,1
B,D,2
C,D,4
C,E,2
D,E,3
```

---

## Testes
Executa um teste mínimo para garantir que:
- O custo retornado é pelo menos o custo base das arestas.
- O circuito retornado não é vazio.

- Usando Makefile:
  make test

- Diretamente:
  python -m pytest -q

---

## Slides
Slides em Markdown (Marp) e exportados para PDF.

- Editar: `slides/seminario.md`  
- Exportar PDF (Marp CLI):  
  make slides  
  ou  
  marp slides/seminario.md --pdf --allow-local-files -o slides/seminario.pdf

Sugestão de conteúdo dos Slides:

- Introdução
- Definição do problema
- Algoritmo (não dirigido)
- Exemplo prático
- Demonstração (CLI)
- Referências.

---

## Entregáveis
- Slides em PDF (`slides/`).
- Código e dados (`src/`, `data/`).
- `README.md` com instruções.
- Link do vídeo de apresentação (inserir quando disponível).

---

## Execução rápida (one‑liner)
pip install -r requirements.txt && python -m pcc.solve_cli --edgelist data/example_edges.csv --draw

---

## Autores
- Gilson Inácio da Silva  
- Ederson

## Licença
- MIT (opcional). Adicione `LICENSE` para licenciar publicamente.
