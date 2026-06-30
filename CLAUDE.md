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
# Docs interativos: http://localhost:8000/docs
```

## Arquitetura

Aplicativo web SPA para organizar filmes, séries e livros favoritos em listas. Stack:

- **Backend**: FastAPI servindo a API REST e os arquivos estáticos do frontend
- **Banco de dados**: SQLite via SQLAlchemy (arquivo `filmes.db` gerado automaticamente na raiz)
- **Frontend**: SPA com Alpine.js (reatividade) e Tailwind CSS (estilos), ambos via CDN — sem build step

### Fluxo de dados

```
Browser → GET /* → FastAPI → static/index.html (SPA)
Browser → /api/* → FastAPI routers → SQLAlchemy → filmes.db
```

`app/main.py` monta `/static` e tem um catch-all `/{full_path}` que devolve `index.html` para suportar navegação client-side. Na inicialização, `_seed_listas()` cria as listas padrão ("Filmes", "Séries", "Livros") se ainda não existirem.

### Modelos de dados

- `Lista` (id, nome, descricao, criado_em) → tem muitos `Filme`
- `Filme` (id, lista_id, titulo, ano, genero, **autor**, nota, comentario, poster_url, adicionado_em)

O campo `autor` é usado principalmente para livros. `nota` aceita 0–10.

### Rotas da API

**Listas** (`app/routers/listas.py`):
- `GET /api/listas/` — retorna `List[ListaSummary]` (id, nome, total_filmes — sem filmes aninhados)
- `GET /api/listas/{lista_id}` — retorna `ListaOut` completo com `filmes: []` aninhados

> Listas são criadas apenas via seed; não existe rota POST/PUT/DELETE para listas.

**Filmes** (`app/routers/filmes.py`):
- `POST /api/listas/{lista_id}/filmes/` — adicionar item
- `PUT /api/listas/{lista_id}/filmes/{filme_id}` — editar (aceita só `nota` e `comentario` via `FilmeUpdate`)
- `DELETE /api/listas/{lista_id}/filmes/{filme_id}` — remover item

**Busca** (`app/routers/search.py`):
- `GET /api/search/?q=<termo>&tipo=<filmes|series|livros>` — busca externa sem autenticação
  - `filmes`/`series` → IMDB suggestion API (`sg.media-imdb.com/suggestion`)
  - `livros` → OpenLibrary (`openlibrary.org/search.json`)

### Frontend (`static/`)

- `index.html` — estrutura HTML com Alpine.js declarativo; telas controladas por `x-show`
- `app.js` — função `app()` com todo o estado e lógica de fetch
- `style.css` — overrides mínimos (line-clamp, tap highlight, font-size iOS)

O estado global vive em `app()`: `listas` (array), `listaAtiva` (objeto com filmes), modais e formulários.

## Deploy (Docker + Litestream)

O container usa **Litestream** para replicar o SQLite continuamente para um storage externo (ex: GCS).

- `Dockerfile` — instala Litestream, copia `app/`, `static/`, `litestream.yml`
- `litestream.yml` — replica `/app/filmes.db` para `$LITESTREAM_REPLICA_URL`
- `docker-entrypoint.sh` — se `$LITESTREAM_REPLICA_URL` estiver definido: restaura o DB antes de iniciar e executa uvicorn via `litestream replicate`; caso contrário, roda uvicorn diretamente

```bash
# Build e rodar com Docker (sem replicação)
docker build -t minhas-listas .
docker run -p 8080:8080 minhas-listas

# Com replicação Litestream
docker run -e LITESTREAM_REPLICA_URL=gcs://bucket/filmes.db -p 8080:8080 minhas-listas
```
