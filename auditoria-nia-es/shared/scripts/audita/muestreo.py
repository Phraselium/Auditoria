"""Muestreo de auditoria (NIA-ES 530).

Metodos implementados:
  - MUS (unidades monetarias, seleccion sistematica con arranque aleatorio)
  - Atributos (pruebas de controles)
  - Aleatorio simple y dirigido (no estadistico)

Todo reproducible: la semilla se registra siempre en el papel de trabajo. Sin
semilla registrada la muestra no es reejecutable por un revisor, y eso la hace
indefendible ante inspeccion.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any

import pandas as pd

# Factores de fiabilidad (distribucion de Poisson) para MUS.
# Clave: riesgo de aceptacion incorrecta; valor: factor con 0 errores esperados.
FACTOR_FIABILIDAD = {0.05: 3.00, 0.10: 2.31, 0.15: 1.90, 0.20: 1.61, 0.25: 1.39}

# Incremento del factor por cada error adicional esperado.
INCREMENTO_POR_ERROR = {0.05: 1.75, 0.10: 1.55, 0.15: 1.44, 0.20: 1.36, 0.25: 1.29}

# Tamanos de muestra para pruebas de controles (frecuencia del control).
TAMANOS_CONTROLES = {
    "diaria": 25, "semanal": 15, "mensual": 5, "trimestral": 2, "anual": 1,
    "multiples_veces_dia": 40,
}


@dataclass
class Muestra:
    metodo: str
    poblacion_n: int
    poblacion_importe: float
    tamano: int
    semilla: int
    intervalo: float | None = None
    seleccion: pd.DataFrame = field(default_factory=pd.DataFrame)
    estrato_alto: pd.DataFrame = field(default_factory=pd.DataFrame)
    fundamento: str = ""
    parametros: dict[str, Any] = field(default_factory=dict)

    @property
    def cobertura(self) -> float:
        if not self.poblacion_importe:
            return 0.0
        cubierto = 0.0
        for df in (self.seleccion, self.estrato_alto):
            if not df.empty and "_importe" in df.columns:
                cubierto += float(df["_importe"].abs().sum())
        return cubierto / abs(self.poblacion_importe)

    def resumen(self) -> str:
        return (
            f"Metodo: {self.metodo} | Poblacion: {self.poblacion_n} partidas, "
            f"{self.poblacion_importe:,.2f} EUR\n"
            f"Muestra: {self.tamano} partidas"
            + (f" + {len(self.estrato_alto)} de examen individual" if not self.estrato_alto.empty else "")
            + f" | Cobertura: {self.cobertura:.1%} del importe\n"
            f"Semilla de aleatoriedad: {self.semilla} (reproducible)"
        )


def tamano_mus(poblacion_importe: float, materialidad_ejecucion: float,
               riesgo: float = 0.05, errores_esperados: int = 0) -> tuple[int, str]:
    """Tamano de muestra para muestreo por unidades monetarias.

    n = (poblacion x factor) / materialidad de ejecucion
    """
    if riesgo not in FACTOR_FIABILIDAD:
        raise ValueError(f"Riesgo no tabulado: {riesgo}. Use {sorted(FACTOR_FIABILIDAD)}")
    if materialidad_ejecucion <= 0:
        raise ValueError("La materialidad de ejecucion debe ser positiva.")
    factor = FACTOR_FIABILIDAD[riesgo] + errores_esperados * INCREMENTO_POR_ERROR[riesgo]
    n = int(-(-abs(poblacion_importe) * factor // materialidad_ejecucion))  # techo
    fundamento = (
        f"Muestreo por unidades monetarias. Tamano n = (poblacion x factor de fiabilidad) / "
        f"materialidad de ejecucion = ({abs(poblacion_importe):,.2f} x {factor:.2f}) / "
        f"{materialidad_ejecucion:,.2f} = {n} partidas. "
        f"Factor de fiabilidad {factor:.2f} correspondiente a un riesgo de aceptacion "
        f"incorrecta del {riesgo:.0%} y {errores_esperados} errores esperados. "
        f"El metodo dirige la seleccion hacia las partidas de mayor importe, que son las "
        f"que concentran el riesgo de incorreccion material por sobrevaloracion."
    )
    return max(n, 1), fundamento


def mus(df: pd.DataFrame, columna_importe: str, materialidad_ejecucion: float,
        riesgo: float = 0.05, errores_esperados: int = 0,
        semilla: int | None = None) -> Muestra:
    """Seleccion MUS sistematica con arranque aleatorio.

    Las partidas de importe superior al intervalo se seleccionan siempre
    (estrato de examen individual): no pueden no salir en la muestra.
    """
    if semilla is None:
        semilla = random.SystemRandom().randint(1, 10**6)
    datos = df.copy()
    datos["_importe"] = datos[columna_importe].astype(float)
    datos = datos[datos["_importe"].abs() > 0].reset_index(drop=True)
    total = float(datos["_importe"].abs().sum())

    n, fundamento = tamano_mus(total, materialidad_ejecucion, riesgo, errores_esperados)
    intervalo = total / n if n else total

    altos = datos[datos["_importe"].abs() >= intervalo].copy()
    resto = datos[datos["_importe"].abs() < intervalo].copy().reset_index(drop=True)

    rng = random.Random(semilla)
    seleccion = pd.DataFrame()
    if not resto.empty:
        total_resto = float(resto["_importe"].abs().sum())
        n_resto = max(int(-(-total_resto // intervalo)), 0) if intervalo else 0
        if n_resto:
            arranque = rng.uniform(0, intervalo)
            acumulado = resto["_importe"].abs().cumsum().values
            indices, objetivo = [], arranque
            for k in range(n_resto):
                pos = int((acumulado >= objetivo).argmax()) if (acumulado >= objetivo).any() else None
                if pos is None:
                    break
                indices.append(pos)
                objetivo += intervalo
            seleccion = resto.iloc[sorted(set(indices))].copy()
            seleccion["_motivo"] = "MUS sistematico"

    if not altos.empty:
        altos["_motivo"] = "Examen individual (importe >= intervalo de muestreo)"

    fundamento += (
        f"\n\nIntervalo de muestreo: {intervalo:,.2f} EUR. Las {len(altos)} partidas de "
        f"importe igual o superior al intervalo se examinan individualmente al 100%; "
        f"sobre el resto de la poblacion se aplica seleccion sistematica con arranque "
        f"aleatorio (semilla {semilla})."
    )
    return Muestra(
        metodo="MUS (unidades monetarias)", poblacion_n=len(datos),
        poblacion_importe=total, tamano=len(seleccion), semilla=semilla,
        intervalo=intervalo, seleccion=seleccion, estrato_alto=altos,
        fundamento=fundamento,
        parametros={"riesgo": riesgo, "errores_esperados": errores_esperados,
                    "materialidad_ejecucion": materialidad_ejecucion},
    )


def atributos(df: pd.DataFrame, frecuencia: str, semilla: int | None = None) -> Muestra:
    """Muestra para pruebas de controles, dimensionada por frecuencia del control."""
    frecuencia = frecuencia.lower()
    if frecuencia not in TAMANOS_CONTROLES:
        raise ValueError(f"Frecuencia no valida: {frecuencia}. "
                         f"Use {sorted(TAMANOS_CONTROLES)}")
    if semilla is None:
        semilla = random.SystemRandom().randint(1, 10**6)
    n = min(TAMANOS_CONTROLES[frecuencia], len(df))
    seleccion = df.sample(n=n, random_state=semilla).copy()
    seleccion["_motivo"] = f"Prueba de control ({frecuencia})"
    if "_importe" not in seleccion.columns:
        seleccion["_importe"] = 0.0
    return Muestra(
        metodo="Atributos (pruebas de controles)", poblacion_n=len(df),
        poblacion_importe=0.0, tamano=n, semilla=semilla, seleccion=seleccion,
        fundamento=(
            f"Prueba de controles sobre un control de operacion {frecuencia}. Tamano de "
            f"muestra {n} conforme a la tabla de tamanos minimos para desviacion esperada "
            f"nula y riesgo de confianza excesiva bajo. Seleccion aleatoria simple con "
            f"semilla {semilla}. Si se detecta una sola desviacion, no se puede confiar en "
            f"el control y hay que reconsiderar el enfoque hacia pruebas sustantivas."
        ),
        parametros={"frecuencia": frecuencia},
    )


def dirigido(df: pd.DataFrame, columna_importe: str, materialidad_ejecucion: float,
             criterios_adicionales: dict[str, Any] | None = None,
             semilla: int | None = None) -> Muestra:
    """Muestreo no estadistico dirigido: todas las partidas por encima de la
    materialidad de ejecucion, mas las que cumplan criterios cualitativos.

    Es el metodo por defecto en encargos de perfil LIGERO: mas barato que MUS y
    perfectamente defendible cuando la poblacion tiene pocas partidas y estas
    concentran el importe. NO permite extrapolar al conjunto de la poblacion:
    la conclusion se limita a lo examinado mas el analitico sobre el resto.
    """
    if semilla is None:
        semilla = random.SystemRandom().randint(1, 10**6)
    datos = df.copy()
    datos["_importe"] = datos[columna_importe].astype(float)
    total = float(datos["_importe"].abs().sum())
    sel = datos[datos["_importe"].abs() >= materialidad_ejecucion].copy()
    sel["_motivo"] = "Importe >= materialidad de ejecucion"
    if criterios_adicionales:
        for nombre, mask in criterios_adicionales.items():
            extra = datos[mask].copy()
            extra = extra[~extra.index.isin(sel.index)]
            if not extra.empty:
                extra["_motivo"] = nombre
                sel = pd.concat([sel, extra])
    cobertura = float(sel["_importe"].abs().sum()) / total if total else 0.0
    return Muestra(
        metodo="Dirigido no estadistico", poblacion_n=len(datos),
        poblacion_importe=total, tamano=len(sel), semilla=semilla,
        seleccion=sel, fundamento=(
            f"Seleccion dirigida de todas las partidas de importe igual o superior a la "
            f"materialidad de ejecucion ({materialidad_ejecucion:,.2f} EUR)"
            + (f", mas las que cumplen los criterios cualitativos: "
               f"{', '.join(criterios_adicionales)}" if criterios_adicionales else "")
            + f". Cobertura alcanzada: {cobertura:.1%} del importe de la poblacion. "
            f"Al no ser un metodo estadistico, la conclusion NO se extrapola al resto de la "
            f"poblacion; el importe no cubierto se somete a procedimientos analiticos "
            f"sustantivos con umbral de investigacion definido a priori."
        ),
        parametros={"materialidad_ejecucion": materialidad_ejecucion,
                    "cobertura": round(cobertura, 4)},
    )


def evalua(muestra: Muestra, errores: list[dict[str, Any]],
           materialidad_ejecucion: float) -> dict[str, Any]:
    """Evalua los errores encontrados y los proyecta a la poblacion.

    Para MUS: proyeccion por tasa de error sobre el importe de la partida
    (tainting) x intervalo de muestreo. Las partidas de examen individual no se
    proyectan: su error es conocido.
    """
    error_conocido = 0.0
    error_proyectado = 0.0
    detalle: list[dict[str, Any]] = []

    for e in errores:
        importe_registrado = float(e.get("importe_registrado", 0.0))
        importe_auditado = float(e.get("importe_auditado", 0.0))
        dif = importe_registrado - importe_auditado
        individual = bool(e.get("examen_individual", False))
        if individual or muestra.metodo.startswith("Dirigido"):
            error_conocido += dif
            proyectado = dif
        else:
            tainting = dif / importe_registrado if importe_registrado else 0.0
            proyectado = tainting * (muestra.intervalo or 0.0)
            error_proyectado += proyectado
        detalle.append({
            "referencia": e.get("referencia", ""),
            "descripcion": e.get("descripcion", ""),
            "registrado": round(importe_registrado, 2),
            "auditado": round(importe_auditado, 2),
            "diferencia": round(dif, 2),
            "tipo": "conocido" if individual else "proyectado",
            "proyeccion": round(proyectado, 2),
        })

    total = error_conocido + error_proyectado
    supera = abs(total) > materialidad_ejecucion
    return {
        "errores": len(errores),
        "error_conocido": round(error_conocido, 2),
        "error_proyectado": round(error_proyectado, 2),
        "error_total_estimado": round(total, 2),
        "materialidad_ejecucion": round(materialidad_ejecucion, 2),
        "supera_materialidad": supera,
        "detalle": detalle,
        "conclusion": (
            f"El error total estimado ({total:,.2f} EUR) SUPERA la materialidad de ejecucion "
            f"({materialidad_ejecucion:,.2f} EUR). La poblacion contiene una incorreccion "
            f"material. Procede: (a) ampliar la muestra, (b) aplicar procedimientos "
            f"alternativos, o (c) proponer el ajuste y solicitar a la direccion que "
            f"investigue la causa y corrija la poblacion completa."
            if supera else
            f"El error total estimado ({total:,.2f} EUR) NO supera la materialidad de "
            f"ejecucion ({materialidad_ejecucion:,.2f} EUR). La evidencia obtenida es "
            f"suficiente y apropiada para concluir que la poblacion no contiene una "
            f"incorreccion material. Las diferencias detectadas se acumulan en el sumario "
            f"de incorrecciones no corregidas."
        ),
    }
