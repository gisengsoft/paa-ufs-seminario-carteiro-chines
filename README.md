# Seminário — Problema do Carteiro Chinês (PCC)

Repositório para o seminário da disciplina **Projeto e Análise de Algoritmos (PAA/UFS)** sobre o **Problema do Carteiro Chinês** (versão não dirigida). Contém código Python reprodutível, dados de exemplo, slides e instruções de execução.

---

## Objetivos

- Contextualizar o Problema do Carteiro Chinês (PCC) em grafos, abordando a roteirização e a inspeção de arestas.
- Apresentar a formulação do problema e seus objetivos.
- Explicar a solução ótima para grafos não dirigidos, utilizando eulerização por pareamento mínimo e circuito de Euler.
- Demonstrar uma implementação prática da solução em Python com exemplo executável.

---

## Estrutura do repositório

<pre>
pcc-ufs-seminario-carteiro-chines/
├── src/
│   └── pcc/
│       ├── __init__.py
│       ├── chinese_postman.py        # algoritmo do PCC (não dirigido)
│       ├── graph_io.py               # leitura de CSV u,v,w
│       └── solve_cli.py              # CLI (execução e desenho opcional)
├── data/
│   ├── example_edges.csv             # instância didática
│   └── real_edges.csv                # instância real (Atalaia) – opcional
├── slides/
│   ├── seminario.md                  # slides (Marp)
│   └── seminario.pdf                 # slides exportados
├── tests/
│   └── test_example.py               # teste mínimo do exemplo
├── tools/
│   └── geojson_to_csv.py             # conversor GeoJSON → CSV u,v,w (leve)
├── README.md
├── requirements.txt                  # networkx, matplotlib
├── Makefile                          # atalhos (run, test, slides)
└── .gitignore
</pre>

---

## Pré‑requisitos

- Python 3.11+ instalado.

---

## Instalação

Crie e ative um ambiente virtual e instale as dependências:

python -m venv .venv
# Linux/macOS
. .venv/bin/activate
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

Dependências principais:

networkx~=3.3
matplotlib~=3.9

---

## Executar o exemplo (didático)

A CLI lê um CSV `u,v,w` em `data/example_edges.csv`, resolve o PCC e imprime custo e circuito; com `--draw`, salva `out/solution.png`.

# Usando Makefile
make run
# Diretamente
python -m pcc.solve_cli --edgelist data/example_edges.csv --draw

Saída esperada:
- Custo mínimo total para cobrir todas as arestas ao menos uma vez.
- Sequência de arestas do circuito euleriano após eulerização.
- Figura em `out/solution.png` com o circuito destacado (se `--draw`).

---

## Como o algoritmo funciona (resumo)

1. Verifica se o grafo é euleriano (todos os graus pares); se sim, extrai circuito de Euler.
2. Caso contrário, identifica os vértices de grau ímpar.
3. Calcula distâncias mínimas entre os vértices ímpares.
4. Resolve o pareamento perfeito mínimo entre ímpares e duplica os caminhos escolhidos.
5. Extrai um circuito de Euler no multigrafo eulerizado (solução ótima no caso não dirigido).

Arquivos:
- `src/pcc/chinese_postman.py` — implementação.
- `src/pcc/solve_cli.py` — orquestração e desenho.
- `src/pcc/graph_io.py` — leitura do CSV.

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

## Exemplo ilustrativo

Abaixo está um exemplo gráfico do **Problema do Carteiro Chinês** aplicado a um grafo simplificado (um “bairro” com 5 esquinas A–E).

- Vértices representam esquinas.
- Arestas representam ruas, com pesos equivalentes a distâncias.
- O caminho ótimo encontrado pelo algoritmo está destacado em **vermelho**.

![Exemplo do Problema do Carteiro Chinês](pcc_exemplo.png)

---

## Estudo de caso real (Bairro Atalaia) - comandos

# 1) converter GeoJSON -> CSV
python tools/geojson_to_csv.py data/osm_subgraph.geojson data/real_edges.csv
# 2) Resolva e gere a imagem da rota
python -m pcc.solve_cli --edgelist data/real_edges.csv --draw

# 3) Fluxo leve sem libs pesadas:
No site Overpass Turbo, consulte as ruas da Atalaia (ex.: `highway=residential in "Atalaia, Aracaju"`), execute e exporte GeoJSON.  

Inclua a figura e o custo nos slides, citando a fonte OSM (ver seção de créditos abaixo).

---

## Testes

pytest -q
# ou
make test

---

## Slides

make slides
# ou:
marp slides/seminario.md --pdf --allow-local-files -o slides/seminario.pdf


## Sugestão de roteiro: 

Introdução → Problema → Algoritmo → Exemplo → Estudo de caso → Demonstração → Referências.

---

## Entregáveis do seminário

- Slides em PDF com explicação do problema, do algoritmo e do exemplo real.
- Código e dados reprodutíveis (este repositório).
- Demonstração funcional (CLI).
- README com instruções e link do vídeo.

---

## Vídeo da apresentação

- Link do YouTube: INSERIR AQUI.

---

## Licença do código

- MIT (se optar por licenciar publicamente). Adicione o arquivo `LICENSE` com o texto da MIT License.

---

## Créditos e licença de dados (OSM)

Este projeto utiliza recortes de vias da região do bairro Atalaia, Aracaju, SE, obtidos via Overpass Turbo a partir do OpenStreetMap.  
- Atribuição: “Map data © OpenStreetMap contributors”.  
- Licença dos dados: Open Database License (ODbL 1.0).  
- Referências oficiais:
  - Copyright e Atribuição (OSM): https://www.openstreetmap.org/copyright
  - Diretrizes de Atribuição (OSMF): https://osmfoundation.org/wiki/Licence/Attribution_Guidelines
  - Texto da ODbL 1.0: https://opendatacommons.org/licenses/odbl/1-0/

**Observação**: ao exibir mapas/rotas nos slides, inclua um rodapé do tipo “Map data © OpenStreetMap contributors, ODbL 1.0” na(s) lâmina(s) que mostram a figura ou em uma lâmina de créditos visível.

---

## Referências

- Materiais de teoria de grafos (caminhos eulerianos, emparelhamento mínimo) e literatura sobre roteamento por arestas.
- Documentação do NetworkX (funções de eulerian circuit, matching e caminhos mínimos).
- Overpass Turbo para extração de subgrafos do OpenStreetMap.
B,C,1
B,D,2
C,D,4
C,E,2
D,E,3






