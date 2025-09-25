# Seminário — Problema do Carteiro Chinês (PCC)

Repositório para o seminário da disciplina **Projeto e Análise de Algoritmos (PAA/UFS)** sobre o **Problema do Carteiro Chinês** (versão não dirigida). Contém código Python reprodutível, dados de exemplo, slides e instruções de execução.

---

## Objetivos

- Contextualizar o Problema do Carteiro Chinês (PCC) em grafos, abordando a roteirização e a inspeção de arestas.
- Apresentar a formulação do problema e seus objetivos.
- Explicar a solução **ótima** para grafos não dirigidos, via eulerização por pareamento mínimo + circuito de Euler.
- Demonstrar uma implementação prática da solução em Python com exemplo executável.

---

## Estrutura do repositório

```text
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
├── requirements.txt                  # networkx, matplotlib, pytest
├── Makefile                          # atalhos (run, test, slides)
└── .gitignore
```

## Pré-requisitos

- Python 3.10+ (ou superior compatível)
- (Opcional) Node.js para gerar slides com Marp CLI

---

## Instalação

```bash
python -m venv .venv
# Linux/macOS
. .venv/bin/activate
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

**Dependências principais**: `networkx`, `matplotlib`, `pytest`.

---

## Executar o exemplo (didático)

O CSV didático está em `data/example_edges.csv`:

```csv
u,v,w
A,B,2
A,C,3
B,C,1
B,D,4
C,E,2
D,E,3
```

### Via Makefile

```bash
make run
# ou:
make test
```

### Diretamente (sem Make)

```bash
python -m pcc.solve_cli --input data/example_edges.csv
python -m pcc.solve_cli --input data/example_edges.csv --plot
# opcional: salvar o tour em arquivo texto
python -m pcc.solve_cli --input data/example_edges.csv --save-tour data/example_tour.txt
```

**Saída esperada**:

- `Total cost: 16.0`
- `Tour: ...` (um circuito fechado; a ordem pode variar)  
  Com `--plot`, abre uma figura e **destaca as arestas duplicadas** (tracejado/espessura maior).

---

## Como o algoritmo funciona (resumo)

1. Verifica se o grafo é euleriano (todos os graus pares) → se sim, extrai circuito de Euler.
2. Caso contrário, identifica os vértices de **grau ímpar**.
3. Calcula **distâncias mínimas** entre os vértices ímpares (Dijkstra).
4. Resolve o **pareamento perfeito mínimo** entre ímpares (DP por bitmask) e **duplica** os caminhos escolhidos.
5. Extrai um **circuito de Euler** no multigrafo eulerizado (solução **ótima** no caso não dirigido).

Arquivos:

- `src/pcc/chinese_postman.py` — implementação
- `src/pcc/solve_cli.py` — orquestração/CLI e plot
- `src/pcc/graph_io.py` — leitura do CSV `u,v,w`

---

## Estudo de caso real (Bairro Atalaia)

1. Obtenha um subgrafo de vias (Overpass/OSM) em **GeoJSON** (LineString/MultiLineString).
2. Converta para `u,v,w` com o conversor leve:

```bash
python tools/geojson_to_csv.py data/osm_subgraph.geojson data/real_edges.csv
```

3. Resolva e visualize:

```bash
python -m pcc.solve_cli --input data/real_edges.csv --plot --save-tour data/real_tour.txt
```

> Dica: inclua nos slides a imagem da rota e o custo total.

---

## Testes

```bash
pytest -q
```

O teste `tests/test_example.py` confere **custo ~16** e se o tour é **fechado** e **cobre** todas as arestas.

---

## Slides (Marp)

```bash
# usando npx (sem instalar globalmente)
npx @marp-team/marp-cli slides/seminario.md -o slides/seminario.pdf

# ou instalar global e usar:
npm i -g @marp-team/marp-cli
marp slides/seminario.md --pdf -o slides/seminario.pdf
```

---

## Exemplo ilustrativo

Abaixo está um exemplo gráfico do **Problema do Carteiro Chinês** aplicado a um grafo simplificado (um “bairro” com 5 esquinas A–E).

- Vértices representam esquinas.
- Arestas representam ruas, com pesos equivalentes a distâncias.
- O caminho ótimo encontrado pelo algoritmo está destacado em **vermelho**.

![Exemplo do Problema do Carteiro Chinês](pcc_exemplo.png)

---

## Entregáveis do seminário

- Slides em PDF (explicação do problema, do algoritmo e do exemplo real)
- Código e dados reprodutíveis (este repositório)
- Demonstração funcional (CLI)
- README com instruções e link do vídeo (inserir quando disponível)

---

## Vídeo da apresentação

- Link do YouTube: **INSERIR AQUI**

---

## Licença do código

- MIT (adicionar arquivo `LICENSE` se optar por essa licença)

---

## Créditos e licença de dados (OSM)

Este projeto pode utilizar recortes de vias obtidos via Overpass Turbo a partir do OpenStreetMap.

- Atribuição: “Map data © OpenStreetMap contributors”
- Licença dos dados: **Open Database License (ODbL 1.0)**
- Referências:
  - https://www.openstreetmap.org/copyright
  - https://osmfoundation.org/wiki/Licence/Attribution_Guidelines
  - https://opendatacommons.org/licenses/odbl/1-0/

> Ao exibir mapas/rotas nos slides, inclua um rodapé com:  
> “Map data © OpenStreetMap contributors, ODbL 1.0”.

---

## Autores

- Gilson Inácio da Silva
- Ederson Manoel de Oliveira
