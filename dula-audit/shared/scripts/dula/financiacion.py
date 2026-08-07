"""Tesoreria y financiacion.

Escala sin friccion desde "3 creditos y un prestamo" hasta carteras de polizas,
confirming, factoring y avales. El problema real no es el calculo, es que los
cuadros de las entidades financieras no tienen dos formatos iguales: por eso la
normalizacion admite cualquier disposicion de columnas.
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from .excepciones import BLOQUEANTE, DOCUMENTAR, INFORMATIVA, RESOLVER, Excepcion, Resultado
from .ingesta import columna, num
from .leasing import tir, van

TOL = 1.00


# ---------------------------------------------------------------------------
# Prestamos y creditos
# ---------------------------------------------------------------------------
def tipo_efectivo(nominal: float, cuota: float, n_cuotas: int,
                  gastos_iniciales: float = 0.0, periodos_ano: int = 12
                  ) -> tuple[float | None, float | None]:
    """Tipo de interes efectivo incorporando los gastos iniciales.

    Es el tipo que exige la NRV 9ª para valorar a coste amortizado: el que
    iguala el valor actual de los flujos futuros con el importe neto recibido
    (nominal menos comisiones de apertura y gastos de formalizacion).
    """
    neto = nominal - gastos_iniciales
    if neto <= 0 or cuota <= 0 or n_cuotas <= 0:
        return None, None
    flujos = [(0.0, -neto)] + [(float(k), cuota) for k in range(1, n_cuotas + 1)]
    t = tir(flujos)
    if t is None:
        return None, None
    return t, (1.0 + t) ** periodos_ano - 1.0


def cuadro_prestamo(nominal: float, cuota: float, n_cuotas: int,
                    fecha_inicio: pd.Timestamp, periodicidad: str = "mensual",
                    gastos_iniciales: float = 0.0,
                    tasa_periodo: float | None = None) -> pd.DataFrame:
    """Cuadro a coste amortizado. El coste amortizado inicial es el importe neto
    recibido; los gastos iniciales se imputan a resultados a lo largo de la vida
    del prestamo a traves del tipo efectivo, no como gasto del ejercicio."""
    from .leasing import PERIODOS_ANO
    pa = PERIODOS_ANO.get(str(periodicidad).lower(), 12)
    if tasa_periodo is None:
        tasa_periodo, _ = tipo_efectivo(nominal, cuota, n_cuotas, gastos_iniciales, pa)
    if tasa_periodo is None:
        tasa_periodo = 0.0
    meses = 12 // pa
    pendiente = nominal - gastos_iniciales
    filas: list[dict[str, Any]] = []
    for k in range(1, n_cuotas + 1):
        fecha = fecha_inicio + pd.DateOffset(months=meses * k)
        interes = round(pendiente * tasa_periodo, 2)
        amortiza = round(cuota - interes, 2)
        if k == n_cuotas:
            amortiza = round(pendiente, 2)
            interes = round(cuota - amortiza, 2)
        pendiente = round(pendiente - amortiza, 2)
        filas.append({"periodo": k, "fecha": fecha, "ejercicio": fecha.year,
                      "cuota": round(cuota, 2), "interes": interes,
                      "amortizacion_capital": amortiza,
                      "coste_amortizado": max(pendiente, 0.0)})
    return pd.DataFrame(filas)


def normaliza_cartera(df: pd.DataFrame) -> pd.DataFrame:
    """Mapea el listado de instrumentos financieros, venga como venga."""
    m = {
        "id": columna(df, "id", "contrato", "referencia", "n operacion", "codigo", "num"),
        "entidad": columna(df, "entidad", "banco", "acreedor", "financiera"),
        "producto": columna(df, "producto", "tipo", "modalidad", "instrumento"),
        "nominal": columna(df, "nominal", "principal", "importe", "capital", "limite",
                           "concedido"),
        "dispuesto": columna(df, "dispuesto", "saldo dispuesto", "utilizado", "saldo"),
        "cuota": columna(df, "cuota", "cuota periodica", "mensualidad"),
        "n_cuotas": columna(df, "n cuotas", "cuotas", "plazo", "numero cuotas"),
        "fecha_inicio": columna(df, "fecha inicio", "inicio", "formalizacion", "fecha"),
        "fecha_vencimiento": columna(df, "vencimiento", "fecha vencimiento", "fecha fin"),
        "periodicidad": columna(df, "periodicidad", "frecuencia"),
        "tipo_interes": columna(df, "tipo interes", "tin", "interes", "tipo"),
        "gastos_iniciales": columna(df, "gastos", "comision apertura", "gastos iniciales"),
        "garantias": columna(df, "garantia", "garantias", "aval", "pignoracion"),
        "saldo_contable": columna(df, "saldo contable", "contabilidad"),
        "cuenta": columna(df, "cuenta", "cuenta contable"),
    }
    out = pd.DataFrame(index=df.index)
    out["id"] = (df[m["id"]].astype(str).str.strip() if m["id"]
                 else [f"FIN-{i + 1:03d}" for i in range(len(df))])
    for campo in ("entidad", "producto", "garantias", "cuenta"):
        out[campo] = df[m[campo]].astype(str).str.strip() if m[campo] else ""
    for campo in ("nominal", "dispuesto", "cuota", "gastos_iniciales", "saldo_contable"):
        out[campo] = num(df, m[campo])
    out["n_cuotas"] = num(df, m["n_cuotas"]).round().astype(int)
    for campo in ("fecha_inicio", "fecha_vencimiento"):
        out[campo] = (pd.to_datetime(df[m[campo]], errors="coerce", dayfirst=True)
                      if m[campo] else pd.NaT)
    out["periodicidad"] = (df[m["periodicidad"]].astype(str).str.lower().str.strip()
                           if m["periodicidad"] else "mensual")
    out["tipo_interes"] = num(df, m["tipo_interes"])
    out["tipo_interes"] = out["tipo_interes"].where(out["tipo_interes"] < 1,
                                                    out["tipo_interes"] / 100.0)
    out["_fila_origen"] = (df["_fila_origen"] if "_fila_origen" in df.columns
                           else range(2, len(df) + 2))
    return out


def procesa_cartera(df: pd.DataFrame, fecha_cierre: str | pd.Timestamp,
                    fichero_origen: str = "financiacion"
                    ) -> tuple[Resultado, pd.DataFrame]:
    """Recalcula deuda viva, reparto corriente/no corriente e intereses.

    Distingue productos con cuadro de amortizacion (prestamos, leasings) de
    productos revolving (polizas, confirming, factoring), en los que la deuda
    viva es el dispuesto y el reparto depende del vencimiento del limite.
    """
    cierre = pd.Timestamp(fecha_cierre)
    doce = cierre + pd.DateOffset(months=12)
    datos = normaliza_cartera(df)
    res = Resultado("Financiacion - recalculo de la cartera")
    filas: list[dict[str, Any]] = []

    for _, c in datos.iterrows():
        origen = f"{fichero_origen} fila {int(c['_fila_origen'])}"
        producto = str(c["producto"]).lower()
        revolving = any(p in producto for p in
                        ("poliza", "credito", "confirming", "factoring", "linea"))

        if revolving:
            deuda = float(c["dispuesto"] or c["saldo_contable"])
            venc = c["fecha_vencimiento"]
            if pd.isna(venc):
                corriente, no_corriente = deuda, 0.0
                res.add(Excepcion(
                    "FIN-001", DOCUMENTAR, "E",
                    f"{c['id']} ({c['entidad']}): producto revolving sin fecha de "
                    "vencimiento. Se clasifica integramente como corriente.",
                    importe=deuda, origen=origen,
                    accion="Obtener el vencimiento del limite para clasificar correctamente.",
                ))
            else:
                corriente = deuda if venc <= doce else 0.0
                no_corriente = deuda if venc > doce else 0.0
            intereses = 0.0
            tipo_eff = float(c["tipo_interes"]) or None
            if c["nominal"] and deuda > c["nominal"] + TOL:
                res.add(Excepcion(
                    "FIN-002", RESOLVER, "E",
                    f"{c['id']} ({c['entidad']}): dispuesto {deuda:,.2f} EUR superior al "
                    f"limite concedido {c['nominal']:,.2f} EUR.",
                    importe=round(deuda - float(c["nominal"]), 2), origen=origen,
                    causa_sugerida="Excedido en poliza no regularizado, o limite reducido "
                                   "por la entidad sin actualizar el listado.",
                    accion="Confirmar con la entidad y evaluar el efecto en covenants.",
                ))
        else:
            if c["nominal"] <= 0 or c["cuota"] <= 0 or c["n_cuotas"] <= 0:
                res.add(Excepcion(
                    "FIN-003", RESOLVER, "E",
                    f"{c['id']} ({c['entidad']}): faltan datos para recalcular "
                    f"(nominal {c['nominal']:,.2f}, cuota {c['cuota']:,.2f}, "
                    f"cuotas {c['n_cuotas']}).",
                    origen=origen,
                    accion="Solicitar el cuadro de amortizacion de la entidad.",
                ))
                filas.append({"id": c["id"], "entidad": c["entidad"],
                              "producto": c["producto"], "estado": "SIN CALCULAR"})
                continue
            tasa_p, tipo_eff = tipo_efectivo(
                float(c["nominal"]), float(c["cuota"]), int(c["n_cuotas"]),
                float(c["gastos_iniciales"]))
            inicio = c["fecha_inicio"] if pd.notna(c["fecha_inicio"]) else cierre
            cuadro = cuadro_prestamo(float(c["nominal"]), float(c["cuota"]),
                                     int(c["n_cuotas"]), inicio, c["periodicidad"],
                                     float(c["gastos_iniciales"]), tasa_p)
            pend = cuadro[cuadro["fecha"] > cierre]
            corriente = float(pend[pend["fecha"] <= doce]["amortizacion_capital"].sum())
            no_corriente = float(pend[pend["fecha"] > doce]["amortizacion_capital"].sum())
            deuda = round(corriente + no_corriente, 2)
            intereses = float(cuadro[(cuadro["fecha"] <= cierre)
                                     & (cuadro["fecha"] > cierre - pd.DateOffset(months=12))]
                              ["interes"].sum())

        estado = "OK"
        dif = None
        if c["saldo_contable"]:
            dif = round(deuda - float(c["saldo_contable"]), 2)
            if abs(dif) > TOL:
                estado = "DIFERENCIA"
                res.add(Excepcion(
                    "FIN-010", RESOLVER, "E",
                    f"{c['id']} ({c['entidad']}): deuda viva recalculada {deuda:,.2f} EUR "
                    f"frente a saldo contable {c['saldo_contable']:,.2f} EUR.",
                    importe=dif, cuenta=str(c["cuenta"]), origen=origen,
                    causa_sugerida="Intereses devengados no periodificados, cuota de "
                                   "diciembre no contabilizada, o gastos de formalizacion "
                                   "llevados a resultados en lugar de a coste amortizado.",
                    accion="Conciliar y proponer ajuste.",
                ))

        if str(c["garantias"]).strip() and str(c["garantias"]).lower() not in {"", "nan", "no"}:
            res.add(Excepcion(
                "FIN-020", INFORMATIVA, "E",
                f"{c['id']} ({c['entidad']}): garantia asociada -> {c['garantias']}.",
                origen=origen,
                accion="Verificar su desglose en la memoria y su inclusion en la "
                       "confirmacion bancaria.",
            ))

        filas.append({
            "id": c["id"], "entidad": c["entidad"], "producto": c["producto"],
            "revolving": revolving,
            "nominal_limite": round(float(c["nominal"]), 2),
            "fecha_inicio": c["fecha_inicio"], "fecha_vencimiento": c["fecha_vencimiento"],
            "deuda_viva": round(deuda, 2),
            "corriente": round(corriente, 2), "no_corriente": round(no_corriente, 2),
            "tipo_efectivo_anual": round(tipo_eff, 6) if tipo_eff else None,
            "tipo_declarado": round(float(c["tipo_interes"]), 6) or None,
            "intereses_ejercicio": round(intereses, 2),
            "garantias": c["garantias"], "cuenta": c["cuenta"],
            "saldo_contable": round(float(c["saldo_contable"]), 2) or None,
            "diferencia": dif, "estado": estado,
        })

    resumen = pd.DataFrame(filas)
    total = float(resumen["deuda_viva"].sum()) if "deuda_viva" in resumen.columns else 0.0
    res.datos = {
        "instrumentos": len(datos),
        "deuda_viva_total": round(total, 2),
        "corriente": round(float(resumen["corriente"].sum()), 2)
        if "corriente" in resumen.columns else 0.0,
        "no_corriente": round(float(resumen["no_corriente"].sum()), 2)
        if "no_corriente" in resumen.columns else 0.0,
    }
    res.conclusion = (
        f"{len(datos)} instrumentos recalculados. Deuda viva total {total:,.2f} EUR "
        f"({res.datos['corriente']:,.2f} corriente / {res.datos['no_corriente']:,.2f} no "
        f"corriente). " + (f"{len(res.excepciones)} excepciones." if res.excepciones
                           else "Sin excepciones."))
    return res, resumen


# ---------------------------------------------------------------------------
# Conciliaciones bancarias
# ---------------------------------------------------------------------------
def concilia_banco(extracto: pd.DataFrame, mayor: pd.DataFrame,
                   col_importe_ext: str, col_importe_may: str,
                   col_fecha_ext: str | None = None,
                   col_fecha_may: str | None = None,
                   cuenta: str = "572", tolerancia: float = 0.01
                   ) -> tuple[Resultado, pd.DataFrame]:
    """Conciliacion bancaria por casacion de importes.

    Casa por importe exacto (y fecha proxima si se aporta). Lo que no casa es la
    partida conciliatoria: cheques pendientes de cobro, abonos en camino,
    comisiones no contabilizadas.
    """
    res = Resultado(f"Conciliacion bancaria cuenta {cuenta}")
    ext = extracto.copy().reset_index(drop=True)
    may = mayor.copy().reset_index(drop=True)
    ext["_imp"] = num(ext, col_importe_ext).round(2)
    may["_imp"] = num(may, col_importe_may).round(2)

    usados_may: set[int] = set()
    conciliaciones: list[dict[str, Any]] = []
    for i, r in ext.iterrows():
        candidatos = may[(~may.index.isin(usados_may))
                         & ((may["_imp"] - r["_imp"]).abs() <= tolerancia)]
        if col_fecha_ext and col_fecha_may and not candidatos.empty:
            fe = pd.to_datetime(r[col_fecha_ext], errors="coerce", dayfirst=True)
            if pd.notna(fe):
                fm = pd.to_datetime(candidatos[col_fecha_may], errors="coerce", dayfirst=True)
                cercanos = candidatos[(fm - fe).abs() <= pd.Timedelta(days=7)]
                if not cercanos.empty:
                    candidatos = cercanos
        if candidatos.empty:
            conciliaciones.append({"origen": "extracto", "importe": r["_imp"],
                                   "fila": i + 2, "situacion": "En extracto, sin registro contable"})
        else:
            usados_may.add(int(candidatos.index[0]))

    for j, r in may[~may.index.isin(usados_may)].iterrows():
        conciliaciones.append({"origen": "mayor", "importe": r["_imp"], "fila": j + 2,
                               "situacion": "Contabilizado, sin movimiento en extracto"})

    df_conc = pd.DataFrame(conciliaciones)
    saldo_ext = round(float(ext["_imp"].sum()), 2)
    saldo_may = round(float(may["_imp"].sum()), 2)
    dif = round(saldo_ext - saldo_may, 2)

    for _, c in df_conc.iterrows():
        res.add(Excepcion(
            "TES-001", RESOLVER if abs(c["importe"]) > 0 else DOCUMENTAR, "D",
            f"{c['situacion']}: {c['importe']:,.2f} EUR (fila {c['fila']}).",
            importe=float(c["importe"]), cuenta=cuenta,
            origen=f"{c['origen']} fila {c['fila']}",
            causa_sugerida=("Cheque emitido pendiente de cobro, o comision bancaria no "
                            "contabilizada." if c["origen"] == "mayor"
                            else "Abono en camino o cargo bancario no registrado."),
            accion="Verificar el cobro/pago posterior y contabilizar lo que proceda.",
        ))
    res.datos = {"saldo_extracto": saldo_ext, "saldo_mayor": saldo_may,
                 "diferencia": dif, "partidas_conciliatorias": len(df_conc)}
    res.conclusion = (
        f"Saldo segun extracto {saldo_ext:,.2f} EUR y segun mayor {saldo_may:,.2f} EUR. "
        + ("Conciliacion sin partidas pendientes." if df_conc.empty else
           f"{len(df_conc)} partidas conciliatorias por {dif:,.2f} EUR neto."))
    return res, df_conc


# ---------------------------------------------------------------------------
# Confirmaciones bancarias
# ---------------------------------------------------------------------------
def seguimiento_confirmaciones(df: pd.DataFrame, area: str = "D") -> Resultado:
    """Control de la circularizacion bancaria (NIA-ES 505).

    Vigila lo que en la practica se descontrola: entidades a las que no se envio,
    envios sin respuesta, y -lo mas importante- respuestas que revelan saldos,
    avales o pignoraciones que NO estaban en la contabilidad ni en la memoria.
    """
    res = Resultado("Seguimiento de confirmaciones bancarias")
    c_ent = columna(df, "entidad", "banco")
    c_env = columna(df, "enviada", "fecha envio", "envio")
    c_resp = columna(df, "respuesta", "recibida", "fecha respuesta")
    c_saldo_conf = columna(df, "saldo confirmado", "confirmado", "saldo banco")
    c_saldo_cont = columna(df, "saldo contable", "contabilidad", "saldo libros")
    c_avales = columna(df, "avales", "garantias", "riesgos indirectos")
    c_avales_cont = columna(df, "avales contabilizados", "avales memoria")

    sin_enviar = respondidas = 0
    for _, r in df.iterrows():
        entidad = str(r[c_ent]).strip() if c_ent else "(sin identificar)"
        enviada = bool(str(r[c_env]).strip()) and str(r[c_env]).lower() not in \
            {"nan", "no", "", "none"} if c_env else False
        respondida = bool(str(r[c_resp]).strip()) and str(r[c_resp]).lower() not in \
            {"nan", "no", "", "none"} if c_resp else False

        if not enviada:
            sin_enviar += 1
            res.add(Excepcion(
                "CIR-001", BLOQUEANTE, area,
                f"{entidad}: no consta el envio de la solicitud de confirmacion.",
                origen="control de circularizacion",
                accion="Enviar la solicitud. Sin confirmacion ni procedimiento alternativo "
                       "suficiente, hay limitacion al alcance.",
                referencia_normativa="NIA-ES 505",
            ))
            continue
        if not respondida:
            res.add(Excepcion(
                "CIR-002", RESOLVER, area,
                f"{entidad}: solicitud enviada sin respuesta.",
                origen="control de circularizacion",
                causa_sugerida="Entidad que no responde a circularizaciones o direccion "
                               "de envio incorrecta.",
                accion="Reiterar el envio y, si no hay respuesta, aplicar procedimientos "
                       "alternativos (extractos y movimientos posteriores) y documentar su "
                       "suficiencia.",
                referencia_normativa="NIA-ES 505.12",
            ))
            continue

        respondidas += 1
        if c_saldo_conf and c_saldo_cont:
            sc = float(num(pd.DataFrame([r]), c_saldo_conf).iloc[0])
            sk = float(num(pd.DataFrame([r]), c_saldo_cont).iloc[0])
            d = round(sc - sk, 2)
            if abs(d) > TOL:
                res.add(Excepcion(
                    "CIR-010", RESOLVER, area,
                    f"{entidad}: saldo confirmado {sc:,.2f} EUR frente a saldo contable "
                    f"{sk:,.2f} EUR.",
                    importe=d, origen="respuesta de la entidad",
                    causa_sugerida="Partidas conciliatorias pendientes o saldo contable "
                                   "desactualizado.",
                    accion="Conciliar y proponer ajuste si la diferencia no es conciliatoria.",
                ))
        if c_avales:
            avales = str(r[c_avales]).strip()
            if avales and avales.lower() not in {"nan", "no", "", "none", "0"}:
                declarados = (str(r[c_avales_cont]).strip().lower()
                              if c_avales_cont else "")
                if declarados in {"", "nan", "no", "none", "0"}:
                    res.add(Excepcion(
                        "CIR-020", RESOLVER, area,
                        f"{entidad}: la confirmacion revela avales/garantias "
                        f"({avales}) que no constan desglosados.",
                        origen="respuesta de la entidad",
                        causa_sugerida="Riesgo indirecto no comunicado por la direccion.",
                        accion="Verificar su naturaleza y desglosarlo en memoria como "
                               "compromiso o pasivo contingente.",
                        referencia_normativa="PGC NRV 15ª; memoria nota de otra informacion",
                    ))
    res.datos = {"entidades": len(df), "sin_enviar": sin_enviar,
                 "respondidas": respondidas,
                 "tasa_respuesta": round(respondidas / len(df), 2) if len(df) else 0.0}
    res.conclusion = (
        f"{respondidas} de {len(df)} entidades han respondido "
        f"({res.datos['tasa_respuesta']:.0%}). "
        + ("Circularizacion completa y conciliada." if not res.excepciones
           else f"{len(res.excepciones)} incidencias."))
    return res


def verifica_covenants(df: pd.DataFrame, area: str = "E") -> Resultado:
    """Verificacion de covenants y de su desglose.

    El incumplimiento de un covenant a la fecha de cierre puede convertir deuda
    no corriente en corriente y, en casos graves, activar dudas sobre empresa en
    funcionamiento. Es una de las comprobaciones que mas se olvidan.
    """
    res = Resultado("Verificacion de covenants")
    c_id = columna(df, "id", "contrato", "referencia")
    c_ent = columna(df, "entidad", "banco")
    c_cov = columna(df, "covenant", "ratio", "condicion")
    c_exig = columna(df, "exigido", "limite", "umbral")
    c_real = columna(df, "real", "obtenido", "calculado", "valor")
    c_sentido = columna(df, "sentido", "tipo", "comparacion")

    incumplidos = 0
    for _, r in df.iterrows():
        ident = f"{r[c_id] if c_id else '?'} ({r[c_ent] if c_ent else '?'})"
        exigido = float(num(pd.DataFrame([r]), c_exig).iloc[0]) if c_exig else None
        real = float(num(pd.DataFrame([r]), c_real).iloc[0]) if c_real else None
        if exigido is None or real is None:
            res.add(Excepcion(
                "COV-001", RESOLVER, area,
                f"{ident}: covenant '{r[c_cov] if c_cov else 'sin identificar'}' sin datos "
                "para verificar su cumplimiento.",
                origen="listado de covenants",
                accion="Obtener el certificado de cumplimiento emitido por la entidad.",
            ))
            continue
        sentido = str(r[c_sentido]).strip().lower() if c_sentido else "minimo"
        cumple = real >= exigido if sentido.startswith("min") else real <= exigido
        if not cumple:
            incumplidos += 1
            res.add(Excepcion(
                "COV-010", BLOQUEANTE, area,
                f"{ident}: INCUMPLIMIENTO del covenant "
                f"'{r[c_cov] if c_cov else ''}' (exigido {sentido} {exigido:,.4f}, "
                f"real {real:,.4f}).",
                importe=round(real - exigido, 4), origen="listado de covenants",
                causa_sugerida="Deterioro de los ratios financieros en el ejercicio.",
                accion="Obtener waiver de la entidad con fecha anterior al cierre. Sin "
                       "waiver, reclasificar la deuda a corriente y evaluar el efecto "
                       "sobre la empresa en funcionamiento y sobre el desglose de memoria.",
                referencia_normativa="PGC NRV 9ª; NIA-ES 570 (Revisada)",
            ))
    res.datos = {"covenants": len(df), "incumplidos": incumplidos}
    res.conclusion = ("Todos los covenants verificados se cumplen a la fecha de cierre."
                      if not incumplidos else
                      f"{incumplidos} covenants incumplidos. Efecto potencial en la "
                      "clasificacion de la deuda y en la opinion.")
    return res
