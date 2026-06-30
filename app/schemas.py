from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class FilmeBase(BaseModel):
    titulo: str = Field(..., min_length=1, max_length=200)
    ano: Optional[int] = None
    genero: Optional[str] = ""
    autor: Optional[str] = ""
    nota: Optional[float] = Field(None, ge=0, le=10)
    comentario: Optional[str] = ""
    poster_url: Optional[str] = ""


class FilmeCreate(FilmeBase):
    pass


class FilmeUpdate(BaseModel):
    nota: Optional[float] = Field(None, ge=0, le=10)
    comentario: Optional[str] = ""


class FilmeOut(FilmeBase):
    id: int
    lista_id: int
    adicionado_em: datetime

    model_config = {"from_attributes": True}


class ListaOut(BaseModel):
    id: int
    nome: str
    descricao: str
    criado_em: datetime
    filmes: list[FilmeOut] = []

    model_config = {"from_attributes": True}


class ListaSummary(BaseModel):
    id: int
    nome: str
    total_filmes: int = 0

    model_config = {"from_attributes": True}


class CitacaoBase(BaseModel):
    citacao: str = Field(..., min_length=1)
    autor: Optional[str] = ""


class CitacaoCreate(CitacaoBase):
    pass


class CitacaoUpdate(CitacaoBase):
    pass


class CitacaoOut(CitacaoBase):
    id: int
    adicionado_em: datetime

    model_config = {"from_attributes": True}


class SearchResult(BaseModel):
    titulo: str
    ano: Optional[int] = None
    genero: Optional[str] = ""
    autor: Optional[str] = ""
    poster_url: Optional[str] = ""
