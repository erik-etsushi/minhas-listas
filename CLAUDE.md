# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Setup e execução

```bash
# Criar ambiente virtual e instalar dependências
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Rodar o servidor (raiz do projeto)
uvicorn app.main:app --reload

# Acessa em http://localhost:8000
```

## Arquitetura

Aplicativo web SPA para organizar filmes favoritos em listas. Stack:

- **Backend**: FastAPI servindo a API REST e os arquivos estáticos do frontend
- **Banco de dados**: SQLite via SQLAlchemy (arquivo `filmes.db` gerado automaticamente na raiz)
- **Frontend**: SPA com Alpine.js (reatividade) e Tailwind CSS (estilos), ambos via CDN — sem build step

### Fluxo de dados

```
Browser → GET /* → FastAPI → static/index.html (SPA)
Browser → /api/* → FastAPI routers → SQLAlchemy → filmes.db
```

O `app/main.py` monta `/static` como diretório de arquivos estáticos e tem um fallback catch-all `/{full_path}` que sempre devolve `index.html` para suportar navegação client-side.

### Modelos de dados

- `Lista` (id, nome, descricao, criado_em) → tem muitos `Filme`
- `Filme` (id, lista_id, titulo, ano, genero, nota, comentario, poster_url, adicionado_em)

### Rotas da API

- `GET/POST /api/listas/` — listar e criar listas
- `GET/PUT/DELETE /api/listas/{id}` — detalhes, editar e excluir lista (com filmes aninhados)
- `POST /api/listas/{lista_id}/filmes/` — adicionar filme
- `PUT/DELETE /api/listas/{lista_id}/filmes/{filme_id}` — editar e remover filme

### Frontend (`static/`)

- `index.html` — estrutura HTML completa com Alpine.js declarativo; duas "telas" controladas por `x-show`
- `app.js` — função `app()` com todo o estado e lógica de fetch; sem frameworks de build
- `style.css` — somente overrides mínimos (line-clamp, tap highlight, font-size iOS)

O estado global vive em `app()` no `app.js`: `listas` (array), `listaAtiva` (objeto com filmes), modais e formulários.
