# Projeto Acadêmico Unicarioca

Este projeto integrado é composto por um **Frontend** (React), um **Backend** (Flask - Python) e um Banco de Dados (**MongoDB**).

Toda a infraestrutura é gerenciada através de containers Docker.

## Tecnologias Utilizadas
* **Frontend:** React.js
* **Backend:** Python + Flask
* **Banco de Dados:** MongoDB
* **Infraestrutura:** Docker e Docker Compose

## Como Rodar o Projeto

1. Certifique-se de ter o [Docker](https://www.docker.com/) instalado no seu computador.
2. Abra o terminal na pasta raiz do projeto.
3. Para iniciar a aplicação, utilize o seguinte comando:
   ```bash
   docker compose up -d --build
   ```

## Acessando a Aplicação
* **Frontend:** [http://localhost:3000](http://localhost:3000)
* **Backend / API:** [http://localhost:5000](http://localhost:5000)

## Encerrando a Aplicação
Para parar os serviços, digite no terminal:
```bash
docker compose down
```
