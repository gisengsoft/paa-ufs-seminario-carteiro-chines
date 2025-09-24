## 📚 Sobre

Repositório com o material do seminário da disciplina **Projeto e Análise de Algoritmos (PAA)** da **UFS**, cujo tema é o **Problema do Carteiro Chinês** (*Chinese Postman Problem*).

Aqui estão organizados: o código em Python, os slides da apresentação e as instruções para execução.

---

## 📌 Estrutura

```text
paa-ufs-seminario-carteiro-chines/
│
├── codigo/
│   └── main.py
│
├── slides/
│   └── apresentacao.pdf   (aqui você colocará os slides exportados do Canva)
│
├── README.md              (documentação principal do projeto)
│
└── requirements.txt       (lista de dependências: networkx, matplotlib)
```

- `codigo/` → código-fonte em Python para resolver uma instância do problema.
- `slides/` → slides da apresentação em PDF.
- `README.md` → este arquivo.
- `requirements.txt` → dependências do projeto.

---

## 📚 Introdução

O **Problema do Carteiro Chinês** (ou *Chinese Postman Problem*) consiste em encontrar o caminho de menor custo que percorre **todas as arestas de um grafo ao menos uma vez**.  
É muito aplicado em problemas de logística, como rotas de entrega, coleta de lixo ou inspeção de ruas.

---

## 🚀 Como executar o código

1. Clone este repositório:
  
  ```bash
  git clone https://github.com/seu-usuario/paa-ufs-seminario-carteiro-chines.git
  cd paa-ufs-seminario-carteiro-chines/codigo
  ```
  
2. Instale as dependências:
  
  ```bash
  pip install -r ../requirements.txt
  ```
  
3. Execute o programa:
  
  ```bash
  python main.py
  ```
  

---

## 🧾 Exemplo de saída

- O script desenhará um grafo simples.
- Caminho Euleriano (se existir):
  
  ```
  Caminho do Carteiro Chinês (Euleriano):
  [('A', 'B'), ('B', 'C'), ('C', 'A'), ('C', 'D'), ('D', 'B')]
  ```
  
- Caso o grafo não seja Euleriano, a mensagem indicará que é necessário emparelhar vértices de grau ímpar.

---

## 📊 Slides

O arquivo `slides/apresentacao.pdf` deve conter os slides exportados do **Canva** (ou outra ferramenta de sua preferência) com o conteúdo do seminário.

---

## 🎥 Vídeo da Apresentação

👉 Link para o YouTube será inserido aqui.

---

## 🧰 Dependências

Conteúdo do arquivo `requirements.txt`:

```
networkx
matplotlib
```

---

## 👥 Autores

- [Gilson Inácio da Silva]
- [Ederson]
