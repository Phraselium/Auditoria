"""Cuadres de integridad. PUERTA DE ENTRADA al trabajo de campo.

Si algo no cuadra, el proceso se detiene y lo reporta. No se sigue trabajando
sobre una base que no cuadra: cualquier prueba posterior seria inutil.
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from .excepciones import BLOQUEANTE, DOCUMENTAR, RESOLVER, Excepcion, Resultado
from .plan_contable import clasifica, es_patrimonial, es_resultados

# Tolerancia por redondeo de centimos. Configurable en skills/convenciones-dula/SKILL.md.
TOLERANCIA = 0.01


def _dif(a: float, b: float) -> float:
    return round(a - b, 2)


def cuadre_debe_haber(sys: pd.DataFrame, area: str = "2.1") -> Resultado:
    """Sumas del balance de sumas y saldos: total debe = total haber."""
    res = Resultado("Cuadre debe = haber (sumas y saldos)")
    td, th = float(sys["debe"].sum()), float(sys["haber"].sum())
    d = _dif(td, th)
    res.datos = {"total_debe": round(td, 2), "total_haber": round(th, 2), "diferencia": d}
    if abs(d) > TOLERANCIA:
        res.add(Excepcion(
            "CUA-001", BLOQUEANTE, area,
            f"El balance de sumas y saldos no cuadra: debe {td:,.2f} vs haber {th:,.2f}.",
            importe=d, origen="balance de sumas y saldos",
            causa_sugerida="Extraccion parcial del fichero, filas de subtotal incluidas "
                           "como datos, o asientos descuadrados en el ERP.",
            accion="Solicitar nueva extraccion completa y no continuar hasta que cuadre.",
        ))
        res.conclusion = "NO CUADRA. Trabajo de campo detenido."
    else:
        res.conclusion = f"Cuadra. Debe = Haber = {td:,.2f} EUR."
    return res


def cuadre_saldos(sys: pd.DataFrame, area: str = "2.1") -> Resultado:
    """Suma de saldos = 0 (partida doble) y coherencia saldo = debe - haber."""
    res = Resultado("Cuadre de saldos")
    total = float(sys["saldo"].sum())
    res.datos = {"suma_saldos": round(total, 2)}
    if abs(total) > TOLERANCIA:
        res.add(Excepcion(
            "CUA-002", BLOQUEANTE, area,
            f"La suma de saldos del balance no es cero: {total:,.2f}.",
            importe=round(total, 2), origen="balance de sumas y saldos",
            causa_sugerida="Faltan cuentas en la extraccion o hay saldos con signo invertido.",
            accion="Revisar la extraccion completa antes de continuar.",
        ))
    incoherentes = sys[(sys["debe"] + sys["haber"] != 0)
                       & ((sys["debe"] - sys["haber"] - sys["saldo"]).abs() > TOLERANCIA)]
    for _, r in incoherentes.head(50).iterrows():
        res.add(Excepcion(
            "CUA-003", RESOLVER, area,
            f"Cuenta {r['cuenta']}: saldo informado {r['saldo']:,.2f} no coincide con "
            f"debe - haber ({r['debe'] - r['haber']:,.2f}).",
            importe=_dif(r["saldo"], r["debe"] - r["haber"]), cuenta=r["cuenta"],
            origen=f"fila {r['_fila_origen']}",
            causa_sugerida="Saldo de apertura no incluido en las sumas, o columna de "
                           "saldo calculada sobre otro periodo.",
            accion="Confirmar con el cliente el periodo de las columnas debe/haber.",
        ))
    if len(incoherentes) > 50:
        res.add(Excepcion(
            "CUA-003", RESOLVER, area,
            f"...y {len(incoherentes) - 50} cuentas mas con la misma incoherencia.",
            origen="balance de sumas y saldos",
            accion="Revisar el criterio de la columna de saldo en la extraccion.",
        ))
    if res.ok and not res.excepciones:
        res.conclusion = "Cuadra. Suma de saldos = 0 y saldo = debe - haber en todas las cuentas."
    elif res.ok:
        res.conclusion = f"Suma de saldos correcta, {len(incoherentes)} incoherencias de detalle."
    else:
        res.conclusion = "NO CUADRA. Trabajo de campo detenido."
    return res


def cuadre_diario_vs_sys(diario: pd.DataFrame, sys: pd.DataFrame,
                         area: str = "2.2") -> Resultado:
    """Diario <-> sumas y saldos, cuenta a cuenta."""
    res = Resultado("Cuadre diario <-> sumas y saldos")
    agg = diario.groupby("cuenta")[["debe", "haber"]].sum().round(2)
    ref = sys.groupby("cuenta")[["debe", "haber"]].sum().round(2)
    comp = agg.join(ref, how="outer", lsuffix="_diario", rsuffix="_sys").fillna(0.0)
    comp["dif_debe"] = (comp["debe_diario"] - comp["debe_sys"]).round(2)
    comp["dif_haber"] = (comp["haber_diario"] - comp["haber_sys"]).round(2)
    descuadres = comp[(comp["dif_debe"].abs() > TOLERANCIA)
                      | (comp["dif_haber"].abs() > TOLERANCIA)]
    res.datos = {
        "cuentas_diario": int(agg.shape[0]),
        "cuentas_sys": int(ref.shape[0]),
        "cuentas_descuadradas": int(descuadres.shape[0]),
        "total_dif_debe": round(float(comp["dif_debe"].sum()), 2),
    }
    for cuenta, r in descuadres.head(100).iterrows():
        res.add(Excepcion(
            "CUA-010", BLOQUEANTE, area,
            f"Cuenta {cuenta}: diario (D {r['debe_diario']:,.2f} / H {r['haber_diario']:,.2f}) "
            f"no coincide con sumas y saldos (D {r['debe_sys']:,.2f} / H {r['haber_sys']:,.2f}).",
            importe=float(r["dif_debe"] or r["dif_haber"]), cuenta=str(cuenta),
            origen="diario vs sumas y saldos",
            causa_sugerida="Diario extraido de un rango de fechas distinto, o cuenta "
                           "creada/renumerada durante el ejercicio.",
            accion="Solicitar diario del ejercicio completo con el mismo corte.",
        ))
    res.conclusion = ("Cuadra cuenta a cuenta." if descuadres.empty
                      else f"NO CUADRA: {len(descuadres)} cuentas con diferencias.")
    return res


def cuadre_asientos(diario: pd.DataFrame, area: str = "2.3") -> Resultado:
    """Cada asiento cuadra individualmente + huecos de numeracion."""
    res = Resultado("Cuadre por asiento e integridad de la numeracion")
    por_asiento = diario.groupby("asiento")[["debe", "haber"]].sum().round(2)
    por_asiento["dif"] = (por_asiento["debe"] - por_asiento["haber"]).round(2)
    descuadrados = por_asiento[por_asiento["dif"].abs() > TOLERANCIA]
    for asiento, r in descuadrados.head(50).iterrows():
        res.add(Excepcion(
            "CUA-020", BLOQUEANTE, area,
            f"Asiento {asiento} descuadrado por {r['dif']:,.2f}.",
            importe=float(r["dif"]), origen=f"asiento {asiento}",
            causa_sugerida="Extraccion truncada del asiento o error de captura del ERP.",
            accion="Solicitar el detalle completo del asiento.",
        ))

    # huecos de numeracion (solo si la numeracion es integra)
    huecos: list[int] = []
    try:
        nums = sorted({int(str(a).strip()) for a in diario["asiento"].unique()
                       if str(a).strip().isdigit()})
        if len(nums) > 1:
            completo = set(range(nums[0], nums[-1] + 1))
            huecos = sorted(completo - set(nums))
    except (ValueError, TypeError):
        huecos = []
    if huecos:
        muestra = ", ".join(str(h) for h in huecos[:20])
        res.add(Excepcion(
            "CUA-021", RESOLVER, area,
            f"{len(huecos)} huecos en la numeracion de asientos (ej.: {muestra}).",
            origen="libro diario",
            causa_sugerida="Asientos anulados, numeracion por diarios separados, o "
                           "asientos eliminados tras su contabilizacion.",
            accion="Obtener explicacion del cliente y, si son eliminaciones, evaluar el "
                   "riesgo de elusion de controles por la direccion.",
            referencia_normativa="NIA-ES 240",
        ))
    res.datos = {"asientos": int(por_asiento.shape[0]),
                 "descuadrados": int(descuadrados.shape[0]),
                 "huecos": len(huecos)}
    res.conclusion = ("Todos los asientos cuadran y la numeracion es correlativa."
                      if not res.excepciones else
                      f"{len(descuadrados)} asientos descuadrados, {len(huecos)} huecos.")
    return res


def cuadre_fechas(diario: pd.DataFrame, ejercicio: int, area: str = "2.4") -> Resultado:
    """Asientos fuera del ejercicio auditado."""
    res = Resultado("Asientos fuera de ejercicio")
    if "fecha" not in diario.columns or diario["fecha"].isna().all():
        res.conclusion = "No verificable: el diario no incluye fecha."
        res.add(Excepcion(
            "CUA-030", DOCUMENTAR, area,
            "El diario recibido no incluye columna de fecha; no se ha podido verificar "
            "el corte de ejercicio sobre el propio fichero.",
            origen="libro diario",
            accion="Solicitar reextraccion con fecha de asiento.",
        ))
        return res
    fuera = diario[diario["fecha"].notna() & (diario["fecha"].dt.year != ejercicio)]
    res.datos = {"apuntes_fuera": int(len(fuera)),
                 "importe": round(float(fuera["debe"].sum()), 2)}
    if not fuera.empty:
        años = ", ".join(str(a) for a in sorted(fuera["fecha"].dt.year.unique()))
        res.add(Excepcion(
            "CUA-031", RESOLVER, area,
            f"{len(fuera)} apuntes con fecha fuera del ejercicio {ejercicio} (anos: {años}), "
            f"por {fuera['debe'].sum():,.2f} EUR al debe.",
            importe=round(float(fuera["debe"].sum()), 2), origen="libro diario",
            causa_sugerida="Asiento de apertura incluido en la extraccion, o contabilizacion "
                           "en periodo incorrecto.",
            accion="Separar el asiento de apertura y verificar el corte de operaciones.",
        ))
    res.conclusion = ("Todos los apuntes estan dentro del ejercicio."
                      if fuera.empty else f"{len(fuera)} apuntes fuera de ejercicio.")
    return res


def cuadre_apertura(sys: pd.DataFrame, cierre_anterior: pd.DataFrame | None,
                    area: str = "2.5") -> Resultado:
    """Apertura del ejercicio <-> cierre del ejercicio anterior."""
    res = Resultado("Cuadre apertura <-> cierre anterior")
    if cierre_anterior is None:
        res.conclusion = "No ejecutado: no se ha aportado el balance del ejercicio anterior."
        res.add(Excepcion(
            "CUA-040", RESOLVER, area,
            "No se ha aportado el balance de cierre del ejercicio anterior.",
            origen="documentacion del cliente",
            accion="Solicitar balance de sumas y saldos del ejercicio anterior.",
        ))
        return res
    if "apertura" not in sys.columns or sys["apertura"].abs().sum() == 0:
        res.conclusion = "No verificable: el balance no incluye columna de apertura."
        res.add(Excepcion(
            "CUA-041", DOCUMENTAR, area,
            "El balance de sumas y saldos no incluye saldos de apertura.",
            origen="balance de sumas y saldos",
            accion="Solicitar reextraccion con saldo inicial.",
        ))
        return res
    ap = sys.groupby("cuenta")["apertura"].sum().round(2)
    ci = cierre_anterior.groupby("cuenta")["saldo"].sum().round(2)
    comp = pd.concat([ap, ci], axis=1, keys=["apertura", "cierre_ant"]).fillna(0.0)
    # las cuentas de resultados no arrastran saldo: se regularizan a 129/120
    comp = comp[[es_patrimonial(c) for c in comp.index]]
    comp["dif"] = (comp["apertura"] - comp["cierre_ant"]).round(2)
    dif = comp[comp["dif"].abs() > TOLERANCIA]
    res.datos = {"cuentas_comparadas": int(comp.shape[0]),
                 "cuentas_con_diferencia": int(dif.shape[0]),
                 "diferencia_total": round(float(comp["dif"].sum()), 2)}
    for cuenta, r in dif.head(100).iterrows():
        res.add(Excepcion(
            "CUA-042", RESOLVER, area,
            f"Cuenta {cuenta}: apertura {r['apertura']:,.2f} no coincide con el cierre "
            f"anterior {r['cierre_ant']:,.2f}.",
            importe=float(r["dif"]), cuenta=str(cuenta),
            origen="apertura vs cierre anterior",
            causa_sugerida="Reformulacion de cuentas del ejercicio anterior, correccion de "
                           "errores (NRV 22ª) o reclasificacion no comunicada.",
            accion="Obtener conciliacion del cliente; si es correccion de error, verificar "
                   "su tratamiento y desglose en memoria.",
        ))
    res.conclusion = ("La apertura coincide con el cierre anterior."
                      if dif.empty else f"{len(dif)} cuentas con diferencia de apertura.")
    return res


def esta_regularizado(sys: pd.DataFrame) -> bool:
    """¿El balance esta tomado despues del asiento de regularizacion?

    Se detecta por la firma caracteristica: las cuentas de los grupos 6 y 7
    tienen movimiento (debe + haber) pero saldo nulo, porque la regularizacion
    las ha cancelado contra la 129.
    """
    r = sys[[es_resultados(c) for c in sys["cuenta"]]]
    if r.empty:
        return False
    movimiento = float((r["debe"] + r["haber"]).sum())
    saldo = abs(float(r["saldo"].sum()))
    return movimiento > TOLERANCIA and saldo <= TOLERANCIA


def resultado_desde_diario(diario: pd.DataFrame) -> float | None:
    """Resultado del ejercicio calculado sobre el diario, excluyendo el asiento
    de regularizacion (el que mueve la 129 contra los grupos 6 y 7)."""
    if diario is None or diario.empty:
        return None
    asientos_reg = set(diario[diario["cuenta"].str.startswith("129")]["asiento"].unique())
    real = diario[~diario["asiento"].isin(asientos_reg)]
    r = real[[es_resultados(c) for c in real["cuenta"]]]
    if r.empty:
        return None
    return round(float(r["haber"].sum() - r["debe"].sum()), 2)


def cuadre_resultado(sys: pd.DataFrame, diario: pd.DataFrame | None = None,
                     area: str = "2.6") -> Resultado:
    """Resultado por grupos 6/7 <-> saldo de la cuenta 129.

    Distingue los dos estados en que puede llegar un balance de sumas y saldos:

    - PRE-REGULARIZACION (lo habitual al pedir el balance a 31/12): los grupos 6
      y 7 conservan su saldo y la 129 esta a cero o no existe. El resultado es
      -(suma de saldos de 6 y 7).
    - POST-REGULARIZACION: los grupos 6 y 7 tienen movimiento pero saldo cero, y
      la 129 recoge el resultado. En este estado el resultado NO puede deducirse
      del balance: se necesita el diario para excluir el asiento de
      regularizacion. Sin diario, la comprobacion no se puede ejecutar y asi se
      hace constar, en lugar de dar por bueno un cuadre que no se ha hecho.
    """
    res = Resultado("Cuadre del resultado del ejercicio")
    resultados = sys[[es_resultados(c) for c in sys["cuenta"]]]
    c129 = sys[sys["cuenta"].str.startswith("129")]
    saldo_129 = round(-float(c129["saldo"].sum()), 2) if not c129.empty else None
    regularizado = esta_regularizado(sys)
    res.datos = {"regularizado": regularizado, "cuenta_129": saldo_129}

    if not regularizado:
        calculado = round(-float(resultados["saldo"].sum()), 2)
        res.datos["resultado_grupos_6_7"] = calculado
        if saldo_129 is None or abs(saldo_129) <= TOLERANCIA:
            res.conclusion = (
                f"Balance tomado antes de la regularizacion. Resultado del ejercicio "
                f"segun los grupos 6 y 7: {calculado:,.2f} EUR."
                if abs(calculado) > TOLERANCIA else "Sin movimiento en grupos 6 y 7.")
            return res
        d = _dif(calculado, saldo_129)
        if abs(d) > TOLERANCIA:
            res.add(Excepcion(
                "CUA-050", BLOQUEANTE, area,
                f"El resultado por grupos 6/7 ({calculado:,.2f}) no coincide con la "
                f"cuenta 129 ({saldo_129:,.2f}), y los grupos 6 y 7 no estan "
                "regularizados.",
                importe=d, cuenta="129", origen="balance de sumas y saldos",
                causa_sugerida="Regularizacion parcial, o saldo de la 129 arrastrado del "
                               "ejercicio anterior sin aplicar.",
                accion="Obtener el detalle de la cuenta 129 y confirmar el estado del cierre.",
            ))
            res.conclusion = "NO CUADRA el resultado del ejercicio."
        else:
            res.conclusion = f"Cuadra. Resultado del ejercicio: {saldo_129:,.2f} EUR."
        return res

    # --- balance post-regularizacion ---
    desde_diario = resultado_desde_diario(diario)
    res.datos["resultado_segun_diario"] = desde_diario
    if desde_diario is None:
        res.add(Excepcion(
            "CUA-051", DOCUMENTAR, area,
            "El balance esta tomado despues de la regularizacion (los grupos 6 y 7 tienen "
            "movimiento y saldo cero), por lo que el resultado no puede verificarse sobre "
            "el propio balance.",
            cuenta="129", origen="balance de sumas y saldos",
            accion="Solicitar el libro diario para recalcular el resultado excluyendo el "
                   "asiento de regularizacion, o el balance previo a la regularizacion.",
        ))
        res.conclusion = (f"No verificable sobre el balance. Resultado segun la cuenta 129: "
                          f"{saldo_129:,.2f} EUR." if saldo_129 is not None
                          else "No verificable sobre el balance.")
        return res
    if saldo_129 is None:
        res.conclusion = (f"Resultado del ejercicio segun el diario: {desde_diario:,.2f} EUR. "
                          "No existe cuenta 129 en el balance.")
        return res
    d = _dif(desde_diario, saldo_129)
    if abs(d) > TOLERANCIA:
        res.add(Excepcion(
            "CUA-050", BLOQUEANTE, area,
            f"El resultado calculado sobre el diario ({desde_diario:,.2f}) no coincide con "
            f"la cuenta 129 del balance ({saldo_129:,.2f}).",
            importe=d, cuenta="129", origen="diario vs balance de sumas y saldos",
            causa_sugerida="Regularizacion incompleta o asientos de resultados posteriores "
                           "a la regularizacion.",
            accion="Obtener el detalle del asiento de regularizacion.",
        ))
        res.conclusion = "NO CUADRA el resultado del ejercicio."
    else:
        res.conclusion = (f"Cuadra. Resultado del ejercicio {saldo_129:,.2f} EUR, "
                          "verificado sobre el diario excluyendo la regularizacion.")
    return res


def cuentas_sin_mapeo(sys: pd.DataFrame, area: str = "2.7") -> Resultado:
    """Cuentas que no encajan en ningun epigrafe del modelo oficial."""
    res = Resultado("Mapeo de cuentas a epigrafes")
    sin: list[dict[str, Any]] = []
    for _, r in sys.iterrows():
        c = clasifica(r["cuenta"])
        if c["estado"] == "SIN MAPEO" and abs(r["saldo"]) > TOLERANCIA:
            sin.append({"cuenta": r["cuenta"], "descripcion": r["descripcion"],
                        "saldo": r["saldo"], "fila": r["_fila_origen"]})
    res.datos = {"cuentas_sin_mapeo": len(sin),
                 "importe": round(sum(abs(s["saldo"]) for s in sin), 2)}
    for s in sin[:50]:
        res.add(Excepcion(
            "CUA-060", RESOLVER, area,
            f"Cuenta {s['cuenta']} ({s['descripcion']}) con saldo {s['saldo']:,.2f} "
            "no tiene epigrafe asignado en el modelo oficial.",
            importe=s["saldo"], cuenta=s["cuenta"], origen=f"fila {s['fila']}",
            causa_sugerida="Cuenta de creacion libre por el cliente fuera del cuadro PGC.",
            accion="Asignar epigrafe manualmente y anadir la regla a mapeo-pgc.json.",
        ))
    res.conclusion = ("Todas las cuentas con saldo estan mapeadas."
                      if not sin else f"{len(sin)} cuentas con saldo sin epigrafe asignado.")
    return res


def ejecuta_todos(sys: pd.DataFrame, diario: pd.DataFrame | None = None,
                  cierre_anterior: pd.DataFrame | None = None,
                  ejercicio: int | None = None) -> tuple[list[Resultado], bool]:
    """Bateria completa. Devuelve (resultados, se_puede_continuar)."""
    resultados = [
        cuadre_debe_haber(sys),
        cuadre_saldos(sys),
        cuadre_resultado(sys, diario),
        cuentas_sin_mapeo(sys),
    ]
    if diario is not None:
        resultados.append(cuadre_diario_vs_sys(diario, sys))
        resultados.append(cuadre_asientos(diario))
        if ejercicio:
            resultados.append(cuadre_fechas(diario, ejercicio))
    resultados.append(cuadre_apertura(sys, cierre_anterior))
    puede_continuar = all(r.ok for r in resultados)
    return resultados, puede_continuar
