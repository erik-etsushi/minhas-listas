from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/api/listas", tags=["listas"])


@router.get("/", response_model=list[schemas.ListaSummary])
def listar_listas(db: Session = Depends(get_db)):
    listas = db.query(models.Lista).all()
    return [
        schemas.ListaSummary(id=l.id, nome=l.nome, total_filmes=len(l.filmes))
        for l in listas
    ]


@router.get("/{lista_id}", response_model=schemas.ListaOut)
def obter_lista(lista_id: int, db: Session = Depends(get_db)):
    lista = db.query(models.Lista).filter(models.Lista.id == lista_id).first()
    if not lista:
        raise HTTPException(status_code=404, detail="Lista não encontrada")
    return lista
