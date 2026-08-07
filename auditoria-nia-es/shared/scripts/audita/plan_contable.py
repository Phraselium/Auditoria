"""Mapeo de cuentas del PGC a epigrafes de los modelos oficiales.

El mapeo vive en shared/references/mapeo-pgc.json (fichero pesado, se carga
bajo demanda). Resolucion: gana el prefijo mas largo.
"""

from __future__ import annotations

import functools
import json
from typing import Any

from . import rutas

@functools.lru_cache(maxsize=1)
def _mapeo() -> dict[str, Any]:
    with open(rutas.fichero("referencias", "mapeo-pgc.json"), encoding="utf-8") as fh:
        return json.load(fh)


@functools.lru_cache(maxsize=1)
def _indices() -> tuple[dict[str, dict], dict[str, dict]]:
    """Construye {prefijo: regla} para balance y pyg."""
    bal: dict[str, dict] = {}
    pyg: dict[str, dict] = {}
    m = _mapeo()
    for regla in m["balance"]:
        for p in regla["prefijos"]:
            bal[p] = regla
    for regla in m["pyg"]:
        for p in regla["prefijos"]:
            pyg[p] = regla
    return bal, pyg


def normaliza_cuenta(cuenta: Any) -> str:
    """Deja solo digitos. Acepta '430.000.001', '4300000 01', 430000001."""
    s = str(cuenta).strip()
    return "".join(c for c in s if c.isdigit())


def grupo(cuenta: Any) -> str:
    c = normaliza_cuenta(cuenta)
    return c[0] if c else ""


def es_patrimonial(cuenta: Any) -> bool:
    """Grupos 1-5 (balance). Los grupos 6-7 son de resultados; 8-9, patrimonio
    neto (ingresos/gastos imputados directamente), que solo existen en el PGC
    normal y no se llevan a la PyG."""
    g = grupo(cuenta)
    return g in "12345"


def es_resultados(cuenta: Any) -> bool:
    return grupo(cuenta) in "67"


def es_grupo_8_9(cuenta: Any) -> bool:
    """Gastos e ingresos imputados al patrimonio neto. Su presencia indica que
    la entidad no puede estar usando el PGC PYMES simplificado sin mas."""
    return grupo(cuenta) in "89"


def _busca(cuenta: str, indice: dict[str, dict]) -> dict | None:
    c = normaliza_cuenta(cuenta)
    # prefijo mas largo primero: probamos de 5 digitos hacia abajo
    for n in range(min(5, len(c)), 1, -1):
        regla = indice.get(c[:n])
        if regla is not None:
            return regla
    return None


def epigrafe_balance(cuenta: Any) -> dict[str, Any] | None:
    bal, _ = _indices()
    return _busca(cuenta, bal)


def epigrafe_pyg(cuenta: Any) -> dict[str, Any] | None:
    _, pyg = _indices()
    return _busca(cuenta, pyg)


def clasifica(cuenta: Any) -> dict[str, Any]:
    """Devuelve masa, epigrafe, titulo y signo de una cuenta.

    Si no hay regla, devuelve estado 'SIN MAPEO' -> lo reporta ingesta como
    excepcion, nunca lo asigna a un epigrafe por aproximacion.
    """
    c = normaliza_cuenta(cuenta)
    if not c:
        return {"estado": "SIN MAPEO", "motivo": "cuenta vacia"}
    regla = epigrafe_balance(c) if es_patrimonial(c) else epigrafe_pyg(c)
    if regla is None:
        if es_grupo_8_9(c):
            return {
                "estado": "GRUPO 8/9",
                "masa": "PATRIMONIO NETO (ECPN)",
                "epigrafe": "",
                "titulo": "Ingresos/gastos imputados directamente al patrimonio neto",
                "signo": 1,
            }
        return {"estado": "SIN MAPEO", "motivo": f"sin regla para {c}"}
    return {
        "estado": "OK",
        "masa": regla.get("masa", "PYG"),
        "epigrafe": regla["epigrafe"],
        "titulo": regla["titulo"],
        "signo": regla["signo"],
    }


def reserva_restringida(cuenta: Any) -> dict[str, Any] | None:
    """Identifica reservas indisponibles/restringidas (art. 274, 273.4, 335 LSC;
    arts. 25 y 105 LIS). Prefijo mas largo primero: 1144 antes que 114."""
    c = normaliza_cuenta(cuenta)
    tabla = _mapeo()["reservas_restringidas"]
    for n in range(4, 2, -1):
        r = tabla.get(c[:n])
        if r is not None:
            return {"cuenta_pgc": c[:n], **r}
    return None
