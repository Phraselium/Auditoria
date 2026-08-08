"""Estado persistente del encargo (`encargo.json`).

Permite que las fases se encadenen sin repetir ingestas y que la revision de
calidad pueda auditar el archivo completo sin volver a ejecutar nada.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any

NOMBRE_FICHERO = "encargo.json"

ESTRUCTURA_CARPETAS = ("00-fuentes", "01-papeles", "02-documentos")

# Indice unico de papeles de trabajo. Aplicado por todas las skills.
INDICE_AREAS = {
    "0": "Aceptacion, independencia y carta de encargo",
    "1": "Planificacion",
    "2": "Ingesta, cuadres y comparador documental",
    "A": "Inmovilizado",
    "B": "Existencias",
    "C": "Clientes e ingresos",
    "D": "Tesoreria",
    "E": "Financiacion y deuda",
    "F": "Arrendamientos",
    "G": "Fondos propios y reservas",
    "H": "Proveedores y compras",
    "I": "Personal",
    "J": "Fiscal",
    "K": "Provisiones y contingencias",
    "L": "Subvenciones",
    "M": "Partes vinculadas",
    "N": "Hechos posteriores y empresa en funcionamiento",
    "8": "Cierre: incorrecciones, manifestaciones y comunicaciones",
    "9": "Informe y revision de calidad",
}


def _ahora() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def esqueleto(cliente: str, ejercicio: int, marco: str = "PGC-PYMES") -> dict[str, Any]:
    return {
        "version_plugin": "1.0.0",
        "creado": _ahora(),
        "actualizado": _ahora(),
        "cliente": {"nombre": cliente, "nif": "", "eip": False, "primer_encargo": False},
        "ejercicio": ejercicio,
        "marco": marco,  # PGC | PGC-PYMES | PGC-CONSOLIDADO
        "perfil": {},  # lo rellena estimacion-encargo / escalado-del-encargo
        "materialidad": [],  # versionada: [{version, fecha, magnitud, ...}]
        "riesgos": [],
        "programas": [],
        "papeles": [],
        "excepciones": [],
        "incorrecciones": [],
        "pendientes": [],  # PBC
        "fuentes": [],
        "informe": {},
        "fases": {
            "aceptacion": "pendiente",
            "planificacion": "pendiente",
            "campo": "pendiente",
            "cierre": "pendiente",
        },
    }


class Encargo:
    """Lectura/escritura del estado. Escritura atomica."""

    def __init__(self, ruta: str, datos: dict[str, Any]):
        self.ruta = ruta
        self.datos = datos

    # -- ciclo de vida -----------------------------------------------------
    @classmethod
    def crear(cls, carpeta: str, cliente: str, ejercicio: int,
              marco: str = "PGC-PYMES") -> "Encargo":
        os.makedirs(carpeta, exist_ok=True)
        for sub in ESTRUCTURA_CARPETAS:
            os.makedirs(os.path.join(carpeta, sub), exist_ok=True)
        enc = cls(os.path.join(carpeta, NOMBRE_FICHERO),
                  esqueleto(cliente, ejercicio, marco))
        enc.guardar()
        return enc

    @classmethod
    def abrir(cls, carpeta_o_fichero: str) -> "Encargo":
        ruta = carpeta_o_fichero
        if os.path.isdir(ruta):
            ruta = os.path.join(ruta, NOMBRE_FICHERO)
        with open(ruta, encoding="utf-8") as fh:
            return cls(ruta, json.load(fh))

    def guardar(self) -> None:
        self.datos["actualizado"] = _ahora()
        tmp = self.ruta + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(self.datos, fh, ensure_ascii=False, indent=2)
        os.replace(tmp, self.ruta)

    @property
    def carpeta(self) -> str:
        return os.path.dirname(os.path.abspath(self.ruta))

    # -- materialidad (versionada) ----------------------------------------
    def fija_materialidad(self, registro: dict[str, Any]) -> dict[str, Any]:
        registro = dict(registro)
        registro["version"] = len(self.datos["materialidad"]) + 1
        registro["fecha"] = _ahora()
        self.datos["materialidad"].append(registro)
        return registro

    @property
    def materialidad_vigente(self) -> dict[str, Any] | None:
        mats = self.datos.get("materialidad") or []
        return mats[-1] if mats else None

    # -- riesgos y respuestas ---------------------------------------------
    def añade_riesgo(self, **kw: Any) -> dict[str, Any]:
        r = {
            "id": kw.get("id") or f"R{len(self.datos['riesgos']) + 1:03d}",
            "area": kw["area"],
            "afirmacion": kw["afirmacion"],
            "descripcion": kw["descripcion"],
            "espectro": kw.get("espectro", "medio"),  # bajo|medio|alto (NIA-ES 315R)
            "factores": kw.get("factores", []),
            "significativo": kw.get("significativo", False),
            "fraude": kw.get("fraude", False),
            "respuestas": kw.get("respuestas", []),  # refs de papeles/programas
        }
        self.datos["riesgos"].append(r)
        return r

    add_riesgo = añade_riesgo

    def responde_riesgo(self, riesgo_id: str, ref_papel: str) -> None:
        for r in self.datos["riesgos"]:
            if r["id"] == riesgo_id and ref_papel not in r["respuestas"]:
                r["respuestas"].append(ref_papel)

    # -- papeles de trabajo -----------------------------------------------
    def registra_papel(self, ref: str, titulo: str, fichero: str = "",
                       conclusion: str = "", riesgos: list[str] | None = None,
                       estado: str = "en curso", horas: float | None = None,
                       preparado_por: str = "", revisado_por: str = "") -> dict[str, Any]:
        anterior = next((p for p in self.datos["papeles"] if p["ref"] == ref), {})
        papel = {
            "ref": ref,
            "titulo": titulo,
            "fichero": fichero,
            "conclusion": conclusion,
            "riesgos": riesgos or [],
            "estado": estado,  # en curso | concluido
            # las horas se acumulan: un area se trabaja en varias sesiones
            "horas": round(float(anterior.get("horas") or 0.0) + float(horas or 0.0), 2),
            "preparado_por": preparado_por or anterior.get("preparado_por", ""),
            "revisado_por": revisado_por or anterior.get("revisado_por", ""),
            "actualizado": _ahora(),
        }
        self.datos["papeles"] = [p for p in self.datos["papeles"] if p["ref"] != ref]
        self.datos["papeles"].append(papel)
        for rid in papel["riesgos"]:
            self.responde_riesgo(rid, ref)
        return papel

    def registra_fuente(self, path: str, huella_sha: str, descripcion: str = "") -> None:
        self.datos["fuentes"] = [
            f for f in self.datos["fuentes"] if f["fichero"] != os.path.basename(path)
        ]
        self.datos["fuentes"].append({
            "fichero": os.path.basename(path),
            "sha256": huella_sha,
            "descripcion": descripcion,
            "registrado": _ahora(),
        })

    def registra_excepciones(self, excepciones: list[Any], area: str) -> None:
        self.datos["excepciones"] = [
            e for e in self.datos["excepciones"] if e.get("area") != area
        ]
        for e in excepciones:
            self.datos["excepciones"].append(e.dict() if hasattr(e, "dict") else dict(e))

    # -- pendientes del cliente (PBC) --------------------------------------
    def añade_pendiente(self, area: str, descripcion: str, prioridad: int = 3,
                        responsable: str = "", comprometido: str = "") -> dict[str, Any]:
        """Registra un elemento de la PBC.

        Prioridad 1 = bloqueante (sin ello no hay trabajo de campo),
        2 = calendario (plazo de respuesta de terceros o fecha irrepetible),
        3 = alto impacto en horas, 4 = resto.
        """
        p = {
            "id": f"P{len(self.datos['pendientes']) + 1:03d}",
            "area": area,
            "descripcion": descripcion,
            "prioridad": int(prioridad),
            "responsable": responsable,
            "solicitado": _ahora(),
            "comprometido": comprometido,
            "estado": "pendiente",  # pendiente | recordado | recibido
            "recordatorios": 0,
        }
        self.datos["pendientes"].append(p)
        return p

    add_pendiente = añade_pendiente

    def recuerda_pendiente(self, pendiente_id: str) -> bool:
        for p in self.datos["pendientes"]:
            if p["id"] == pendiente_id:
                p["recordatorios"] += 1
                p["estado"] = "recordado"
                p["ultimo_recordatorio"] = _ahora()
                return True
        return False

    def recibe_pendiente(self, pendiente_id: str) -> bool:
        for p in self.datos["pendientes"]:
            if p["id"] == pendiente_id:
                p["estado"] = "recibido"
                p["recibido"] = _ahora()
                return True
        return False

    # -- horas -------------------------------------------------------------
    def imputa_horas(self, ref_papel: str, horas: float, quien: str = "") -> float:
        """Imputa horas a un papel. Devuelve el acumulado del papel."""
        for p in self.datos["papeles"]:
            if p["ref"] == ref_papel:
                p["horas"] = round(float(p.get("horas") or 0.0) + float(horas), 2)
                if quien and not p.get("preparado_por"):
                    p["preparado_por"] = quien
                p["actualizado"] = _ahora()
                return p["horas"]
        raise KeyError(f"No existe el papel {ref_papel}. Registrelo antes de imputar horas.")

    @property
    def horas_consumidas(self) -> float:
        return round(sum(float(p.get("horas") or 0.0)
                         for p in self.datos.get("papeles", [])), 2)

    # -- incorrecciones ----------------------------------------------------
    def añade_incorreccion(self, **kw: Any) -> dict[str, Any]:
        i = {
            "id": kw.get("id") or f"I{len(self.datos['incorrecciones']) + 1:03d}",
            "area": kw["area"],
            "descripcion": kw["descripcion"],
            "efecto_resultado": float(kw.get("efecto_resultado", 0.0)),
            "efecto_patrimonio": float(kw.get("efecto_patrimonio", 0.0)),
            "epigrafe": kw.get("epigrafe", ""),
            "tipo": kw.get("tipo", "factual"),  # factual | juicio | proyectada
            "corregida": bool(kw.get("corregida", False)),
            "ejercicio_anterior": bool(kw.get("ejercicio_anterior", False)),
            "cualitativa": kw.get("cualitativa", ""),
        }
        self.datos["incorrecciones"].append(i)
        return i

    add_incorreccion = añade_incorreccion
