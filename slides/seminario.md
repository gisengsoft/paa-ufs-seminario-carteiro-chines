---
marp: true
theme: default
paginate: true
math: katex
---
# Problema do Carteiro Chinês (CPP)
Projeto e Análise de Algoritmos — Seminário

Autores: Gilson Inácio da Silva; Ederson Manoel de Oliveira  
Professor: Leonardo Nogueira Matos

---

## Contexto e relevância
- Percorrer todas as arestas com custo mínimo e retornar ao ponto de partida.
- Aplicações: coleta de lixo, varrição de ruas, leitura de medidores, inspeções.
- Conceitos: euleriano, caminhos mínimos, emparelhamento.

---

## Definição (não dirigido)
Dado um grafo conexo, não dirigido e ponderado (pesos ≥ 0), encontrar um circuito fechado de custo mínimo que percorra todas as arestas pelo menos uma vez.

---

## Algoritmo
1. Conectividade (ignorar isolados)
2. Vértices ímpares
3. Dijkstra entre ímpares
4. Matching perfeito mínimo (DP por bitmask) — $O(k^2 \cdot 2^k)$
5. Duplicar arestas ao longo desses caminhos
6. Circuito de Euler (Hierholzer)

---

## Complexidade
- Dijkstra: $O(m \log n)$ por fonte
- Matching (DP): $O(k^2 \cdot 2^k)$
- Hierholzer: $O(m')$ no multigrafo

---

## Exemplo (A–E)
A–B: 2; A–C: 3; B–C: 1; B–D: 4; C–E: 2; D–E: 3  
Ímpares: B, C → duplicar B–C (1).  
Custo total: 15 + 1 = 16.

---

## Como executar
- Criar venv e instalar dependências:
  - Windows: `.venv\Scripts\activate` + `pip install -r requirements.txt`
- Rodar:
  - `PYTHONPATH=src python -m pcc.solve_cli --input data/example_edges.csv --plot`

---

## Conclusões
- Método ótimo para não dirigido com pesos ≥ 0.
- Base para variantes (direcionado, misto, RPP).