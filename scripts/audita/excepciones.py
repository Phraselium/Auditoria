"""Modelo unico de excepcion. Todas las skills reportan con esta estructura.

Reporte por excepcion (principio nº3): el output por defecto es
conclusion + excepciones + evidencia. Nunca volcados masivos.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any

# Severidad. El orden importa: se usa para ordenar y para decidir si se puede firmar.
BLOQUEANTE = "BLOQUEANTE"        # impide continuar / impide firmar
RESOLVER = "RESOLVER"            # a resolver antes de firmar
DOCUMENTAR = "DOCUMENTAR"        # mejora de documentacion
INFORMATIVA = "INFORMATIVA"      # se deja constancia, no exige accion

ORDEN_SEVERIDAD = {BLOQUEANTE: 0, RESOLVER: 1, DOCUMENTAR: 2, INFORMATIVA: 3}


@dataclass
class Excepcion:
    codigo: str                       # p.ej. "CUA-003"
    severidad: str
    area: str                         # referencia del indice: "E", "F", "2.1"...
    descripcion: str
    importe: float | None = None
    cuenta: str | None = None
    origen: str = ""                  # traza legible
    causa_sugerida: str = ""          # hipotesis, nunca afirmacion
    accion: str = ""                  # que hay que hacer
    referencia_normativa: str = ""    # solo si fundamenta la decision

    def __post_init__(self) -> None:
        if self.severidad not in ORDEN_SEVERIDAD:
            raise ValueError(f"Severidad no valida: {self.severidad}")

    def fila(self) -> dict[str, Any]:
        return {
            "Codigo": self.codigo,
            "Severidad": self.severidad,
            "Area": self.area,
            "Descripcion": self.descripcion,
            "Importe": self.importe,
            "Cuenta": self.cuenta or "",
            "Origen": self.origen,
            "Causa sugerida": self.causa_sugerida,
            "Accion": self.accion,
            "Norma": self.referencia_normativa,
        }

    def dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Resultado:
    """Lo que devuelve toda rutina de calculo del plugin."""

    concepto: str
    conclusion: str = ""
    excepciones: list[Excepcion] = field(default_factory=list)
    datos: dict[str, Any] = field(default_factory=dict)

    def añade(self, exc: Excepcion) -> None:
        self.excepciones.append(exc)

    def add(self, exc: Excepcion) -> None:  # alias ascii
        self.excepciones.append(exc)

    @property
    def bloqueantes(self) -> list[Excepcion]:
        return [e for e in self.excepciones if e.severidad == BLOQUEANTE]

    @property
    def ok(self) -> bool:
        return not self.bloqueantes

    def ordenadas(self) -> list[Excepcion]:
        return sorted(
            self.excepciones,
            key=lambda e: (ORDEN_SEVERIDAD[e.severidad], -abs(e.importe or 0)),
        )

    def resumen(self, max_lineas: int = 15) -> str:
        """Resumen en pantalla, maximo 15 lineas (formato de salida §7)."""
        lineas = [f"== {self.concepto} =="]
        if self.conclusion:
            lineas.append(f"Conclusion: {self.conclusion}")
        cuenta = {s: 0 for s in ORDEN_SEVERIDAD}
        for e in self.excepciones:
            cuenta[e.severidad] += 1
        lineas.append(
            "Excepciones: "
            + ", ".join(f"{s}={cuenta[s]}" for s in ORDEN_SEVERIDAD if cuenta[s])
            or "Excepciones: ninguna"
        )
        for e in self.ordenadas()[: max_lineas - len(lineas) - 1]:
            imp = f" {e.importe:,.2f}" if e.importe is not None else ""
            lineas.append(f"  [{e.severidad}] {e.codigo} {e.area}:{imp} {e.descripcion}")
        restantes = len(self.excepciones) - (len(lineas) - 3)
        if restantes > 0:
            lineas.append(f"  ... y {restantes} mas (ver hoja Excepciones)")
        return "\n".join(lineas[:max_lineas])
