from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/api/citacoes", tags=["citacoes"])


@router.get("/", response_model=list[schemas.CitacaoOut])
def listar_citacoes(db: Session = Depends(get_db)):
    return db.query(models.Citacao).all()


@router.post("/", response_model=schemas.CitacaoOut, status_code=201)
def criar_citacao(dados: schemas.CitacaoCreate, db: Session = Depends(get_db)):
    c = models.Citacao(**dados.model_dump())
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


@router.put("/{citacao_id}", response_model=schemas.CitacaoOut)
def editar_citacao(citacao_id: int, dados: schemas.CitacaoUpdate, db: Session = Depends(get_db)):
    c = db.query(models.Citacao).filter(models.Citacao.id == citacao_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Não encontrada")
    for campo, valor in dados.model_dump().items():
        setattr(c, campo, valor)
    db.commit()
    db.refresh(c)
    return c


@router.delete("/{citacao_id}", status_code=204)
def remover_citacao(citacao_id: int, db: Session = Depends(get_db)):
    c = db.query(models.Citacao).filter(models.Citacao.id == citacao_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Não encontrada")
    db.delete(c)
    db.commit()
