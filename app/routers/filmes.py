from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/api/listas/{lista_id}/filmes", tags=["filmes"])


def _get_lista(lista_id: int, db: Session) -> models.Lista:
    lista = db.query(models.Lista).filter(models.Lista.id == lista_id).first()
    if not lista:
        raise HTTPException(status_code=404, detail="Lista não encontrada")
    return lista


@router.post("/", response_model=schemas.FilmeOut, status_code=201)
def adicionar_filme(lista_id: int, filme: schemas.FilmeCreate, db: Session = Depends(get_db)):
    _get_lista(lista_id, db)
    db_filme = models.Filme(**filme.model_dump(), lista_id=lista_id)
    db.add(db_filme)
    db.commit()
    db.refresh(db_filme)
    return db_filme


@router.put("/{filme_id}", response_model=schemas.FilmeOut)
def editar_filme(lista_id: int, filme_id: int, dados: schemas.FilmeUpdate, db: Session = Depends(get_db)):
    _get_lista(lista_id, db)
    filme = db.query(models.Filme).filter(
        models.Filme.id == filme_id, models.Filme.lista_id == lista_id
    ).first()
    if not filme:
        raise HTTPException(status_code=404, detail="Não encontrado")
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(filme, campo, valor)
    db.commit()
    db.refresh(filme)
    return filme


@router.delete("/{filme_id}", status_code=204)
def remover_filme(lista_id: int, filme_id: int, db: Session = Depends(get_db)):
    _get_lista(lista_id, db)
    filme = db.query(models.Filme).filter(
        models.Filme.id == filme_id, models.Filme.lista_id == lista_id
    ).first()
    if not filme:
        raise HTTPException(status_code=404, detail="Não encontrado")
    db.delete(filme)
    db.commit()
