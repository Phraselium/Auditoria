"""Trazabilidad: todo dato de salida debe poder reconducirse a su origen.

Principio de diseno nº2 del encargo (cero invencion): ninguna cifra sale del
plugin sin una `Traza` que diga de que fichero, hoja y celda/fila procede, o de
que documento, pagina y clausula.

Uso tipico:

    reg = RegistroTrazas()
    t = reg.anota("importe_financiado", 120000.0,
                  Traza("leasings.xlsx", hoja="Contratos", ref="D14"))
    ...
    reg.a_dataframe()   # -> hoja "Traza" del papel de trabajo
"""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass, field
from typing import Any

# Marcadores reservados. Nunca se sustituyen por una estimacion silenciosa.
PENDIENTE_CLIENTE = "[PENDIENTE-CLIENTE]"
JUICIO_AUDITOR = "[JUICIO-AUDITOR]"
VERIFICAR_LITERAL = "[VERIFICAR-LITERAL-ICAC]"

MARCADORES = (PENDIENTE_CLIENTE, JUICIO_AUDITOR, VERIFICAR_LITERAL)


@dataclass(frozen=True)
class Traza:
    """Origen verificable de un dato.

    Para ficheros de calculo: fichero + hoja + celda/fila.
    Para documentos: fichero + pagina + clausula (se usan `hoja` y `ref`).
    """

    fichero: str
    hoja: str | None = None
    ref: str | None = None
    nota: str | None = None
    # Confianza declarada de la extraccion (1.0 = leido de una celda; valores
    # menores los fija el extractor documental sobre PDF/OCR).
    confianza: float = 1.0

    def __str__(self) -> str:
        partes = [os.path.basename(self.fichero)]
        if self.hoja:
            partes.append(str(self.hoja))
        if self.ref:
            partes.append(str(self.ref))
        base = "!".join(partes)
        if self.nota:
            base = f"{base} ({self.nota})"
        return base

    @property
    def fiable(self) -> bool:
        """Por debajo de 0.85 el dato va siempre a revision humana."""
        return self.confianza >= 0.85


@dataclass
class Anotacion:
    concepto: str
    valor: Any
    traza: Traza

    @property
    def requiere_revision(self) -> bool:
        if isinstance(self.valor, str) and self.valor in MARCADORES:
            return True
        return not self.traza.fiable


@dataclass
class RegistroTrazas:
    """Acumula las trazas de un papel de trabajo."""

    anotaciones: list[Anotacion] = field(default_factory=list)

    def anota(self, concepto: str, valor: Any, traza: Traza) -> Any:
        self.anotaciones.append(Anotacion(concepto, valor, traza))
        return valor

    def pendiente(self, concepto: str, fichero: str, nota: str | None = None) -> str:
        """Marca un dato ausente. Devuelve el marcador, nunca un valor inventado."""
        self.anotaciones.append(
            Anotacion(concepto, PENDIENTE_CLIENTE, Traza(fichero, nota=nota))
        )
        return PENDIENTE_CLIENTE

    def juicio(self, concepto: str, fichero: str, nota: str | None = None) -> str:
        self.anotaciones.append(
            Anotacion(concepto, JUICIO_AUDITOR, Traza(fichero, nota=nota))
        )
        return JUICIO_AUDITOR

    def extend(self, otro: "RegistroTrazas") -> None:
        self.anotaciones.extend(otro.anotaciones)

    @property
    def pendientes(self) -> list[Anotacion]:
        return [a for a in self.anotaciones if a.requiere_revision]

    def filas(self) -> list[dict[str, Any]]:
        return [
            {
                "Concepto": a.concepto,
                "Valor": a.valor,
                "Fichero": os.path.basename(a.traza.fichero),
                "Hoja/Pagina": a.traza.hoja or "",
                "Celda/Fila/Clausula": a.traza.ref or "",
                "Confianza": round(a.traza.confianza, 2),
                "Nota": a.traza.nota or "",
                "Requiere revision": "SI" if a.requiere_revision else "",
            }
            for a in self.anotaciones
        ]


def huella(path: str) -> str:
    """SHA-256 del fichero fuente. Se guarda en encargo.json para detectar que
    el cliente ha reenviado una version distinta de un fichero ya trabajado."""
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for bloque in iter(lambda: fh.read(65536), b""):
            h.update(bloque)
    return h.hexdigest()
