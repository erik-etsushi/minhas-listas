from sqlalchemy import Column, ForeignKey, Integer, String, Float, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class Lista(Base):
    __tablename__ = "listas"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False, unique=True)
    descricao = Column(Text, default="")
    criado_em = Column(DateTime(timezone=True), server_default=func.now())

    filmes = relationship("Filme", back_populates="lista", cascade="all, delete-orphan")


class Filme(Base):
    __tablename__ = "filmes"

    id = Column(Integer, primary_key=True, index=True)
    lista_id = Column(Integer, ForeignKey("listas.id"), nullable=False)
    titulo = Column(String(200), nullable=False)
    ano = Column(Integer)
    genero = Column(String(100), default="")
    autor = Column(String(200), default="")
    nota = Column(Float)
    comentario = Column(Text, default="")
    poster_url = Column(String(500), default="")
    adicionado_em = Column(DateTime(timezone=True), server_default=func.now())

    lista = relationship("Lista", back_populates="filmes")


class Citacao(Base):
    __tablename__ = "citacoes"

    id = Column(Integer, primary_key=True, index=True)
    citacao = Column(Text, nullable=False)
    autor = Column(String(200), default="")
    adicionado_em = Column(DateTime(timezone=True), server_default=func.now())
