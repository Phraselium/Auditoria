"""Materialidad (NIA-ES 320 y 450).

Determinacion de la magnitud de referencia y del porcentaje CON justificacion
del criterio elegido, materialidad de ejecucion graduada por perfil de riesgo,
materialidades especificas y umbral de incorrecciones claramente insignificantes.

El plugin propone; el auditor firmante decide. Toda propuesta lleva su
fundamento redactado para que un revisor externo lo reconstruya sin explicaciones.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# Rangos habituales en la practica espanola. Configurables en skills/convenciones-despacho/SKILL.md.
# No son un mandato normativo: la NIA-ES 320 no fija porcentajes.
RANGOS = {
    "resultado_antes_impuestos": (0.05, 0.10),
    "cifra_negocios": (0.005, 0.02),
    "total_activo": (0.005, 0.02),
    "patrimonio_neto": (0.01, 0.05),
    "gastos_totales": (0.005, 0.02),
}

ETIQUETAS = {
    "resultado_antes_impuestos": "Resultado antes de impuestos",
    "cifra_negocios": "Importe neto de la cifra de negocios",
    "total_activo": "Total activo",
    "patrimonio_neto": "Patrimonio neto",
    "gastos_totales": "Total gastos",
}

# Materialidad de ejecucion segun perfil de riesgo del encargo.
MP_POR_PERFIL = {"LIGERO": 0.75, "ESTANDAR": 0.65, "COMPLEJO": 0.55}

# Umbral de incorrecciones claramente insignificantes: % de la materialidad global.
PCT_INSIGNIFICANTE = 0.05


@dataclass
class Materialidad:
    magnitud: str
    valor_magnitud: float
    porcentaje: float
    global_: float
    ejecucion: float
    insignificante: float
    perfil: str
    fundamento: str
    especificas: dict[str, float] = field(default_factory=dict)
    traza: str = ""

    def dict(self) -> dict[str, Any]:
        return {
            "magnitud": self.magnitud,
            "etiqueta": ETIQUETAS.get(self.magnitud, self.magnitud),
            "valor_magnitud": round(self.valor_magnitud, 2),
            "porcentaje": self.porcentaje,
            "global": round(self.global_, 2),
            "ejecucion": round(self.ejecucion, 2),
            "insignificante": round(self.insignificante, 2),
            "perfil": self.perfil,
            "fundamento": self.fundamento,
            "especificas": {k: round(v, 2) for k, v in self.especificas.items()},
            "traza": self.traza,
        }

    def resumen(self) -> str:
        return (
            f"Magnitud: {ETIQUETAS.get(self.magnitud, self.magnitud)} = "
            f"{self.valor_magnitud:,.2f} EUR\n"
            f"Porcentaje aplicado: {self.porcentaje:.2%}\n"
            f"Materialidad global (MG): {self.global_:,.2f} EUR\n"
            f"Materialidad de ejecucion (MP): {self.ejecucion:,.2f} EUR "
            f"({MP_POR_PERFIL[self.perfil]:.0%} de MG, perfil {self.perfil})\n"
            f"Umbral de incorrecciones claramente insignificantes: "
            f"{self.insignificante:,.2f} EUR"
        )


def elige_magnitud(cifras: dict[str, float], entidad_con_beneficio_estable: bool = True,
                   proxima_a_perdidas: bool = False) -> tuple[str, str]:
    """Elige la magnitud de referencia y explica por que.

    Criterio: el resultado antes de impuestos es la magnitud preferente cuando
    la entidad tiene animo de lucro y el resultado es estable y significativo.
    Se descarta cuando es volatil, proximo a cero o negativo, porque produce una
    materialidad artificialmente baja que dispara el alcance sin ganar calidad.
    """
    rai = cifras.get("resultado_antes_impuestos", 0.0)
    inc = cifras.get("cifra_negocios", 0.0)
    activo = cifras.get("total_activo", 0.0)

    if rai > 0 and inc > 0 and abs(rai) / inc >= 0.02 and \
            entidad_con_beneficio_estable and not proxima_a_perdidas:
        return "resultado_antes_impuestos", (
            "Se toma el resultado antes de impuestos como magnitud de referencia por ser "
            "una entidad con animo de lucro cuyo resultado es positivo, estable y "
            "significativo respecto de la cifra de negocios "
            f"({abs(rai) / inc:.1%}), y por ser la magnitud en la que se centra el interes "
            "de los usuarios de las cuentas anuales."
        )
    if inc > 0 and (rai <= 0 or (inc and abs(rai) / inc < 0.02) or proxima_a_perdidas):
        motivo = ("el resultado del ejercicio es negativo" if rai < 0
                  else "el resultado se situa proximo al umbral de perdidas"
                  if proxima_a_perdidas or (inc and abs(rai) / inc < 0.02)
                  else "el resultado es volatil")
        return "cifra_negocios", (
            f"Se descarta el resultado antes de impuestos porque {motivo}, lo que produciria "
            "una materialidad anormalmente baja y no representativa. Se toma el importe neto "
            "de la cifra de negocios por ser una magnitud estable y representativa del "
            "volumen de actividad de la entidad."
        )
    if activo > 0:
        return "total_activo", (
            "Se toma el total activo como magnitud de referencia por tratarse de una entidad "
            "sin actividad ordinaria relevante en el ejercicio o de caracter patrimonial, "
            "siendo el activo la magnitud de mayor interes para los usuarios."
        )
    raise ValueError("No hay magnitud valida: revise las cifras aportadas.")


def calcula(cifras: dict[str, float], perfil: str = "ESTANDAR",
            magnitud: str | None = None, porcentaje: float | None = None,
            traza: str = "", **kw: Any) -> Materialidad:
    """Calcula la materialidad. Todo determinista.

    `perfil` gradua la materialidad de ejecucion: a mayor riesgo, menor MP.
    """
    perfil = perfil.upper()
    if perfil not in MP_POR_PERFIL:
        raise ValueError(f"Perfil no valido: {perfil}")

    if magnitud is None:
        magnitud, fundamento_mag = elige_magnitud(cifras, **kw)
    else:
        fundamento_mag = (f"Magnitud fijada manualmente por el auditor: "
                          f"{ETIQUETAS.get(magnitud, magnitud)}.")
    if magnitud not in cifras:
        raise ValueError(f"No se ha aportado el valor de la magnitud '{magnitud}'.")

    valor = abs(float(cifras[magnitud]))
    minimo, maximo = RANGOS[magnitud]
    if porcentaje is None:
        # Dentro del rango: extremo bajo si el riesgo es alto, alto si es bajo.
        posicion = {"LIGERO": 1.0, "ESTANDAR": 0.5, "COMPLEJO": 0.0}[perfil]
        porcentaje = minimo + (maximo - minimo) * posicion
        fundamento_pct = (
            f"Se aplica el {porcentaje:.2%}, dentro del rango habitual del "
            f"{minimo:.2%}-{maximo:.2%} para esta magnitud, situado en el "
            f"{'extremo superior' if posicion > 0.6 else 'extremo inferior' if posicion < 0.4 else 'punto medio'} "
            f"del rango por corresponder a un encargo de perfil {perfil}, en el que el "
            f"riesgo global valorado es {'bajo' if perfil == 'LIGERO' else 'alto' if perfil == 'COMPLEJO' else 'medio'}."
        )
    else:
        fundamento_pct = f"Porcentaje fijado manualmente por el auditor: {porcentaje:.2%}."

    mg = valor * porcentaje
    factor_mp = MP_POR_PERFIL[perfil]
    mp = mg * factor_mp
    insignif = mg * PCT_INSIGNIFICANTE

    fundamento = (
        f"{fundamento_mag}\n\n{fundamento_pct}\n\n"
        f"Materialidad de ejecucion: se fija en el {factor_mp:.0%} de la materialidad "
        f"global, para reducir a un nivel aceptablemente bajo la probabilidad de que el "
        f"conjunto de incorrecciones no corregidas y no detectadas supere la materialidad "
        f"global. El porcentaje responde al perfil {perfil} del encargo "
        f"{'(riesgo bajo, poblaciones homogeneas y sin incorrecciones relevantes en ejercicios anteriores)' if perfil == 'LIGERO' else '(riesgo alto, mayor expectativa de incorrecciones)' if perfil == 'COMPLEJO' else '(riesgo medio)'}.\n\n"
        f"Umbral de incorrecciones claramente insignificantes: {PCT_INSIGNIFICANTE:.0%} de "
        f"la materialidad global. Las incorrecciones por debajo de este importe no se "
        f"acumulan en el sumario, salvo que por su naturaleza sean cualitativamente "
        f"significativas."
    )

    return Materialidad(
        magnitud=magnitud, valor_magnitud=valor, porcentaje=porcentaje,
        global_=mg, ejecucion=mp, insignificante=insignif, perfil=perfil,
        fundamento=fundamento, traza=traza,
    )


def especifica(mat: Materialidad, area: str, motivo: str,
               factor: float = 0.5) -> Materialidad:
    """Materialidad especifica mas baja para areas sensibles (NIA-ES 320.10).

    Casos tipicos: retribuciones a la direccion y operaciones con partes
    vinculadas (por expectativa del usuario, no por importe), y cualquier
    partida cuyo desglose sea legalmente exigido.
    """
    mat.especificas[area] = mat.global_ * factor
    mat.fundamento += (
        f"\n\nMaterialidad especifica para {area}: {mat.global_ * factor:,.2f} EUR "
        f"({factor:.0%} de la materialidad global). Motivo: {motivo}"
    )
    return mat


def evalua_recalculo(anterior: dict[str, Any], nueva: Materialidad) -> dict[str, Any]:
    """Recalculo al cierre. Alerta si el cambio afecta al alcance ya ejecutado.

    Lo relevante no es que cambie la materialidad, sino que BAJE: si la
    materialidad de ejecucion final es menor que la usada para dimensionar las
    muestras, el trabajo ejecutado se queda corto.
    """
    mp_ant = float(anterior.get("ejecucion", 0.0))
    variacion = (nueva.ejecucion - mp_ant) / mp_ant if mp_ant else 0.0
    afecta = nueva.ejecucion < mp_ant * 0.95
    return {
        "mp_anterior": round(mp_ant, 2),
        "mp_nueva": round(nueva.ejecucion, 2),
        "variacion": round(variacion, 4),
        "afecta_alcance": afecta,
        "mensaje": (
            f"ALERTA: la materialidad de ejecucion baja un {abs(variacion):.1%} "
            f"(de {mp_ant:,.2f} a {nueva.ejecucion:,.2f} EUR). Los tamanos de muestra y los "
            "umbrales de investigacion analitica calculados con la materialidad anterior "
            "quedan por debajo de lo necesario. Hay que reevaluar el alcance de las pruebas "
            "ya ejecutadas y, en su caso, ampliarlas."
            if afecta else
            f"La materialidad de ejecucion pasa de {mp_ant:,.2f} a {nueva.ejecucion:,.2f} EUR "
            f"({variacion:+.1%}). No reduce el alcance ya ejecutado; no requiere ampliacion."
        ),
    }
