"""Localizacion de los ficheros de referencia y de las plantillas.

La misma libreria se distribuye de dos formas, y en cada una los ficheros de
apoyo cuelgan de un sitio distinto:

  Plugin de Claude Code   <raiz>/shared/references/   <raiz>/shared/templates/
  Paquete de claude.ai    <raiz>/referencias/         <raiz>/plantillas/

En lugar de duplicar la libreria, se resuelve la ruta en tiempo de ejecucion:
primero `DULA_RAIZ` (que exporta el lanzador), y si no, deduciendola desde la
ubicacion del propio modulo. Si no se encuentra, se dice donde se ha buscado en
lugar de fallar con un fichero no encontrado a secas.
"""

from __future__ import annotations

import functools
import os

# nombres admitidos, en orden de preferencia, para cada tipo de recurso
NOMBRES = {
    "referencias": (os.path.join("shared", "references"), "referencias", "references"),
    "plantillas": (os.path.join("shared", "templates"), "plantillas", "templates"),
}


def raices_candidatas() -> list[str]:
    """Posibles raices de la distribucion, de mas a menos fiable."""
    out: list[str] = []
    env = os.environ.get("DULA_RAIZ")
    if env:
        out.append(os.path.abspath(env))
    # .../<raiz>/shared/scripts/dula/rutas.py  -> cuatro niveles
    # .../<raiz>/scripts/dula/rutas.py         -> tres niveles
    aqui = os.path.dirname(os.path.abspath(__file__))
    out.append(os.path.abspath(os.path.join(aqui, "..", "..", "..")))
    out.append(os.path.abspath(os.path.join(aqui, "..", "..")))
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
        + "\n\nSi la libreria esta en una ubicacion no habitual, exporte DULA_RAIZ "
          "apuntando a la raiz de la distribucion.")


def fichero(recurso: str, nombre: str) -> str:
    return os.path.join(directorio(recurso), nombre)
