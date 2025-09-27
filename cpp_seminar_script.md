# Seminário – Problema do Carteiro Chinês (Chinese Postman Problem, CPP)

## Introdução
O **Problema do Carteiro Chinês (CPP)** surge em contextos onde é preciso **percorrer todas as arestas** de um grafo com **custo total mínimo** e **retornar ao ponto de partida**. Exemplos práticos incluem: coleta de lixo, varrição de ruas, leitura de medidores, manutenção de redes e inspeção de cabos/oleodutos. Em termos de teoria dos grafos, o CPP conecta-se diretamente a **circuitos eulerianos** e ao **emparelhamento mínimo** de vértices de grau ímpar.

**Por que é relevante?** Em aplicações reais, as “ruas” são arestas ponderadas (distância/tempo) e queremos um **roteiro fechado** que cubra todas elas com o **menor esforço**. O CPP demonstra como combinar **caminhos mínimos**, **grafo multiconjunto** (duplicação de arestas) e **Hierholzer** para obter um circuito euleriano.

## Apresentação do problema
**Definição (CPP não direcionado):** Dado um grafo conexo não direcionado e ponderado \\(G=(V,E)\\) com pesos não negativos, encontrar um **circuito fechado** de **custo mínimo** que **percorra todas as arestas pelo menos uma vez**.

- Se **todos os vértices tiverem grau par**, existe um **circuito euleriano** e ele já é a solução ótima.
- Se **existirem vértices de grau ímpar**, será necessário **duplicar** algumas arestas para viabilizar um circuito euleriano.

**Objetivo:** Minimizar o **custo total** (soma dos pesos das arestas originais + arestas duplicadas).

## Como o algoritmo resolve (versão clássica, não direcionada)
A solução é **ótima** para o CPP **não direcionado** com pesos não negativos.

1. **Conectividade:** verificar se o grafo é conexo (ignorando vértices isolados).
2. **Vértices ímpares:** listar os vértices com **grau ímpar** (sempre em número par).
3. **Distâncias entre ímpares:** calcular **caminhos mínimos** entre todos os pares de vértices ímpares (Dijkstra).
4. **Emparelhamento mínimo perfeito:** encontrar o **emparelhamento de custo mínimo** entre os vértices ímpares (neste projeto usamos DP por bitmask).
5. **Duplicação de arestas:** para cada par emparelhado, **duplicar** as arestas do caminho mínimo entre eles.
6. **Circuito Euleriano (Hierholzer):** construir o circuito que percorre cada aresta exatamente uma vez, originando a **rota do carteiro**.  

**Custo total =** soma das arestas originais **+** soma das duplicadas ao longo dos caminhos mínimos.

## Exemplo prático (grafo pequeno)
Grafo não direcionado e ponderado com vértices \\( \\{A,B,C,D,E\\}\\):

Arestas (peso):  
- \\(A-B: 2\\)  
- \\(A-C: 3\\)  
- \\(B-C: 1\\)  
- \\(B-D: 4\\)  
- \\(C-E: 2\\)  
- \\(D-E: 3\\)

**Passo a passo:**
1. **Graus:** \\( \\deg(A)=2, \\deg(B)=3, \\deg(C)=3, \\deg(D)=2, \\deg(E)=2 \\) ⇒ Ímpares: \\(B, C\\).
2. **Caminho mínimo entre ímpares:** de \\(B\\) para \\(C\\) tem custo **1** (aresta direta).
3. **Emparelhamento mínimo:** único par \\((B,C)\\) com custo 1.
4. **Duplicação:** duplicar \\(B-C\\).
5. **Euleriano:** agora todos os graus são pares ⇒ aplicar **Hierholzer** e obter um circuito.

**Custo total:** soma das arestas originais (15) + duplicação (1) ⇒ **16**.

## Código-fonte (Python, sem dependências pesadas)
O arquivo `cpp_solver.py` contém:
- Representação simples de grafo.
- Dijkstra para caminhos mínimos.
- Emparelhamento mínimo por DP bitmask.
- Duplicação de arestas ao longo de caminhos mínimos.
- Circuito de Hierholzer.
- Um **exemplo** pronto para rodar.

**Como executar localmente:**
```bash
python3 cpp_solver.py
```
Saída esperada:
```
Chinese Postman Problem (Undirected)
Total cost: 16.0
Eulerian circuit (vertex sequence):
A -> C -> B -> D -> E -> C -> B -> A
```

## Observações didáticas
- Se não há vértices ímpares, o grafo já é euleriano.  
- Para instâncias maiores, recomenda-se usar um algoritmo de emparelhamento perfeito mínimo mais geral (ex.: Blossom).  
- Para grafos direcionados, a formulação envolve balanceamento de graus via fluxo mínimo.  
- Em aplicações reais, extensões podem tornar o problema NP-difícil (como no Rural Postman Problem).

## Referências sugeridas
- Apostilas de “Route Inspection Problem” (CPP).  
- Livros de teoria dos grafos sobre circuitos eulerianos e emparelhamentos.
