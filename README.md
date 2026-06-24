# Sistema de Controle de Estoque — Unicarioca

SPA desenvolvida como **Projeto de Extensão em Web Back-End** do Centro Universitário Carioca (Unicarioca). A solução é voltada a **micro e pequenos comerciantes (MPEs)** que precisam gerenciar produtos, monitorar quantidades em estoque e identificar itens que exigem reposição.

## Sobre o projeto

O sistema permite cadastrar produtos com informações como nome, categoria, preço, quantidade atual e estoque mínimo. O backend calcula automaticamente a situação de cada item:

| Situação   | Condição                                      |
|------------|-----------------------------------------------|
| `ok`       | quantidade acima do estoque mínimo            |
| `baixo`    | quantidade menor ou igual ao estoque mínimo   |
| `esgotado` | quantidade igual a zero                         |

A exclusão de produtos é feita por **exclusão lógica**, preservando o histórico no banco de dados.

## Tecnologias

| Camada         | Tecnologia                          |
|----------------|-------------------------------------|
| Frontend       | React.js, Axios, HTML, CSS          |
| Backend        | Python, Flask, Flask-CORS           |
| Banco de dados | MongoDB                             |
| Infraestrutura | Docker, Docker Compose              |
| Testes         | unittest (biblioteca padrão Python) |

## Arquitetura

O backend segue organização em camadas:

```
Controller → Service → Repository → MongoDB
```

- **Controller:** rotas HTTP (Blueprint Flask)
- **Service:** regras de negócio e validações
- **Repository:** persistência e consultas
- **Domain:** entidade `Produto`, enums e value objects

Injeção de dependência é feita no `app.py` (composition root).

## Diagramas UML

### Diagrama de caso de uso

Ator: **Comerciante**. Relacionamentos `include` e `extend` conforme definido na Etapa 2.

```mermaid
flowchart TB
    Comerciante((Comerciante))

    subgraph Sistema["Sistema de Controle de Estoque"]
        direction TB
        UC1(["Listar produtos do estoque"])
        UC2(["Ver resumo e alertas"])
        UC3(["Filtrar e buscar produtos"])
        UC4(["Cadastrar novo produto"])
        UC5(["Ver detalhes do produto"])
        UC6(["Atualizar produto"])
        UC7(["Atualizar quantidade em estoque"])
        UC8(["Excluir produto"])
    end

    Comerciante --> UC1
    Comerciante --> UC4
    Comerciante --> UC5
    Comerciante --> UC6
    Comerciante --> UC8

    UC1 -.->|include| UC2
    UC1 -.->|extend| UC3
    UC6 -.->|extend| UC7
```

### Diagrama de classes

Domínio, value objects, enums e camadas do backend Flask.

```mermaid
classDiagram
    direction TB

    class ProdutoController {
        <<Flask Blueprint>>
        +listar() Response
        +cadastrar() Response
        +detalhar(id) Response
        +atualizar(id) Response
        +ajustar_quantidade(id) Response
        +excluir(id) Response
    }

    class ProdutoService {
        +listar(filtros) tuple
        +cadastrar(dados) Produto
        +buscar_por_id(id) Produto
        +atualizar(id, dados) Produto
        +ajustar_quantidade(id, qtd) Produto
        +excluir(id) dict
        +validar(dados) list
        +gerar_resumo(produtos) ResumoEstoque
    }

    class ProdutoRepository {
        +find_all(filtros) list
        +find_by_id(id) Produto
        +insert(produto) Produto
        +update(id, dados) Produto
        +soft_delete(id) bool
    }

    class Produto {
        +ObjectId _id
        +str nome
        +str categoria
        +float preco_unitario
        +int quantidade_estoque
        +int estoque_minimo
        +str unidade_medida
        +str status
        +calcular_situacao() SituacaoEstoque
        +to_dict() dict
        +to_document() dict
        +from_document(doc) Produto
    }

    class ResumoEstoque {
        <<value object>>
        +int total_produtos
        +int produtos_em_alerta
        +int produtos_esgotados
        +to_dict() dict
    }

    class Categoria {
        <<enumeration>>
        alimentos
        bebidas
        limpeza
        higiene
        papelaria
        utilidades
        outros
    }

    class UnidadeMedida {
        <<enumeration>>
        un kg g l ml pct cx
    }

    class SituacaoEstoque {
        <<enumeration>>
        ok baixo esgotado
    }

    class StatusProduto {
        <<enumeration>>
        ativo descontinuado
    }

    ProdutoController --> ProdutoService : usa
    ProdutoService --> ProdutoRepository : usa
    ProdutoRepository --> Produto : persiste
    ProdutoService --> ResumoEstoque : gera
    ProdutoService --> Produto : valida
    Produto ..> SituacaoEstoque : calcula
    Produto ..> Categoria : categoria
    Produto ..> UnidadeMedida : unidade
    Produto ..> StatusProduto : status
```

## Estrutura do repositório

```
projeto-academico-unicarioca/
├── backend/
│   ├── app.py                 # ponto de entrada da API
│   ├── controllers/           # rotas HTTP
│   ├── services/              # regras de negócio
│   ├── repositories/          # acesso ao MongoDB
│   ├── domain/                # entidades e enums
│   ├── dtos/                  # tradução HTTP ↔ domínio
│   ├── migrations/            # versionamento do banco
│   ├── tests/                 # testes unitários
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.js             # SPA principal
│   │   ├── App.css
│   │   └── api.js             # cliente Axios
│   └── package.json
├── docs/
│   └── ENTREGA_ETAPA3.html    # modelo de entrega (PDF)
└── docker-compose.yml
```

## Pré-requisitos

- [Docker](https://www.docker.com/) e Docker Compose instalados

## Como executar

### Primeira execução (ou após alterar dependências)

```bash
docker compose up -d --build
```

### Execução no dia a dia (desenvolvimento)

Com os volumes configurados para hot-reload, basta:

```bash
docker compose up -d
```

Use `--build` novamente apenas se houver mudanças em `Dockerfile`, `requirements.txt` ou `package.json`.

### Migrations do banco

Após subir os containers pela primeira vez:

```bash
docker exec unicarioca_backend python migrate.py
```

### Testes unitários (backend)

```bash
docker exec -w /app unicarioca_backend python -m unittest discover -s tests -t /app -v
```

## Acessos

| Serviço        | URL                          |
|----------------|------------------------------|
| Frontend (SPA) | http://localhost:3000        |
| API (Backend)  | http://localhost:5000        |
| Mongo Express  | http://localhost:8081        |

## API REST — Produtos

| Método | Rota                          | Descrição                    |
|--------|-------------------------------|------------------------------|
| GET    | `/produtos`                   | Listar (filtros + resumo)    |
| GET    | `/produtos/<id>`              | Detalhar produto             |
| POST   | `/produtos`                   | Cadastrar produto            |
| PUT    | `/produtos/<id>`              | Atualizar produto            |
| PATCH  | `/produtos/<id>/quantidade`   | Ajuste rápido de quantidade  |
| DELETE | `/produtos/<id>`              | Excluir (exclusão lógica)    |

**Filtros disponíveis em `GET /produtos`:** `?categoria=`, `?status=`, `?busca=`

**Exemplo de resposta da listagem:**

```json
{
  "produtos": [
    {
      "id": "...",
      "nome": "Arroz Branco 5kg",
      "categoria": "alimentos",
      "quantidade_estoque": 40,
      "estoque_minimo": 10,
      "situacao": "ok"
    }
  ],
  "resumo": {
    "total_produtos": 3,
    "produtos_em_alerta": 1,
    "produtos_esgotados": 1
  }
}
```

## Funcionalidades da SPA

- Cadastro, edição e exclusão de produtos
- Listagem com situação visual (ok / baixo / esgotado)
- Painel de resumo com totais e alertas
- Filtros dinâmicos por categoria e busca por nome
- Ajuste rápido de quantidade (+ / −)
- Menu de navegação entre seções

## Encerrar a aplicação

```bash
docker compose down
```

Para remover também o volume de dados do MongoDB:

```bash
docker compose down -v
```

## Contexto acadêmico

Projeto desenvolvido na disciplina **Projeto de Extensão em Web Back-End** (Unicarioca), como culminância da **Etapa 3 — Produto Final**, com customização conforme regras de negócio definidas na Etapa 2 (Plano de Ação em Prática).
