from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .database import engine, SessionLocal
from . import models
from .routers import listas, filmes, search, citacoes, email as email_router

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Minhas Listas")


def _seed_listas():
    db = SessionLocal()
    try:
        for nome in ("Filmes", "Séries", "Livros"):
            if not db.query(models.Lista).filter(models.Lista.nome == nome).first():
                db.add(models.Lista(nome=nome))
        db.commit()
    finally:
        db.close()


_seed_listas()

app.include_router(listas.router)
app.include_router(filmes.router)
app.include_router(search.router)
app.include_router(citacoes.router)
app.include_router(email_router.router)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/{full_path:path}")
def spa_fallback(full_path: str):
    return FileResponse("static/index.html")
