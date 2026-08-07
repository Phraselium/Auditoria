"""Arrendamientos (PGC NRV 8ª / PGC PYMES NRV 7ª).

Procesa lotes de cientos de contratos heterogeneos:
  1. Normaliza los terminos extraidos (columnas con cualquier nombre).
  2. Calcula el tipo de interes implicito (TIE) por biseccion, sin dependencias.
  3. Clasifica financiero/operativo con motivacion indicador a indicador.
  4. Construye o valida el cuadro de cuotas y la periodificacion de la carga
     financiera.
  5. Reparte corriente / no corriente a la fecha de cierre.
  6. Compara con la contabilidad y reporta SOLO las diferencias.

Objetivo declarado: convertir 3 dias de trabajo en unas horas. Lo que el script
no puede hacer -leer un contrato escaneado con garantias- se marca por confianza
y va a revision humana.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pandas as pd

from .excepciones import DOCUMENTAR, INFORMATIVA, RESOLVER, Excepcion, Resultado
from .ingesta import columna, num

PERIODOS_ANO = {"mensual": 12, "bimestral": 6, "trimestral": 4,
                "cuatrimestral": 3, "semestral": 2, "anual": 1}

# Tolerancias configurables (skills/convenciones-dula/SKILL.md).
TOL_IMPORTE = 1.00        # EUR de diferencia admitida en cuadres de contrato
TOL_TIPO = 0.0025         # 0,25 p.p. entre el TIE calculado y el declarado

# Umbrales de los indicadores de clasificacion. No son reglas legales rigidas:
# la NRV 8ª habla de "no existan dudas razonables". Se usan como indicio
# motivado, y el caso dudoso se eleva a juicio del auditor.
UMBRAL_VIDA_UTIL = 0.75   # plazo / vida util
UMBRAL_VALOR_ACTUAL = 0.90  # VA de pagos minimos / valor razonable
UMBRAL_OPCION_BAJA = 0.50  # opcion / cuota: opcion "claramente inferior"


# ---------------------------------------------------------------------------
# Matematica financiera (determinista, sin dependencias externas)
# ---------------------------------------------------------------------------
def van(tasa: float, flujos: list[tuple[float, float]]) -> float:
    """Valor actual de una lista de (periodo, importe). Periodo 0 = hoy."""
    return sum(imp / (1.0 + tasa) ** t for t, imp in flujos)


def tir(flujos: list[tuple[float, float]], minimo: float = -0.99,
        maximo: float = 10.0, precision: float = 1e-10,
        max_iter: int = 300) -> float | None:
    """TIR por biseccion. Devuelve la tasa POR PERIODO.

    Biseccion en lugar de Newton: no necesita derivada, no diverge y en 300
    iteraciones da precision suficiente para 2 decimales de tipo anual.
    """
    f_min, f_max = van(minimo, flujos), van(maximo, flujos)
    if f_min * f_max > 0:
        return None  # no hay cambio de signo: no existe TIR en el intervalo
    a, b = minimo, maximo
    for _ in range(max_iter):
        c = (a + b) / 2.0
        fc = van(c, flujos)
        if abs(fc) < precision or (b - a) / 2.0 < precision:
            return c
        if van(a, flujos) * fc < 0:
            b = c
        else:
            a = c
    return (a + b) / 2.0


def tipo_implicito(importe_financiado: float, cuota: float, n_cuotas: int,
                   opcion_compra: float = 0.0, periodos_ano: int = 12,
                   anticipado: bool = False) -> tuple[float | None, float | None]:
    """Tipo implicito del arrendamiento. Devuelve (tasa_periodo, tasa_anual).

    Planteamiento: el importe financiado es el valor actual de los pagos minimos
    (cuotas + opcion de compra, cuando no hay dudas razonables de que se
    ejercitara).
    """
    if importe_financiado <= 0 or cuota <= 0 or n_cuotas <= 0:
        return None, None
    flujos: list[tuple[float, float]] = [(0.0, -importe_financiado)]
    desplazamiento = 0 if anticipado else 1
    for k in range(n_cuotas):
        flujos.append((float(k + desplazamiento), cuota))
    if opcion_compra:
        flujos.append((float(n_cuotas - 1 + desplazamiento), opcion_compra))
    tasa = tir(flujos)
    if tasa is None:
        return None, None
    return tasa, (1.0 + tasa) ** periodos_ano - 1.0


def cuadro_amortizacion(importe_financiado: float, cuota: float, n_cuotas: int,
                        fecha_inicio: pd.Timestamp, periodicidad: str = "mensual",
                        opcion_compra: float = 0.0, anticipado: bool = False,
                        tasa_periodo: float | None = None) -> pd.DataFrame:
    """Cuadro de cuotas periodo a periodo: cuota, interes, amortizacion, deuda viva.

    Si no se pasa `tasa_periodo`, se calcula el implicito. El ultimo periodo
    absorbe el redondeo para que la deuda viva final sea exactamente cero.
    """
    pa = PERIODOS_ANO.get(str(periodicidad).lower(), 12)
    if tasa_periodo is None:
        tasa_periodo, _ = tipo_implicito(importe_financiado, cuota, n_cuotas,
                                         opcion_compra, pa, anticipado)
    if tasa_periodo is None:
        tasa_periodo = 0.0

    meses_paso = 12 // pa
    filas: list[dict[str, Any]] = []
    pendiente = float(importe_financiado)
    for k in range(1, n_cuotas + 1):
        fecha = fecha_inicio + pd.DateOffset(months=meses_paso * (k - 1 if anticipado else k))
        if anticipado:
            interes = round((pendiente - cuota) * tasa_periodo, 2) if k > 1 else 0.0
            amortiza = round(cuota - interes, 2)
        else:
            interes = round(pendiente * tasa_periodo, 2)
            amortiza = round(cuota - interes, 2)
        es_ultima = (k == n_cuotas)
        if es_ultima:
            # el ultimo periodo cancela el pendiente (mas la opcion si procede)
            amortiza = round(pendiente - (opcion_compra if opcion_compra else 0.0), 2)
            interes = round(cuota - amortiza, 2)
        pendiente = round(pendiente - amortiza, 2)
        filas.append({
            "periodo": k,
            "fecha": fecha,
            "ejercicio": fecha.year,
            "cuota": round(cuota, 2),
            "interes": interes,
            "amortizacion_capital": amortiza,
            "deuda_viva": max(pendiente, 0.0),
        })
    if opcion_compra:
        fecha = filas[-1]["fecha"]
        filas.append({
            "periodo": n_cuotas + 1,
            "fecha": fecha,
            "ejercicio": fecha.year,
            "cuota": round(opcion_compra, 2),
            "interes": 0.0,
            "amortizacion_capital": round(opcion_compra, 2),
            "deuda_viva": 0.0,
        })
    return pd.DataFrame(filas)


# ---------------------------------------------------------------------------
# Clasificacion financiero / operativo
# ---------------------------------------------------------------------------
@dataclass
class Clasificacion:
    tipo: str                       # FINANCIERO | OPERATIVO | DUDOSO
    indicadores: list[str] = field(default_factory=list)
    motivacion: str = ""
    requiere_juicio: bool = False


def clasifica_contrato(c: dict[str, Any]) -> Clasificacion:
    """Clasificacion motivada segun los indicadores de la NRV 8ª del PGC.

    Basta que concurra UNO de los indicadores para presumir arrendamiento
    financiero. Cuando no concurre ninguno pero falta informacion para
    descartarlos, se devuelve DUDOSO y se eleva al auditor: nunca se clasifica
    como operativo por defecto solo porque falten datos.
    """
    ind: list[str] = []
    faltan: list[str] = []

    if c.get("transferencia_propiedad"):
        ind.append("El contrato transfiere la propiedad del activo al arrendatario al "
                   "finalizar el plazo.")

    opcion = float(c.get("opcion_compra") or 0.0)
    cuota = float(c.get("cuota") or 0.0)
    vr = float(c.get("valor_razonable") or 0.0)
    if opcion and cuota and opcion <= cuota * (1 + UMBRAL_OPCION_BAJA):
        ind.append(
            f"El precio de la opcion de compra ({opcion:,.2f} EUR) es equivalente o "
            f"inferior a una cuota periodica ({cuota:,.2f} EUR), por lo que en la fecha de "
            "inicio no existen dudas razonables de que sera ejercitada."
        )

    plazo_anos = float(c.get("plazo_meses") or 0) / 12.0
    vida_util = float(c.get("vida_util_anos") or 0.0)
    if plazo_anos and vida_util:
        ratio = plazo_anos / vida_util
        if ratio >= UMBRAL_VIDA_UTIL:
            ind.append(
                f"El plazo del contrato ({plazo_anos:.1f} anos) cubre el {ratio:.0%} de la "
                f"vida economica del activo ({vida_util:.1f} anos), esto es, la mayor parte "
                "de la misma."
            )
    elif plazo_anos:
        faltan.append("vida util del activo")

    va = float(c.get("valor_actual_pagos") or c.get("importe_financiado") or 0.0)
    if va and vr:
        ratio_vr = va / vr
        if ratio_vr >= UMBRAL_VALOR_ACTUAL:
            ind.append(
                f"El valor actual de los pagos minimos ({va:,.2f} EUR) supone el "
                f"{ratio_vr:.0%} del valor razonable del activo ({vr:,.2f} EUR), "
                "practicamente su totalidad."
            )
    elif va:
        faltan.append("valor razonable del activo en el origen")

    if c.get("activo_especializado"):
        ind.append("El activo es de naturaleza tan especializada que solo el arrendatario "
                   "puede utilizarlo sin realizar modificaciones importantes.")

    if ind:
        motivacion = (
            "Se clasifica como ARRENDAMIENTO FINANCIERO. Concurren los siguientes "
            "indicadores de transferencia sustancial de los riesgos y beneficios inherentes "
            "a la propiedad (NRV 8ª PGC):\n- " + "\n- ".join(ind) +
            "\nBasta la concurrencia de uno de ellos para la calificacion."
        )
        return Clasificacion("FINANCIERO", ind, motivacion)

    if faltan:
        motivacion = (
            "CLASIFICACION NO CONCLUIDA. No concurre ninguno de los indicadores verificables "
            "con la informacion disponible, pero falta el dato de: "
            + ", ".join(sorted(set(faltan))) +
            ". No se clasifica como operativo por defecto: se requiere completar la "
            "informacion o el juicio del auditor sobre la sustancia del contrato."
        )
        return Clasificacion("DUDOSO", ind, motivacion, requiere_juicio=True)

    return Clasificacion("OPERATIVO", ind, (
        "Se clasifica como ARRENDAMIENTO OPERATIVO. No concurre ninguno de los indicadores "
        "de la NRV 8ª PGC: no hay transferencia de propiedad ni opcion de compra en "
        "condiciones que hagan razonablemente cierta su ejecucion, el plazo no cubre la mayor "
        "parte de la vida economica del activo, el valor actual de los pagos minimos es "
        "sustancialmente inferior a su valor razonable y el activo no es de naturaleza "
        "especializada. No se transfieren sustancialmente los riesgos y beneficios inherentes "
        "a la propiedad."
    ))


# ---------------------------------------------------------------------------
# Normalizacion del lote
# ---------------------------------------------------------------------------
CANONICAS = {"id", "entidad", "importe_financiado", "plazo_meses", "cuota",
             "periodicidad", "opcion_compra", "tipo_declarado"}


def normaliza_lote(df: pd.DataFrame) -> pd.DataFrame:
    """Mapea las columnas del fichero de contratos, se llamen como se llamen.

    Es idempotente: si recibe un lote ya normalizado (caso habitual cuando se
    consolidan varios ficheros de entidades distintas antes de procesarlos), lo
    devuelve tal cual en lugar de volver a mapear y perder campos.
    """
    if CANONICAS <= set(df.columns):
        out = df.copy()
        if "_fila_origen" not in out.columns:
            out["_fila_origen"] = range(2, len(out) + 2)
        return out
    m = {
        "id": columna(df, "id", "contrato", "n contrato", "referencia", "num", "codigo"),
        "entidad": columna(df, "entidad", "arrendador", "banco", "financiera", "acreedor"),
        "activo": columna(df, "activo", "bien", "descripcion", "matricula", "elemento"),
        "fecha_inicio": columna(df, "fecha inicio", "inicio", "fecha contrato", "fecha"),
        "importe_financiado": columna(df, "importe financiado", "principal", "nominal",
                                      "capital", "importe", "financiado"),
        "plazo_meses": columna(df, "plazo meses", "plazo", "n cuotas", "cuotas",
                               "numero cuotas", "meses"),
        "cuota": columna(df, "cuota", "cuota periodica", "importe cuota", "mensualidad"),
        "periodicidad": columna(df, "periodicidad", "frecuencia"),
        "tipo_declarado": columna(df, "tipo interes", "tin", "interes", "tipo nominal"),
        "opcion_compra": columna(df, "opcion compra", "opcion de compra", "residual",
                                 "valor residual", "vr"),
        "valor_razonable": columna(df, "valor razonable", "valor contado", "precio contado",
                                   "valor mercado"),
        "vida_util_anos": columna(df, "vida util", "vida util anos", "vida"),
        "gastos_iniciales": columna(df, "gastos iniciales", "comision apertura", "gastos"),
        "confianza": columna(df, "confianza", "confidence", "fiabilidad"),
        "transferencia_propiedad": columna(df, "transferencia propiedad", "transfiere"),
        "activo_especializado": columna(df, "especializado", "activo especializado"),
        "saldo_contable": columna(df, "saldo contable", "contabilidad", "saldo cont"),
    }
    out = pd.DataFrame(index=df.index)
    out["id"] = (df[m["id"]].astype(str).str.strip() if m["id"]
                 else [f"CTO-{i + 1:04d}" for i in range(len(df))])
    out["entidad"] = df[m["entidad"]].astype(str).str.strip() if m["entidad"] else ""
    out["activo"] = df[m["activo"]].astype(str).str.strip() if m["activo"] else ""
    out["fecha_inicio"] = (pd.to_datetime(df[m["fecha_inicio"]], errors="coerce",
                                          dayfirst=True)
                           if m["fecha_inicio"] else pd.NaT)
    for campo in ("importe_financiado", "cuota", "opcion_compra", "valor_razonable",
                  "gastos_iniciales", "saldo_contable"):
        out[campo] = num(df, m[campo])
    out["plazo_meses"] = num(df, m["plazo_meses"]).round().astype(int)
    out["vida_util_anos"] = num(df, m["vida_util_anos"])
    out["tipo_declarado"] = num(df, m["tipo_declarado"])
    # tipos declarados en % (5,25) o en tanto por uno (0,0525)
    out["tipo_declarado"] = out["tipo_declarado"].where(
        out["tipo_declarado"] < 1, out["tipo_declarado"] / 100.0)
    out["periodicidad"] = (df[m["periodicidad"]].astype(str).str.strip().str.lower()
                           if m["periodicidad"] else "mensual")
    out["periodicidad"] = out["periodicidad"].where(
        out["periodicidad"].isin(PERIODOS_ANO), "mensual")
    out["confianza"] = num(df, m["confianza"]).replace(0.0, 1.0) if m["confianza"] else 1.0

    def _bool(col: str | None) -> pd.Series:
        if not col:
            return pd.Series([False] * len(df), index=df.index)
        return df[col].astype(str).str.strip().str.lower().isin(
            {"si", "sí", "s", "true", "1", "x", "yes"})

    out["transferencia_propiedad"] = _bool(m["transferencia_propiedad"])
    out["activo_especializado"] = _bool(m["activo_especializado"])
    out["_fila_origen"] = df["_fila_origen"] if "_fila_origen" in df.columns else range(2, len(df) + 2)
    return out


# ---------------------------------------------------------------------------
# Motor de lote
# ---------------------------------------------------------------------------
def procesa_lote(df_contratos: pd.DataFrame, fecha_cierre: str | pd.Timestamp,
                 fichero_origen: str = "contratos",
                 tol_importe: float = TOL_IMPORTE,
                 tol_tipo: float = TOL_TIPO) -> tuple[Resultado, pd.DataFrame, pd.DataFrame]:
    """Procesa el lote completo.

    Devuelve (Resultado con excepciones, resumen por contrato, cuadro consolidado
    por contrato y ejercicio).
    """
    cierre = pd.Timestamp(fecha_cierre)
    datos = normaliza_lote(df_contratos)
    res = Resultado("Arrendamientos - proceso en lote")

    resumen: list[dict[str, Any]] = []
    cuadros: list[pd.DataFrame] = []

    for _, c in datos.iterrows():
        cid = c["id"]
        fila = int(c["_fila_origen"])
        origen = f"{fichero_origen} fila {fila}"

        # --- validaciones de entrada (no se calcula sobre datos ausentes) ---
        if c["importe_financiado"] <= 0 or c["cuota"] <= 0 or c["plazo_meses"] <= 0:
            res.add(Excepcion(
                "ARR-001", RESOLVER, "F",
                f"Contrato {cid}: faltan datos esenciales (importe financiado "
                f"{c['importe_financiado']:,.2f}, cuota {c['cuota']:,.2f}, plazo "
                f"{c['plazo_meses']}). No se ha calculado.",
                cuenta=None, origen=origen,
                causa_sugerida="Extraccion incompleta del contrato o del cuadro de la entidad.",
                accion="Solicitar el cuadro de amortizacion de la entidad financiera.",
            ))
            resumen.append({"id": cid, "entidad": c["entidad"], "estado": "SIN CALCULAR",
                            "clasificacion": "[PENDIENTE-CLIENTE]"})
            continue

        if c["confianza"] < 0.85:
            res.add(Excepcion(
                "ARR-002", RESOLVER, "F",
                f"Contrato {cid}: la extraccion documental tiene confianza "
                f"{c['confianza']:.0%}, por debajo del umbral. Los terminos deben "
                "verificarse contra el contrato original.",
                origen=origen, causa_sugerida="Documento escaneado de baja calidad.",
                accion="Verificacion documental completa por el auditor.",
            ))

        pa = PERIODOS_ANO[c["periodicidad"]]
        # El campo de plazo se informa en meses; con periodicidad mensual coincide
        # con el numero de cuotas, y con cualquier otra se convierte.
        n_cuotas = max(int(round(c["plazo_meses"] * pa / 12)), 1)

        # Coherencia financiera basica: la suma de los pagos minimos tiene que
        # superar el importe financiado. Si no, los datos son incompatibles entre
        # si y cualquier tipo implicito que se calculara seria ficticio (la
        # biseccion encontraria una tasa negativa sin sentido economico).
        total_pagos = round(float(c["cuota"]) * n_cuotas + float(c["opcion_compra"]), 2)
        if total_pagos <= float(c["importe_financiado"]):
            res.add(Excepcion(
                "ARR-003", RESOLVER, "F",
                f"Contrato {cid}: la suma de los pagos minimos ({total_pagos:,.2f} EUR: "
                f"{n_cuotas} cuotas de {c['cuota']:,.2f} mas opcion de "
                f"{c['opcion_compra']:,.2f}) no supera el importe financiado "
                f"({c['importe_financiado']:,.2f} EUR), lo que es financieramente "
                "imposible en un arrendamiento con carga financiera positiva.",
                importe=round(total_pagos - float(c["importe_financiado"]), 2),
                origen=origen,
                causa_sugerida="Confusion entre importe financiado y valor total del bien, "
                               "cuota extraida sin IVA frente a importe con IVA, o plazo "
                               "informado en anos en lugar de meses.",
                accion="Contrastar contra el cuadro de amortizacion de la entidad "
                       "financiera antes de recalcular.",
            ))
            resumen.append({"id": cid, "entidad": c["entidad"], "estado": "INCOHERENTE",
                            "clasificacion": "[JUICIO-AUDITOR]"})
            continue

        tasa_p, tasa_anual = tipo_implicito(
            float(c["importe_financiado"]), float(c["cuota"]), n_cuotas,
            float(c["opcion_compra"]), pa)

        if tasa_p is None:
            res.add(Excepcion(
                "ARR-004", RESOLVER, "F",
                f"Contrato {cid}: no ha sido posible determinar el tipo de interes "
                "implicito a partir de los terminos extraidos.",
                origen=origen,
                causa_sugerida="Combinacion de terminos incompatible entre si.",
                accion="Contrastar contra el cuadro de amortizacion de la entidad.",
            ))
            resumen.append({"id": cid, "entidad": c["entidad"], "estado": "INCOHERENTE",
                            "clasificacion": "[JUICIO-AUDITOR]"})
            continue

        # --- clasificacion ---
        clasif = clasifica_contrato({
            "transferencia_propiedad": bool(c["transferencia_propiedad"]),
            "opcion_compra": float(c["opcion_compra"]),
            "cuota": float(c["cuota"]),
            "valor_razonable": float(c["valor_razonable"]),
            "plazo_meses": int(c["plazo_meses"]),
            "vida_util_anos": float(c["vida_util_anos"]),
            "importe_financiado": float(c["importe_financiado"]),
            "activo_especializado": bool(c["activo_especializado"]),
        })
        if clasif.requiere_juicio:
            res.add(Excepcion(
                "ARR-010", RESOLVER, "F",
                f"Contrato {cid}: clasificacion financiero/operativo no concluida. "
                f"{clasif.motivacion}",
                origen=origen,
                causa_sugerida="Falta informacion sobre vida util o valor razonable del bien.",
                accion="Obtener el dato o documentar el juicio del auditor sobre la sustancia.",
                referencia_normativa="NRV 8ª PGC",
            ))

        # --- cuadro y reparto ---
        cuadro = cuadro_amortizacion(
            float(c["importe_financiado"]), float(c["cuota"]), n_cuotas,
            c["fecha_inicio"] if pd.notna(c["fecha_inicio"]) else cierre,
            c["periodicidad"], float(c["opcion_compra"]), tasa_periodo=tasa_p)
        cuadro.insert(0, "contrato", cid)
        cuadro.insert(1, "entidad", c["entidad"])
        cuadros.append(cuadro)

        pendientes = cuadro[cuadro["fecha"] > cierre]
        doce_meses = cierre + pd.DateOffset(months=12)
        corriente = float(pendientes[pendientes["fecha"] <= doce_meses]
                          ["amortizacion_capital"].sum())
        no_corriente = float(pendientes[pendientes["fecha"] > doce_meses]
                             ["amortizacion_capital"].sum())
        deuda_viva = round(corriente + no_corriente, 2)
        intereses_ejercicio = float(
            cuadro[(cuadro["fecha"] <= cierre)
                   & (cuadro["fecha"] > cierre - pd.DateOffset(months=12))]["interes"].sum())
        intereses_diferidos = float(pendientes["interes"].sum())

        # --- contraste con el tipo declarado por la entidad ---
        if c["tipo_declarado"] and tasa_anual is not None:
            dif_tipo = abs(tasa_anual - float(c["tipo_declarado"]))
            if dif_tipo > tol_tipo:
                res.add(Excepcion(
                    "ARR-020", DOCUMENTAR, "F",
                    f"Contrato {cid}: el tipo implicito recalculado ({tasa_anual:.2%}) "
                    f"difiere del declarado por la entidad ({c['tipo_declarado']:.2%}) en "
                    f"{dif_tipo * 100:.2f} p.p.",
                    origen=origen,
                    causa_sugerida="Gastos iniciales no incluidos en el calculo de la "
                                   "entidad, o base de calculo 360/365 distinta.",
                    accion="Verificar si la diferencia procede de comisiones de apertura; "
                           "si es asi, incorporarlas al coste amortizado.",
                ))

        # --- contraste con la contabilidad ---
        estado = "OK"
        if c["saldo_contable"]:
            dif = round(deuda_viva - float(c["saldo_contable"]), 2)
            if abs(dif) > tol_importe:
                estado = "DIFERENCIA"
                res.add(Excepcion(
                    "ARR-030", RESOLVER, "F",
                    f"Contrato {cid}: deuda viva recalculada {deuda_viva:,.2f} EUR frente a "
                    f"saldo contable {c['saldo_contable']:,.2f} EUR.",
                    importe=dif, origen=origen,
                    causa_sugerida="Cuotas contabilizadas por el importe total sin separar "
                                   "carga financiera, o cuota impagada no registrada.",
                    accion="Conciliar contrato a contrato y proponer ajuste.",
                ))

        resumen.append({
            "id": cid,
            "entidad": c["entidad"],
            "activo": c["activo"],
            "fecha_inicio": c["fecha_inicio"],
            "importe_financiado": round(float(c["importe_financiado"]), 2),
            "cuota": round(float(c["cuota"]), 2),
            "periodicidad": c["periodicidad"],
            "n_cuotas": n_cuotas,
            "opcion_compra": round(float(c["opcion_compra"]), 2),
            "tipo_implicito_anual": round(tasa_anual, 6) if tasa_anual else None,
            "tipo_declarado": round(float(c["tipo_declarado"]), 6) or None,
            "clasificacion": clasif.tipo,
            "motivacion": clasif.motivacion,
            "deuda_viva_cierre": deuda_viva,
            "corriente_524": round(corriente, 2),
            "no_corriente_174": round(no_corriente, 2),
            "intereses_ejercicio": round(intereses_ejercicio, 2),
            "intereses_diferidos": round(intereses_diferidos, 2),
            "saldo_contable": round(float(c["saldo_contable"]), 2) or None,
            "diferencia": (round(deuda_viva - float(c["saldo_contable"]), 2)
                           if c["saldo_contable"] else None),
            "confianza_extraccion": round(float(c["confianza"]), 2),
            "estado": estado,
        })

    df_resumen = pd.DataFrame(resumen)
    df_cuadros = pd.concat(cuadros, ignore_index=True) if cuadros else pd.DataFrame()

    calculados = df_resumen[df_resumen.get("estado", pd.Series(dtype=str)).notna()] \
        if not df_resumen.empty else df_resumen
    financieros = (df_resumen[df_resumen["clasificacion"] == "FINANCIERO"]
                   if "clasificacion" in df_resumen.columns else pd.DataFrame())
    total_deuda = float(financieros["deuda_viva_cierre"].sum()) if not financieros.empty else 0.0

    res.datos = {
        "contratos": len(datos),
        "procesados": int(len(calculados)),
        "financieros": int(len(financieros)),
        "operativos": int((df_resumen["clasificacion"] == "OPERATIVO").sum())
        if "clasificacion" in df_resumen.columns else 0,
        "dudosos": int((df_resumen["clasificacion"] == "DUDOSO").sum())
        if "clasificacion" in df_resumen.columns else 0,
        "deuda_viva_total": round(total_deuda, 2),
        "corriente": round(float(financieros["corriente_524"].sum()), 2)
        if not financieros.empty else 0.0,
        "no_corriente": round(float(financieros["no_corriente_174"].sum()), 2)
        if not financieros.empty else 0.0,
        "intereses_diferidos": round(float(financieros["intereses_diferidos"].sum()), 2)
        if not financieros.empty else 0.0,
    }
    res.conclusion = (
        f"Procesados {res.datos['procesados']} de {res.datos['contratos']} contratos. "
        f"{res.datos['financieros']} financieros, {res.datos['operativos']} operativos, "
        f"{res.datos['dudosos']} pendientes de clasificacion. Deuda viva total a cierre: "
        f"{total_deuda:,.2f} EUR ({res.datos['corriente']:,.2f} corriente / "
        f"{res.datos['no_corriente']:,.2f} no corriente). "
        + (f"{len(res.excepciones)} excepciones a resolver."
           if res.excepciones else "Sin excepciones.")
    )
    return res, df_resumen, df_cuadros


def cuadro_por_ejercicio(df_cuadros: pd.DataFrame) -> pd.DataFrame:
    """Agregado por ejercicio: cuota, carga financiera y amortizacion de capital.

    Es la tabla que exige el desglose de memoria y la que el auditor necesita
    para verificar la periodificacion.
    """
    if df_cuadros.empty:
        return pd.DataFrame()
    g = df_cuadros.groupby("ejercicio").agg(
        cuotas=("cuota", "sum"),
        carga_financiera=("interes", "sum"),
        amortizacion_capital=("amortizacion_capital", "sum"),
        n_cuotas=("periodo", "count"),
    ).round(2).reset_index()
    return g


def conciliacion_contable(df_resumen: pd.DataFrame, saldo_174: float,
                          saldo_524: float, tol: float = TOL_IMPORTE) -> Resultado:
    """Cuadre global del area contra las cuentas 174 y 524."""
    res = Resultado("Arrendamientos - conciliacion con la contabilidad")
    fin = df_resumen[df_resumen["clasificacion"] == "FINANCIERO"] \
        if "clasificacion" in df_resumen.columns else pd.DataFrame()
    calc_nc = round(float(fin["no_corriente_174"].sum()), 2) if not fin.empty else 0.0
    calc_c = round(float(fin["corriente_524"].sum()), 2) if not fin.empty else 0.0

    for etiqueta, calculado, contable, cuenta in (
            ("no corriente", calc_nc, saldo_174, "174"),
            ("corriente", calc_c, saldo_524, "524")):
        dif = round(calculado - contable, 2)
        if abs(dif) > tol:
            res.add(Excepcion(
                "ARR-040", RESOLVER, "F",
                f"Deuda por arrendamiento financiero {etiqueta}: recalculada "
                f"{calculado:,.2f} EUR frente a saldo contable de la cuenta {cuenta} "
                f"{contable:,.2f} EUR.",
                importe=dif, cuenta=cuenta, origen="cuadro de leasings vs sumas y saldos",
                causa_sugerida="Reclasificacion corriente/no corriente no actualizada al "
                               "cierre, o contratos cancelados no dados de baja.",
                accion="Proponer reclasificacion y verificar el desglose de memoria.",
            ))
    res.datos = {"calculado_no_corriente": calc_nc, "contable_174": round(saldo_174, 2),
                 "calculado_corriente": calc_c, "contable_524": round(saldo_524, 2)}
    res.conclusion = ("La deuda por arrendamiento financiero recalculada cuadra con la "
                      "contabilidad." if res.ok and not res.excepciones else
                      "Diferencias entre el recalculo y la contabilidad; ver excepciones.")
    return res
