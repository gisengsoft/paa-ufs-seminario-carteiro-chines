**Universidade Federal de Sergipe (UFS)**  
**Departamento de Computação (DCOMP)**  
**Programa de Pós-Graduação em Ciência da Computação (PROCC)**  

📚 **Disciplina:** Projeto e Análise de Algoritmos  
👨‍🏫 **Professor:** Leonardo Matos  

## Alunos:

- Gilson Inácio da Silva
- Ederson Manoel de Oliveira


# Seminário — Problema do Carteiro Chinês (PCC)

Repositório do seminário da disciplina PAA/UFS sobre o Problema do Carteiro Chinês (CPP) em grafos não dirigidos. Traz implementação em Python, dados de exemplo, conversor GeoJSON→CSV, testes e slides.

---

## Apresentação (vídeo)

- YouTube: [APRESENTACAO PROBLEMA CARTEIRO CHINES](https://youtu.be/q0n0M7dWr60)
- Slides (PDF): [slides/seminario.pdf](slides/seminario.pdf)

<!-- Se quiser uma miniatura clicável, substitua VIDEO_ID e descomente:
[![Assistir no YouTube](https://img.youtube.com/vi/VIDEO_ID/hqdefault.jpg)](https://youtu.be/VIDEO_ID)
-->

---

Try it (rápido)

- Quer ver funcionando em 1 minuto? Vá direto para o [Quickstart](#quickstart).

---

## Objetivos

- Contextualizar o problema e aplicações (coleta de lixo, varrição, leitura de medidores etc.).
- Explicar a solução ótima para grafos não dirigidos (eulerização via matching mínimo + circuito de Euler).
- Disponibilizar uma CLI reprodutível, dados e slides para demonstração.

---

## Estrutura do projeto (pastas e arquivos)

Visão geral da árvore de diretórios para navegação rápida.

```text
.
├─ README.md
├─ requirements.txt
├─ Makefile
├─ make.ps1
├─ pcc_exemplo.png
├─ cpp_solver.py
├─ cpp_seminar_script.md
├─ data/
│  ├─ example_edges.csv
│  ├─ real_edges.csv
│  ├─ real_nodes.csv
│  └─ osm_subgraph.geojson
├─ src/
│  └─ pcc/
│     ├─ __init__.py
│     ├─ chinese_postman.py
│     ├─ graph_io.py
│     └─ solve_cli.py
├─ tools/
│  └─ geojson_to_csv.py
├─ tests/
│  └─ test_example.py
├─ slides/
│  ├─ seminario.pdf
│  └─ img/
│     ├─ example.png
│     ├─ real_solution.png
│     └─ real_solution_basemap.png
└─ out/   (artefatos gerados: PNG, TXT, GeoJSON, GPX)
```

Referências rápidas:

- Núcleo do algoritmo: `src/pcc/chinese_postman.py` → `solve_cpp_undirected`
- CLI/plot/export: `src/pcc/solve_cli.py` → `main`
- Leitura de CSV: `src/pcc/graph_io.py` → `load_graph_from_csv`
- Conversor OSM→CSV: `tools/geojson_to_csv.py`
- Dados de exemplo/real: `data/`
- Automação de tarefas: `Makefile` e `make.ps1`
- Slides e imagens: `slides/` (PDF e figuras)
- Testes: `tests/test_example.py`

Observação: a pasta `out/` é recriada pelos comandos/targets e não precisa ser versionada.

---

## Estrutura do repositório

```powershell
python tools\geojson_to_csv.py data\osm_subgraph.geojson data\real_edges.csv --snap-m 12 --nodes-out data\real_nodes.csv --bbox "-37.0628,-10.9496,-37.0564,-10.9435"
```

```bash
python tools/geojson_to_csv.py data/osm_subgraph.geojson data/real_edges.csv --snap-m 12 --nodes-out data/real_nodes.csv --bbox "-37.0628,-10.9496,-37.0564,-10.9435"
```

2a) Resolver (visual “limpo”, sem mapa):

Windows (PowerShell)

```powershell
$env:PYTHONPATH="src"
python -m pcc.solve_cli --input data\real_edges.csv --nodes data\real_nodes.csv --largest-component --plot `
  --label-mode endpoints --show-start --edge-alpha 0.32 --edge-width 2.9 --fig-width 12 --fig-height 9 --dpi 320 `
  --save-plot out\real_solution.png --save-tour out\real_tour.txt `
  --save-geojson out\real_tour.geojson --save-gpx out\real_tour.gpx
```

Linux/macOS

```bash
PYTHONPATH=src python -m pcc.solve_cli --input data/real_edges.csv --nodes data/real_nodes.csv --largest-component --plot \
  --label-mode endpoints --show-start --edge-alpha 0.32 --edge-width 2.9 --fig-width 12 --fig-height 9 --dpi 320 \
  --save-plot out/real_solution.png --save-tour out/real_tour.txt \
  --save-geojson out/real_tour.geojson --save-gpx out/real_tour.gpx
```

2b) Com mapa de fundo (OpenStreetMap via contextily):

```powershell
$env:PYTHONPATH="src"
python -m pcc.solve_cli --input data\real_edges.csv --nodes data\real_nodes.csv --largest-component --plot `
  --style tour --basemap --basemap-provider CartoDB.Positron --basemap-zoom 17 `
  --label-mode endpoints --show-start --edge-alpha 0.55 --edge-width 3.4 --fig-width 13 --fig-height 9.5 --dpi 320 `
  --save-plot out\real_solution_basemap.png --save-tour out\real_tour.txt
```

```bash
PYTHONPATH=src python -m pcc.solve_cli --input data/real_edges.csv --nodes data/real_nodes.csv --largest-component --plot \
  --style tour --basemap --basemap-provider CartoDB.Positron --basemap-zoom 17 \
  --label-mode endpoints --show-start --edge-alpha 0.55 --edge-width 3.4 --fig-width 13 --fig-height 9.5 --dpi 320 \
  --save-plot out/real_solution_basemap.png --save-tour out/real_tour.txt
```

## Pré‑requisitos

- Python 3.10+ (recomendado 3.11/3.12)
- (Opcional) Node.js para exportar slides com Marp

---

## Quickstart

Windows (PowerShell)

```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:PYTHONPATH="src"
python -m pcc.solve_cli --input data\example_edges.csv --plot --save-plot out\example.png --save-tour out\example_tour.txt
```

Se o PowerShell não propagar `PYTHONPATH`, use o cmd como alternativa:

```powershell
cmd /d /c "set PYTHONPATH=src&& python -m pcc.solve_cli --input data\example_edges.csv"
```

Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=src python -m pcc.solve_cli --input data/example_edges.csv --plot --save-plot out/example.png --save-tour out/example_tour.txt
```

Windows (com make.ps1)

```powershell
.\make.ps1 install
.\make.ps1 run
\.\make.ps1 plot        # salva out\example.png/out\example_tour.txt e copia a imagem para slides\img\example.png
\.\make.ps1 real        # recorte Jardins (sem mapa), gera PNG/TXT/GeoJSON/GPX e copia para slides\img\real_solution.png
\.\make.ps1 real-basemap # recorte Jardins com mapa OSM e estilo tour (requer contextily/pyproj)
.\make.ps1 test
```

---

## Instalação

Windows (PowerShell)

```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Executar o exemplo (didático)

CSV de exemplo (data/example_edges.csv):

```csv
u,v,w
A,B,2
A,C,3
B,C,1
B,D,4
C,E,2
D,E,3
```

Nota sobre pesos (w)

- A coluna `w` representa o custo da aresta e deve ser não negativa.
- Se você usar o conversor `tools/geojson_to_csv.py`, `w` será a distância geodésica em metros.
- Você pode usar outras unidades (km, tempo, custo monetário); apenas mantenha a unidade consistente — o algoritmo minimiza a soma dos pesos.

Windows (PowerShell)

```powershell
$env:PYTHONPATH="src"
python -m pcc.solve_cli --input data\example_edges.csv
python -m pcc.solve_cli --input data\example_edges.csv --plot --save-plot out\example.png --save-tour out\example_tour.txt
```

Alternativa (evita escopo de variável no PowerShell):

```powershell
cmd /d /c "set PYTHONPATH=src&& python -m pcc.solve_cli --input data\example_edges.csv --plot --save-plot out\example.png --save-tour out\example_tour.txt"
```

Linux/macOS

```bash
PYTHONPATH=src python -m pcc.solve_cli --input data/example_edges.csv
PYTHONPATH=src python -m pcc.solve_cli --input data/example_edges.csv --plot --save-plot out/example.png --save-tour out/example_tour.txt
```

Flags da CLI

- `--input` (alias: `--edgelist`): caminho do CSV `u,v,w`.
- `--plot` (alias: `--draw`): exibe/gera figura com arestas duplicadas.
- `--save-plot PATH`: salva a figura (PNG/SVG).
- `--save-tour PATH`: salva o tour (sequência de vértices) em texto.
- `--nodes PATH`: CSV de nós (`id,lat,lon`) para plot/export georreferenciado.
- `--save-geojson PATH`: exporta o tour em GeoJSON (requer `--nodes`).
- `--save-gpx PATH`: exporta o tour em GPX (requer `--nodes`).
- `--largest-component`: usa apenas o maior componente conexo (útil em dados reais desconexos).
- Estilo/legibilidade:
  - `--label-mode [all|junctions|odd|endpoints|none]` (novo: `endpoints` rotula apenas extremidades — grau ≤ 1)
  - `--edge-labels` (rótulos de peso nas arestas)
  - `--show-start` (novo: marca início/fim do tour com uma estrela)
  - `--style [default|tour]`
  - `--node-size`, `--label-size`, `--edge-alpha`, `--edge-width`, `--layout-k`, `--dpi`, `--fig-width`, `--fig-height`
  - `--basemap` (novo: sobrepõe o tour em um mapa OSM; requer `--nodes` + pacote `contextily`)
  - `--basemap-provider`, `--basemap-zoom` (opcionais – ajuste do tile provider/zoom)

Saída esperada (o tour pode variar):

```
Custo Total: 16.00
Tour: A -> C -> E -> D -> B -> C -> B -> A
Resumo: Distância total: 16 m (assumindo pesos em metros); ruas repetidas: 1 segmento(s)
```

Notas sobre a saída:

- O valor de "Custo Total" agora é exibido com 2 casas decimais para facilitar leitura.
- É impresso um "Resumo" amigável: a distância é formatada automaticamente em metros ou quilômetros
  (se os pesos representarem metros), e é informada a quantidade de segmentos de rua repetidos no tour
  (decorrentes da eulerização por duplicação de arestas).

---

## Como o algoritmo funciona (resumo)

1) Verifica conectividade (ignorando isolados) e soma o custo base.
2) Lista vértices de grau ímpar. Se não houver, extrai circuito de Euler.
3) Calcula caminhos mínimos entre ímpares (Dijkstra).
4) Emparelhamento perfeito mínimo (DP por bitmask; O(k^2·2^k)).
5) Duplica arestas dos caminhos escolhidos e extrai circuito euleriano no multigrafo.
6) Método é ótimo para grafos não dirigidos com pesos ≥ 0.

Arquivos: `src/pcc/chinese_postman.py` (solver), `src/pcc/solve_cli.py` (CLI/plot), `src/pcc/graph_io.py` (CSV).

---

## Estudo de caso real (OSM)

1) Converter GeoJSON → CSV `u,v,w` e nós (`id,lat,lon`) — ajuste `--snap-m` (em metros):
   - Observação: `tools/geojson_to_csv.py` usa apenas a biblioteca padrão do Python (sem dependências extras).

Windows (PowerShell)

```powershell
python tools\geojson_to_csv.py data\osm_subgraph.geojson data\real_edges.csv --snap-m 8 --nodes-out data\real_nodes.csv
```

Linux/macOS

```bash
python tools/geojson_to_csv.py data/osm_subgraph.geojson data/real_edges.csv --snap-m 8 --nodes-out data/real_nodes.csv
```

2) Resolver focando no maior componente, georreferenciando com `--nodes` e exportando artefatos:

Windows (PowerShell)

```powershell
$env:PYTHONPATH="src"
python -m pcc.solve_cli --input data\real_edges.csv --nodes data\real_nodes.csv --largest-component --plot `
  --save-plot out\real_solution.png --save-tour out\real_tour.txt `
  --save-geojson out\real_tour.geojson --save-gpx out\real_tour.gpx
```

Linux/macOS

```bash
PYTHONPATH=src python -m pcc.solve_cli --input data/real_edges.csv --nodes data/real_nodes.csv --largest-component --plot \
  --save-plot out/real_solution.png --save-tour out/real_tour.txt \
  --save-geojson out/real_tour.geojson --save-gpx out/real_tour.gpx
```

Observação: os alvos `plot`, `real` e `real-basemap` já copiam as imagens atualizadas para `slides/img/`.

---

## Presets de visualização (recomendados)

Grafo pequeno (rótulos completos e pesos nas arestas)

```powershell
# Windows (PowerShell)
$env:PYTHONPATH="src"
python -m pcc.solve_cli --input data\example_edges.csv --plot `
  --label-mode all --edge-labels --show-start `
  --node-size 650 --label-size 12 --edge-width 2.2 --edge-alpha 0.40 --dpi 280 `
  --save-plot out\example.png --save-tour out\example_tour.txt
```

```bash
# Linux/macOS
PYTHONPATH=src python -m pcc.solve_cli --input data/example_edges.csv --plot \
  --label-mode all --edge-labels --show-start \
  --node-size 650 --label-size 12 --edge-width 2.2 --edge-alpha 0.40 --dpi 280 \
  --save-plot out/example.png --save-tour out/example_tour.txt
```

Caso real – bairro Jardins (visual limpo, sem mapa)

```powershell
$env:PYTHONPATH="src"
python -m pcc.solve_cli --input data\real_edges.csv --nodes data\real_nodes.csv --largest-component --plot `
  --label-mode endpoints --show-start --edge-alpha 0.32 --edge-width 2.9 --fig-width 12 --fig-height 9 --dpi 320 `
  --save-plot out\real_solution.png --save-tour out\real_tour.txt
```

```bash
PYTHONPATH=src python -m pcc.solve_cli --input data/real_edges.csv --nodes data/real_nodes.csv --largest-component --plot \
  --label-mode endpoints --show-start --edge-alpha 0.32 --edge-width 2.9 --fig-width 12 --fig-height 9 --dpi 320 \
  --save-plot out/real_solution.png --save-tour out/real_tour.txt
```

Caso real – bairro Jardins com mapa (tour destacado)

```powershell
$env:PYTHONPATH="src"
python -m pcc.solve_cli --input data\real_edges.csv --nodes data\real_nodes.csv --largest-component --plot `
  --style tour --basemap --basemap-provider CartoDB.Positron --basemap-zoom 17 `
  --label-mode endpoints --show-start --edge-alpha 0.55 --edge-width 3.4 --fig-width 13 --fig-height 9.5 --dpi 320 `
  --save-plot out\real_solution_basemap.png --save-tour out\real_tour.txt
```

```bash
PYTHONPATH=src python -m pcc.solve_cli --input data/real_edges.csv --nodes data/real_nodes.csv --largest-component --plot \
  --style tour --basemap --basemap-provider CartoDB.Positron --basemap-zoom 17 \
  --label-mode endpoints --show-start --edge-alpha 0.55 --edge-width 3.4 --fig-width 13 --fig-height 9.5 --dpi 320 \
  --save-plot out/real_solution_basemap.png --save-tour out/real_tour.txt
```

Observações

- Em redes densas, ative `--edge-labels` somente se o número de arestas for pequeno.
- Ajuste `--dpi`, `--fig-width` e `--fig-height` para exportações de alta qualidade.
- Para um visual “mapa real”, combine `--basemap` + `--style tour` (veja o preset acima).

## Compatibilidade/aliases da CLI

Os aliases abaixo são equivalentes às flags principais e existem por conveniência.

Windows (PowerShell)

```powershell
$env:PYTHONPATH="src"
# --input ≡ --edgelist
python -m pcc.solve_cli --edgelist data\example_edges.csv
# --plot ≡ --draw
python -m pcc.solve_cli --input data\example_edges.csv --draw --save-plot out\example.png
```

Linux/macOS

```bash
PYTHONPATH=src python -m pcc.solve_cli --edgelist data/example_edges.csv
PYTHONPATH=src python -m pcc.solve_cli --input data/example_edges.csv --draw --save-plot out/example.png
```

---

## Testes

```bash
pytest -q
```

O teste `tests/test_example.py` confere custo ≈ 16.0, tour fechado e cobertura das arestas do exemplo.

---

## Slides (Marp)

```bash
npx @marp-team/marp-cli slides/seminario.md -o slides/seminario.pdf
```

---

## Dicas e troubleshooting

- `ModuleNotFoundError: pcc`: defina `PYTHONPATH=src` como nos comandos acima.
- Grafo real desconexo: use `--largest-component` ou aumente `--snap-m` no conversor.
- Sem `make` no Windows: use os comandos PowerShell ou crie um `make.ps1` com atalhos.
- Ambiente sem GUI (servidor/CI): gere o arquivo com `--plot --save-plot out/fig.png` (não abrirá janela interativa).

---

## Exemplo ilustrativo

Abaixo está um exemplo gráfico do **Problema do Carteiro Chinês** aplicado a um grafo simplificado (um “bairro” com 5 esquinas A–E).

- Vértices representam esquinas.
- Arestas representam ruas, com pesos equivalentes a distâncias.
- O caminho ótimo encontrado pelo algoritmo está destacado em **vermelho**.

![Exemplo do Problema do Carteiro Chinês](pcc_exemplo.png)

---

## Créditos e licenças

- Código: pode ser licenciado como MIT (adicione um `LICENSE` se desejar).
- Dados: “Map data © OpenStreetMap contributors”, ODbL 1.0.
  - https://www.openstreetmap.org/copyright
  - https://osmfoundation.org/wiki/Licence/Attribution_Guidelines
  - https://opendatacommons.org/licenses/odbl/1-0/

---

## Autores

- Gilson Inácio da Silva
- Ederson Manoel de Oliveira
