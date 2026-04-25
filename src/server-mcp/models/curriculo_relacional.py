"""Modelos ORM normalizados para persistir el curriculo en PostgreSQL."""

from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from curriculo_matematica.db.engine import Base


class CurriculoNivel(Base):
    __tablename__ = "curriculo_nivel"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)


class CurriculoNodo(Base):
    __tablename__ = "curriculo_nodo"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    nivel_id: Mapped[int] = mapped_column(
        ForeignKey("curriculo_nivel.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    titulo: Mapped[str] = mapped_column(String(255), nullable=False)
    capacidad: Mapped[str] = mapped_column(Text, nullable=False)
    situacion_anclaje: Mapped[str] = mapped_column(Text, nullable=False)
    pregunta_indagacion: Mapped[str] = mapped_column(Text, nullable=False)


class CurriculoNodoSaber(Base):
    __tablename__ = "curriculo_nodo_saber"
    __table_args__ = (UniqueConstraint("nodo_id", "orden", name="uq_curriculo_nodo_saber_orden"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nodo_id: Mapped[str] = mapped_column(
        ForeignKey("curriculo_nodo.id", ondelete="CASCADE"), nullable=False, index=True
    )
    orden: Mapped[int] = mapped_column(Integer, nullable=False)
    texto: Mapped[str] = mapped_column(Text, nullable=False)


class CurriculoNodoAndamiaje(Base):
    __tablename__ = "curriculo_nodo_andamiaje"
    __table_args__ = (UniqueConstraint("nodo_id", "orden", name="uq_curriculo_nodo_andamiaje_orden"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nodo_id: Mapped[str] = mapped_column(
        ForeignKey("curriculo_nodo.id", ondelete="CASCADE"), nullable=False, index=True
    )
    orden: Mapped[int] = mapped_column(Integer, nullable=False)
    texto: Mapped[str] = mapped_column(Text, nullable=False)


class CurriculoNodoVocabulario(Base):
    __tablename__ = "curriculo_nodo_vocabulario"
    __table_args__ = (UniqueConstraint("nodo_id", "orden", name="uq_curriculo_nodo_vocab_orden"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nodo_id: Mapped[str] = mapped_column(
        ForeignKey("curriculo_nodo.id", ondelete="CASCADE"), nullable=False, index=True
    )
    orden: Mapped[int] = mapped_column(Integer, nullable=False)
    termino: Mapped[str] = mapped_column(String(255), nullable=False)


class CurriculoActividad(Base):
    __tablename__ = "curriculo_actividad"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)


class CurriculoNodoActividad(Base):
    __tablename__ = "curriculo_nodo_actividad"
    __table_args__ = (UniqueConstraint("nodo_id", "orden", name="uq_curriculo_nodo_actividad_orden"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nodo_id: Mapped[str] = mapped_column(
        ForeignKey("curriculo_nodo.id", ondelete="CASCADE"), nullable=False, index=True
    )
    actividad_id: Mapped[str] = mapped_column(
        ForeignKey("curriculo_actividad.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    orden: Mapped[int] = mapped_column(Integer, nullable=False)


class CurriculoNodoPrerequisito(Base):
    __tablename__ = "curriculo_nodo_prerequisito"

    nodo_id: Mapped[str] = mapped_column(
        ForeignKey("curriculo_nodo.id", ondelete="CASCADE"), primary_key=True
    )
    prerequisito_nodo_id: Mapped[str] = mapped_column(
        ForeignKey("curriculo_nodo.id", ondelete="RESTRICT"), primary_key=True
    )
