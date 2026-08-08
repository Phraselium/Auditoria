"""Localizacion de los ficheros de referencia y de las plantillas.

Las dos distribuciones —plugin de Claude Code y paquete de claude.ai— tienen la
misma disposicion, asi que la regla es una sola:

  <raiz>/scripts/audita/   la libreria
  <raiz>/referencias/      mapeo del PGC, desgloses de memoria, programas
  <raiz>/plantillas/       informe, cartas y comunicaciones

La ruta se resuelve en tiempo de ejecucion: primero `AUDITA_RAIZ` (que exporta
el lanzador), y si no, deduciendola desde la ubicacion del propio modulo. Si no
se encuentra, se dice donde se ha buscado en lugar de fallar con un fichero no
encontrado a secas.
"""

from __future__ import annotations

import functools
import os

# nombres admitidos, en orden de preferencia, para cada tipo de recurso
NOMBRES = {
    "referencias": ("referencias", "references"),
    "plantillas": ("plantillas", "templates"),
}


def raices_candidatas() -> list[str]:
    """Posibles raices de la distribucion, de mas a menos fiable."""
    out: list[str] = []
    env = os.environ.get("AUDITA_RAIZ")
    if env:
        out.append(os.path.abspath(env))
    # .../<raiz>/scripts/audita/rutas.py -> dos niveles hasta la raiz
    aqui = os.path.dirname(os.path.abspath(__file__))
    out.append(os.path.abspath(os.path.join(aqui, "..", "..")))
    # tolerancia por si la libreria se instala un nivel mas adentro
    out.append(os.path.abspath(os.path.join(aqui, "..", "..", "..")))
    vistos: set[str] = set()
    return [r for r in out if not (r in vistos or vistos.add(r))]


@functools.lru_cache(maxsize=4)
def directorio(recurso: str) -> str:
    """Devuelve el directorio de `referencias` o `plantillas`."""
    if recurso not in NOMBRES:
        raise ValueError(f"Recurso desconocido: {recurso}")
    intentos: list[str] = []
    for raiz in raices_candidatas():
        for nombre in NOMBRES[recurso]:
            ruta = os.path.join(raiz, nombre)
            intentos.append(ruta)
            if os.path.isdir(ruta):
                return ruta
    raise FileNotFoundError(
        f"No se encuentra el directorio de {recurso}. Se ha buscado en:\n  "
        + "\n  ".join(intentos)
        + "\n\nSi la libreria esta en una ubicacion no habitual, exporte AUDITA_RAIZ "
          "apuntando a la raiz de la distribucion.")


def fichero(recurso: str, nombre: str) -> str:
    return os.path.join(directorio(recurso), nombre)
