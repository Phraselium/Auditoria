"""Registro de asistencia por herramientas automatizadas (`uso-ia.log`).

Lo exige el sistema de gestion de la calidad del despacho (NIGC1-ES) y da
estructura al uso responsable de IA en un servicio de interes publico
(ISO/IEC 42001). Sin este registro, ante una inspeccion no hay forma de
acreditar sobre que informacion se ejecuto cada calculo ni quien valido el
resultado.

Formato JSONL: una linea por ejecucion, apendable y legible por script.

Cada entrada nace con `validado_por = null`. El auditor la valida despues:

    python3 -m dula.cli validar <carpeta-encargo> --entrada <id> --quien "MJ Perez"

`revision-de-calidad` reporta como excepcion las ejecuciones sin validar cuyo
resultado se ha incorporado a un papel de trabajo concluido.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any

from .traza import huella

NOMBRE_FICHERO = "uso-ia.log"
PENDIENTE_VALIDACION = "[PENDIENTE-VALIDACION]"


def _ahora() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Bitacora:
    """Registro append-only de ejecuciones asistidas."""

    def __init__(self, carpeta: str):
        self.ruta = os.path.join(os.path.abspath(carpeta), NOMBRE_FICHERO)

    # -- escritura ---------------------------------------------------------
    def registra(self, skill: str, comando: str = "",
                 entradas: list[str] | None = None,
                 salidas: list[str] | None = None,
                 parametros: dict[str, Any] | None = None,
                 conclusion: str = "", excepciones: int = 0,
                 papel: str = "", version_plugin: str = "1.4.0") -> str:
        """Anota una ejecucion. Devuelve el id de la entrada."""
        entradas_h: list[dict[str, str]] = []
        for e in entradas or []:
            reg = {"fichero": os.path.basename(e)}
            if os.path.isfile(e):
                reg["sha256"] = huella(e)
            else:
                reg["sha256"] = PENDIENTE_VALIDACION
            entradas_h.append(reg)

        entrada = {
            "id": self._siguiente_id(),
            "momento": _ahora(),
            "version_plugin": version_plugin,
            "skill": skill,
            "comando": comando,
            "papel": papel,
            "entradas": entradas_h,
            "salidas": [os.path.basename(s) for s in (salidas or [])],
            "parametros": parametros or {},
            "conclusion": (conclusion or "")[:500],
            "excepciones": excepciones,
            "validado_por": None,
            "validado_en": None,
        }
        os.makedirs(os.path.dirname(self.ruta), exist_ok=True)
        with open(self.ruta, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entrada, ensure_ascii=False) + "\n")
        return entrada["id"]

    def _siguiente_id(self) -> str:
        return f"IA-{len(self.entradas()) + 1:04d}"

    # -- lectura -----------------------------------------------------------
    def entradas(self) -> list[dict[str, Any]]:
        if not os.path.exists(self.ruta):
            return []
        out: list[dict[str, Any]] = []
        with open(self.ruta, encoding="utf-8") as fh:
            for linea in fh:
                linea = linea.strip()
                if linea:
                    out.append(json.loads(linea))
        return out

    @property
    def sin_validar(self) -> list[dict[str, Any]]:
        return [e for e in self.entradas() if not e.get("validado_por")]

    # -- validacion --------------------------------------------------------
    def valida(self, entrada_id: str, quien: str) -> bool:
        """Marca una entrada como validada. Reescribe el fichero completo.

        No se admite validar 'todo': la validacion es un acto del auditor sobre
        un resultado concreto, y el registro debe poder acreditar cual.
        """
        entradas = self.entradas()
        encontrada = False
        for e in entradas:
            if e["id"] == entrada_id:
                e["validado_por"] = quien
                e["validado_en"] = _ahora()
                encontrada = True
        if not encontrada:
            return False
        tmp = self.ruta + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            for e in entradas:
                fh.write(json.dumps(e, ensure_ascii=False) + "\n")
        os.replace(tmp, self.ruta)
        return True

    # -- informe -----------------------------------------------------------
    def resumen(self) -> dict[str, Any]:
        entradas = self.entradas()
        return {
            "ejecuciones": len(entradas),
            "validadas": sum(1 for e in entradas if e.get("validado_por")),
            "sin_validar": sum(1 for e in entradas if not e.get("validado_por")),
            "skills_utilizadas": sorted({e["skill"] for e in entradas}),
            "papeles_afectados": sorted({e["papel"] for e in entradas if e.get("papel")}),
        }

    def informe(self) -> str:
        """Texto para el archivo del encargo."""
        entradas = self.entradas()
        if not entradas:
            return ("REGISTRO DE ASISTENCIA POR HERRAMIENTAS AUTOMATIZADAS\n\n"
                    "No consta ninguna ejecucion registrada.")
        r = self.resumen()
        lineas = [
            "REGISTRO DE ASISTENCIA POR HERRAMIENTAS AUTOMATIZADAS",
            "=" * 70,
            f"Ejecuciones registradas: {r['ejecuciones']}   "
            f"Validadas: {r['validadas']}   Sin validar: {r['sin_validar']}",
            "",
            "El trabajo se ha realizado con asistencia de herramientas automatizadas de",
            "analisis de datos y calculo, bajo la supervision y revision del equipo del",
            "encargo. Su utilizacion no altera las responsabilidades del auditor ni el",
            "alcance del trabajo.",
            "",
            f"{'ID':<9} {'FECHA':<21} {'SKILL':<28} {'PAPEL':<7} VALIDADO POR",
            "-" * 70,
        ]
        for e in entradas:
            lineas.append(
                f"{e['id']:<9} {e['momento'][:19]:<21} {e['skill'][:27]:<28} "
                f"{e.get('papel', '')[:6]:<7} {e.get('validado_por') or PENDIENTE_VALIDACION}")
        if r["sin_validar"]:
            lineas += ["", f"ATENCION: {r['sin_validar']} ejecuciones sin validar. "
                           "Toda ejecucion cuyo resultado se haya incorporado a un papel "
                           "de trabajo concluido debe estar validada por el auditor que la "
                           "revisa."]
        return "\n".join(lineas)
