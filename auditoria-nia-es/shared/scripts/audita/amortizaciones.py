"""Recalculo integral de amortizaciones del inmovilizado.

Recalcula elemento a elemento, con prorrateo por dias en altas y bajas, y
contrasta contra la dotacion contabilizada. Reporta solo lo que difiere.
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from .excepciones import DOCUMENTAR, INFORMATIVA, RESOLVER, Excepcion, Resultado
from .ingesta import columna, num

TOL = 1.00

# Coeficientes maximos de la tabla del art. 12.1 LIS, como referencia de
# razonabilidad. Superarlos no es un error contable, pero suele indicar que la
# vida util contable se ha fijado por criterio fiscal y no economico.
COEF_MAX_LIS = {
    "edificios": 0.02, "construcciones": 0.02, "instalaciones": 0.10,
    "maquinaria": 0.12, "utillaje": 0.25, "mobiliario": 0.10,
    "equipos informaticos": 0.25, "elementos de transporte": 0.16,
    "otro inmovilizado": 0.10, "aplicaciones informaticas": 0.33,
}


def normaliza_inventario(df: pd.DataFrame) -> pd.DataFrame:
    m = {
        "id": columna(df, "id", "elemento", "referencia", "codigo", "num"),
        "descripcion": columna(df, "descripcion", "concepto", "denominacion", "bien"),
        "familia": columna(df, "familia", "tipo", "naturaleza", "grupo", "epigrafe"),
        "cuenta": columna(df, "cuenta", "cuenta contable"),
        "fecha_alta": columna(df, "fecha alta", "alta", "fecha adquisicion", "adquisicion"),
        "fecha_baja": columna(df, "fecha baja", "baja", "fecha enajenacion"),
        "coste": columna(df, "coste", "valor adquisicion", "importe", "precio adquisicion"),
        "valor_residual": columna(df, "valor residual", "residual"),
        "coeficiente": columna(df, "coeficiente", "porcentaje", "tasa", "% amortizacion"),
        "vida_util": columna(df, "vida util", "anos", "vida"),
        "aa_inicial": columna(df, "amortizacion acumulada inicial", "aa inicial",
                              "amortizacion acumulada anterior", "acumulada inicio"),
        "dotacion_contable": columna(df, "dotacion", "amortizacion ejercicio",
                                     "dotacion contable", "amortizacion del ejercicio"),
        "aa_final": columna(df, "amortizacion acumulada final", "aa final",
                            "acumulada final", "amortizacion acumulada"),
    }
    out = pd.DataFrame(index=df.index)
    out["id"] = (df[m["id"]].astype(str).str.strip() if m["id"]
                 else [f"ELE-{i + 1:04d}" for i in range(len(df))])
    for campo in ("descripcion", "familia", "cuenta"):
        out[campo] = df[m[campo]].astype(str).str.strip() if m[campo] else ""
    for campo in ("fecha_alta", "fecha_baja"):
        out[campo] = (pd.to_datetime(df[m[campo]], errors="coerce", dayfirst=True)
                      if m[campo] else pd.NaT)
    for campo in ("coste", "valor_residual", "aa_inicial", "dotacion_contable", "aa_final"):
        out[campo] = num(df, m[campo])
    out["coeficiente"] = num(df, m["coeficiente"])
    out["coeficiente"] = out["coeficiente"].where(out["coeficiente"] < 1,
                                                  out["coeficiente"] / 100.0)
    out["vida_util"] = num(df, m["vida_util"])
    out["_fila_origen"] = (df["_fila_origen"] if "_fila_origen" in df.columns
                           else range(2, len(df) + 2))
    return out


def recalcula(df_inventario: pd.DataFrame, inicio_ejercicio: str | pd.Timestamp,
              fin_ejercicio: str | pd.Timestamp, metodo: str = "lineal",
              fichero_origen: str = "inventario"
              ) -> tuple[Resultado, pd.DataFrame]:
    """Recalculo integral. Prorrateo por dias naturales.

    Base = coste - valor residual. Se limita la amortizacion acumulada a la base
    amortizable: un elemento no puede amortizarse por encima de su coste, y ese
    exceso es una de las incidencias mas frecuentes en inventarios antiguos.
    """
    ini, fin = pd.Timestamp(inicio_ejercicio), pd.Timestamp(fin_ejercicio)
    dias_ejercicio = (fin - ini).days + 1
    datos = normaliza_inventario(df_inventario)
    res = Resultado("Recalculo de amortizaciones del inmovilizado")
    filas: list[dict[str, Any]] = []

    for _, e in datos.iterrows():
        origen = f"{fichero_origen} fila {int(e['_fila_origen'])}"
        coste = float(e["coste"])
        if coste <= 0:
            res.add(Excepcion(
                "AMO-001", RESOLVER, "A",
                f"Elemento {e['id']} ({e['descripcion']}): sin coste informado.",
                origen=origen, accion="Completar el inventario."))
            continue

        coef = float(e["coeficiente"])
        if not coef and e["vida_util"]:
            coef = 1.0 / float(e["vida_util"])
        if not coef:
            res.add(Excepcion(
                "AMO-002", RESOLVER, "A",
                f"Elemento {e['id']} ({e['descripcion']}): sin coeficiente ni vida util. "
                "No se ha recalculado.",
                importe=coste, origen=origen,
                accion="Obtener el criterio de amortizacion aplicado."))
            continue

        base = coste - float(e["valor_residual"])
        alta, baja = e["fecha_alta"], e["fecha_baja"]

        # dias amortizables dentro del ejercicio
        desde = max(alta, ini) if pd.notna(alta) else ini
        hasta = min(baja, fin) if pd.notna(baja) else fin
        dias = max((hasta - desde).days + 1, 0) if hasta >= desde else 0
        if pd.notna(alta) and alta > fin:
            dias = 0  # alta posterior al cierre

        teorica = round(base * coef * dias / dias_ejercicio, 2)

        # tope: no amortizar por encima de la base
        aa_ini = float(e["aa_inicial"])
        margen = round(base - aa_ini, 2)
        limitada = False
        if teorica > margen:
            teorica = max(margen, 0.0)
            limitada = True

        contable = float(e["dotacion_contable"])
        dif = round(teorica - contable, 2)

        if abs(dif) > TOL:
            res.add(Excepcion(
                "AMO-010", RESOLVER, "A",
                f"Elemento {e['id']} ({e['descripcion']}): dotacion recalculada "
                f"{teorica:,.2f} EUR frente a contabilizada {contable:,.2f} EUR.",
                importe=dif, cuenta=str(e["cuenta"]), origen=origen,
                causa_sugerida=("Alta o baja no prorrateada por dias, coeficiente distinto "
                                "al del inventario, o elemento ya totalmente amortizado."),
                accion="Verificar el criterio y proponer ajuste si la diferencia es real.",
            ))
        if limitada and margen <= 0:
            res.add(Excepcion(
                "AMO-011", DOCUMENTAR, "A",
                f"Elemento {e['id']} ({e['descripcion']}): totalmente amortizado "
                f"(coste {coste:,.2f} EUR) y sigue en el inventario.",
                importe=coste, cuenta=str(e["cuenta"]), origen=origen,
                causa_sugerida="Elemento en uso totalmente amortizado, o baja no registrada.",
                accion="Verificar que sigue en uso y desglosarlo en memoria; si no esta en "
                       "uso, dar de baja.",
            ))
        if aa_ini > base + TOL:
            res.add(Excepcion(
                "AMO-012", RESOLVER, "A",
                f"Elemento {e['id']}: amortizacion acumulada inicial {aa_ini:,.2f} EUR "
                f"superior a la base amortizable {base:,.2f} EUR.",
                importe=round(aa_ini - base, 2), cuenta=str(e["cuenta"]), origen=origen,
                causa_sugerida="Sobreamortizacion arrastrada de ejercicios anteriores.",
                accion="Regularizar y evaluar si es correccion de error (NRV 22ª).",
            ))
        # razonabilidad frente a la tabla del art. 12.1 LIS
        familia = str(e["familia"]).lower()
        for clave, maximo in COEF_MAX_LIS.items():
            if clave in familia and coef > maximo * 1.05:
                res.add(Excepcion(
                    "AMO-020", INFORMATIVA, "A",
                    f"Elemento {e['id']} ({e['familia']}): coeficiente {coef:.2%} superior "
                    f"al maximo de la tabla del art. 12.1 LIS ({maximo:.2%}).",
                    cuenta=str(e["cuenta"]), origen=origen,
                    causa_sugerida="Vida util contable inferior a la fiscal.",
                    accion="Verificar que responde a la vida util economica real y que la "
                           "diferencia esta recogida como diferencia temporaria.",
                ))
                break

        filas.append({
            "id": e["id"], "descripcion": e["descripcion"], "familia": e["familia"],
            "cuenta": e["cuenta"], "fecha_alta": alta, "fecha_baja": baja,
            "coste": round(coste, 2), "valor_residual": round(float(e["valor_residual"]), 2),
            "base_amortizable": round(base, 2), "coeficiente": round(coef, 6),
            "dias_amortizados": dias,
            "aa_inicial": round(aa_ini, 2),
            "dotacion_recalculada": teorica, "dotacion_contable": round(contable, 2),
            "diferencia": dif,
            "aa_final_recalculada": round(aa_ini + teorica, 2),
            "aa_final_contable": round(float(e["aa_final"]), 2) or None,
            "vnc_recalculado": round(coste - aa_ini - teorica, 2),
        })

    detalle = pd.DataFrame(filas)
    total_rec = float(detalle["dotacion_recalculada"].sum()) if not detalle.empty else 0.0
    total_cont = float(detalle["dotacion_contable"].sum()) if not detalle.empty else 0.0
    res.datos = {
        "elementos": len(datos), "recalculados": len(detalle),
        "dotacion_recalculada": round(total_rec, 2),
        "dotacion_contable": round(total_cont, 2),
        "diferencia_total": round(total_rec - total_cont, 2),
        "elementos_con_diferencia": int((detalle["diferencia"].abs() > TOL).sum())
        if not detalle.empty else 0,
    }
    res.conclusion = (
        f"Recalculados {len(detalle)} de {len(datos)} elementos. Dotacion recalculada "
        f"{total_rec:,.2f} EUR frente a {total_cont:,.2f} EUR contabilizados "
        f"(diferencia {total_rec - total_cont:+,.2f} EUR). "
        + (f"{res.datos['elementos_con_diferencia']} elementos con diferencia individual."
           if res.datos["elementos_con_diferencia"] else "Sin diferencias individuales."))
    return res, detalle


def indicios_deterioro(detalle: pd.DataFrame, area: str = "A") -> Resultado:
    """Indicios de deterioro sobre el inventario recalculado (NRV 2ª.2.2)."""
    res = Resultado("Indicios de deterioro del inmovilizado")
    if detalle.empty:
        res.conclusion = "Sin inventario recalculado."
        return res
    # elementos sin amortizar en el ejercicio pero con valor neto contable relevante
    parados = detalle[(detalle["dias_amortizados"] == 0)
                      & (detalle["vnc_recalculado"] > 0)
                      & (detalle["fecha_baja"].isna())]
    for _, e in parados.iterrows():
        res.add(Excepcion(
            "DET-001", RESOLVER, area,
            f"Elemento {e['id']} ({e['descripcion']}): valor neto contable "
            f"{e['vnc_recalculado']:,.2f} EUR y sin amortizacion en el ejercicio.",
            importe=float(e["vnc_recalculado"]), cuenta=str(e["cuenta"]),
            origen="inventario",
            causa_sugerida="Elemento fuera de uso, en curso, o alta posterior al cierre.",
            accion="Verificar su situacion y evaluar si procede reconocer un deterioro.",
        ))
    res.datos = {"elementos_sin_amortizar": len(parados)}
    res.conclusion = ("No se han identificado indicios de deterioro a partir del inventario."
                      if parados.empty else
                      f"{len(parados)} elementos requieren evaluacion de deterioro.")
    return res
