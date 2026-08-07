"""Procedimientos analiticos (NIA-ES 520).

Regla de oro implementada: el umbral de investigacion se define A PRIORI, antes
de mirar las cifras. Si se fija despues, el procedimiento no es un analitico
sustantivo, es una racionalizacion de lo que ha salido, y no vale como evidencia.
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from .excepciones import DOCUMENTAR, INFORMATIVA, RESOLVER, Excepcion, Resultado


def umbral_investigacion(materialidad_ejecucion: float, factor: float = 0.5,
                         variacion_relativa: float = 0.10) -> dict[str, float]:
    """Umbral doble: absoluto y relativo. Se investiga lo que supera AMBOS.

    Solo absoluto: en partidas pequenas dispara por cambios porcentuales enormes
    pero irrelevantes. Solo relativo: deja pasar variaciones grandes en partidas
    estables. La conjuncion de los dos es lo que funciona en la practica.
    """
    return {
        "absoluto": round(materialidad_ejecucion * factor, 2),
        "relativo": variacion_relativa,
        "fundamento": (
            f"Se investigaran las variaciones que superen simultaneamente "
            f"{materialidad_ejecucion * factor:,.2f} EUR ({factor:.0%} de la materialidad "
            f"de ejecucion) y el {variacion_relativa:.0%} en terminos relativos. El umbral "
            f"se fija con caracter previo al analisis de las cifras, conforme a la NIA-ES "
            f"520.5.c)."
        ),
    }


def variaciones(actual: dict[str, float], anterior: dict[str, float],
                umbral: dict[str, float], etiqueta: str = "epigrafe",
                area: str = "1.6") -> tuple[Resultado, pd.DataFrame]:
    """Comparativa interanual con umbral definido a priori."""
    res = Resultado(f"Procedimientos analiticos - variaciones interanuales ({etiqueta})")
    filas: list[dict[str, Any]] = []
    for k in sorted(set(actual) | set(anterior)):
        va, vb = round(actual.get(k, 0.0), 2), round(anterior.get(k, 0.0), 2)
        d = round(va - vb, 2)
        pct = (d / abs(vb)) if vb else (1.0 if d else 0.0)
        investigar = abs(d) > umbral["absoluto"] and abs(pct) > umbral["relativo"]
        filas.append({etiqueta: k, "ejercicio_actual": va, "ejercicio_anterior": vb,
                      "variacion": d, "variacion_pct": round(pct, 4),
                      "investigar": "SI" if investigar else ""})
        if investigar:
            res.add(Excepcion(
                "ANA-001", RESOLVER, area,
                f"'{k}': {vb:,.2f} -> {va:,.2f} EUR ({d:+,.2f}, {pct:+.1%}). Supera el "
                f"umbral de investigacion.",
                importe=d, origen="comparativa interanual",
                causa_sugerida="Pendiente de explicacion por la direccion.",
                accion="Obtener explicacion de la direccion, corroborarla con evidencia "
                       "independiente y documentar la conclusion. Una explicacion no "
                       "corroborada no es evidencia suficiente.",
                referencia_normativa="NIA-ES 520.7",
            ))
    detalle = pd.DataFrame(filas).sort_values("variacion", key=abs, ascending=False)
    res.datos = {"conceptos": len(filas),
                 "a_investigar": int(sum(1 for f in filas if f["investigar"])),
                 "umbral_absoluto": umbral["absoluto"],
                 "umbral_relativo": umbral["relativo"]}
    res.conclusion = (
        f"Analizados {len(filas)} conceptos con umbral de {umbral['absoluto']:,.2f} EUR y "
        f"{umbral['relativo']:.0%}. "
        + ("Ninguna variacion supera el umbral; no se han identificado relaciones "
           "incoherentes con las expectativas." if not res.excepciones else
           f"{res.datos['a_investigar']} variaciones requieren investigacion."))
    return res, detalle


RATIOS = {
    "margen_bruto": ("Margen bruto", lambda c: _div(c.get("margen_bruto",
                     c.get("cifra_negocios", 0) - c.get("aprovisionamientos", 0)),
                     c.get("cifra_negocios", 0))),
    "rotacion_existencias": ("Rotacion de existencias (dias)",
                             lambda c: _div(c.get("existencias", 0) * 365,
                                            abs(c.get("aprovisionamientos", 0)))),
    "periodo_medio_cobro": ("Periodo medio de cobro (dias)",
                            lambda c: _div(c.get("clientes", 0) * 365,
                                           c.get("cifra_negocios", 0))),
    "periodo_medio_pago": ("Periodo medio de pago (dias)",
                           lambda c: _div(c.get("proveedores", 0) * 365,
                                          abs(c.get("aprovisionamientos", 0)))),
    "endeudamiento": ("Endeudamiento (pasivo / patrimonio neto)",
                      lambda c: _div(c.get("pasivo", 0), c.get("patrimonio_neto", 0))),
    "liquidez": ("Liquidez (activo corriente / pasivo corriente)",
                 lambda c: _div(c.get("activo_corriente", 0),
                                c.get("pasivo_corriente", 0))),
    "cobertura_intereses": ("Cobertura de intereses (RAII / gastos financieros)",
                            lambda c: _div(c.get("resultado_explotacion", 0),
                                           abs(c.get("gastos_financieros", 0)))),
    "rentabilidad_ventas": ("Rentabilidad sobre ventas",
                            lambda c: _div(c.get("resultado_antes_impuestos", 0),
                                           c.get("cifra_negocios", 0))),
}


def _div(a: float, b: float) -> float | None:
    return round(a / b, 4) if b else None


def ratios(actual: dict[str, float], anterior: dict[str, float] | None = None,
           variacion_significativa: float = 0.20,
           area: str = "1.6") -> tuple[Resultado, pd.DataFrame]:
    """Bateria de ratios con comparativa interanual."""
    res = Resultado("Procedimientos analiticos - ratios")
    filas: list[dict[str, Any]] = []
    for clave, (etiqueta, fn) in RATIOS.items():
        va = fn(actual)
        vb = fn(anterior) if anterior else None
        var = None
        if va is not None and vb not in (None, 0):
            var = round((va - vb) / abs(vb), 4)
            if abs(var) > variacion_significativa:
                res.add(Excepcion(
                    "ANA-010", DOCUMENTAR, area,
                    f"{etiqueta}: {vb:,.4f} -> {va:,.4f} ({var:+.1%}).",
                    origen="ratios", causa_sugerida="Cambio en la estructura de la "
                                                    "actividad o en las politicas contables.",
                    accion="Contrastar con el entendimiento del negocio y con las "
                           "explicaciones de la direccion.",
                ))
        filas.append({"ratio": etiqueta, "actual": va, "anterior": vb, "variacion": var})
    res.datos = {"ratios_calculados": len([f for f in filas if f["actual"] is not None])}
    res.conclusion = ("Los ratios no muestran variaciones significativas respecto del "
                      "ejercicio anterior." if not res.excepciones else
                      f"{len(res.excepciones)} ratios con variacion superior al "
                      f"{variacion_significativa:.0%}.")
    return res, pd.DataFrame(filas)


def evolucion_mensual(diario: pd.DataFrame, prefijo_cuenta: str = "70",
                      umbral_desviacion: float = 0.35,
                      area: str = "C") -> tuple[Resultado, pd.DataFrame]:
    """Analisis mensual de ingresos o gastos.

    Detecta concentracion anomala en un mes -tipicamente diciembre-, meses sin
    actividad y desviaciones sobre la media. Es el analitico que mejor responde
    a la presuncion de fraude en el reconocimiento de ingresos.
    """
    res = Resultado(f"Evolucion mensual de las cuentas {prefijo_cuenta}")
    d = diario[diario["cuenta"].str.startswith(prefijo_cuenta)].copy()
    if d.empty or "fecha" not in d.columns or d["fecha"].isna().all():
        res.conclusion = f"No hay movimientos de cuentas {prefijo_cuenta} con fecha."
        return res, pd.DataFrame()
    d["mes"] = pd.to_datetime(d["fecha"]).dt.month
    d["importe"] = d["haber"] - d["debe"]
    mensual = d.groupby("mes")["importe"].sum().round(2)
    mensual = mensual.reindex(range(1, 13), fill_value=0.0)
    media = float(mensual[mensual != 0].mean()) if (mensual != 0).any() else 0.0

    filas: list[dict[str, Any]] = []
    for mes, imp in mensual.items():
        desv = round((imp - media) / abs(media), 4) if media else None
        filas.append({"mes": int(mes), "importe": float(imp), "media": round(media, 2),
                      "desviacion": desv})
        if media and abs(imp - media) / abs(media) > umbral_desviacion:
            sev = RESOLVER if mes == 12 else DOCUMENTAR
            res.add(Excepcion(
                "ANA-020", sev, area,
                f"Mes {mes:02d}: {imp:,.2f} EUR frente a una media mensual de "
                f"{media:,.2f} EUR ({desv:+.1%}).",
                importe=round(imp - media, 2), origen="diario",
                causa_sugerida=("Concentracion de ingresos en el ultimo mes del ejercicio; "
                                "posible corte de operaciones incorrecto o reconocimiento "
                                "anticipado." if mes == 12 else
                                "Estacionalidad de la actividad o facturacion irregular."),
                accion=("Verificar el corte de operaciones sobre las ultimas facturas del "
                        "ejercicio y las primeras del siguiente." if mes == 12 else
                        "Contrastar con la estacionalidad conocida del negocio."),
                referencia_normativa="NIA-ES 240.25" if mes == 12 else "",
            ))
        if imp == 0 and media:
            res.add(Excepcion(
                "ANA-021", DOCUMENTAR, area,
                f"Mes {mes:02d}: sin movimientos en cuentas {prefijo_cuenta}.",
                origen="diario", causa_sugerida="Periodo de inactividad o facturacion "
                                                "agrupada en otro mes.",
                accion="Confirmar la razonabilidad con el entendimiento del negocio.",
            ))
    res.datos = {"meses_con_desviacion": len(res.excepciones),
                 "media_mensual": round(media, 2),
                 "total": round(float(mensual.sum()), 2)}
    res.conclusion = (
        f"Total del ejercicio {mensual.sum():,.2f} EUR, media mensual {media:,.2f} EUR. "
        + ("Distribucion mensual regular." if not res.excepciones else
           f"{len(res.excepciones)} meses con desviacion significativa."))
    return res, pd.DataFrame(filas)


def expectativa(concepto: str, valor_registrado: float, valor_esperado: float,
                base_calculo: str, materialidad_ejecucion: float,
                precision: float = 0.5, area: str = "1.6") -> Resultado:
    """Analitico sustantivo con expectativa construida sobre datos independientes.

    Es lo que convierte un analitico en evidencia sustantiva: la expectativa debe
    construirse con datos ajenos al registro que se audita (nº de empleados x
    salario medio del convenio, m2 x precio, kWh x tarifa, unidades x precio).
    """
    res = Resultado(f"Analitico sustantivo - {concepto}")
    dif = round(valor_registrado - valor_esperado, 2)
    umbral = materialidad_ejecucion * precision
    supera = abs(dif) > umbral
    res.datos = {"registrado": round(valor_registrado, 2),
                 "esperado": round(valor_esperado, 2), "diferencia": dif,
                 "umbral": round(umbral, 2), "supera": supera}
    if supera:
        res.add(Excepcion(
            "ANA-030", RESOLVER, area,
            f"{concepto}: importe registrado {valor_registrado:,.2f} EUR frente a la "
            f"expectativa de {valor_esperado:,.2f} EUR (diferencia {dif:+,.2f} EUR, "
            f"umbral {umbral:,.2f} EUR).",
            importe=dif, origen=base_calculo,
            causa_sugerida="Pendiente de investigar.",
            accion="Investigar la diferencia mediante procedimientos adicionales y "
                   "corroborar las explicaciones de la direccion con evidencia.",
            referencia_normativa="NIA-ES 520.5-7",
        ))
    res.conclusion = (
        f"Expectativa construida sobre: {base_calculo}. Importe esperado "
        f"{valor_esperado:,.2f} EUR frente a {valor_registrado:,.2f} EUR registrados. "
        + (f"La diferencia de {dif:+,.2f} EUR supera el umbral de precision "
           f"({umbral:,.2f} EUR) y requiere investigacion." if supera else
           f"La diferencia de {dif:+,.2f} EUR se situa dentro del umbral de precision "
           f"({umbral:,.2f} EUR). El procedimiento aporta evidencia sustantiva suficiente "
           f"sobre la razonabilidad del importe registrado."))
    return res
