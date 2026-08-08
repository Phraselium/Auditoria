"""Comparador documental. El nucleo de la automatizacion.

Compara sistematicamente y reporta SOLO diferencias, con importe, cuenta, origen
y sugerencia de causa. Nunca vuelca la comparacion completa.

Comparaciones cubiertas:
  - Cuentas anuales formuladas <-> balance de sumas y saldos
  - Memoria <-> cifras de balance y cuenta de resultados
  - Memoria <-> checklist de desgloses obligatorios del modelo aplicable
  - Ejercicio <-> ejercicio anterior <-> cuentas depositadas en el Registro
  - Versiones sucesivas de borradores (diff con impacto por epigrafe)
  - Informe de gestion <-> cuentas anuales
  - Informe de auditoria <-> cuentas anuales definitivas (ultima verificacion)
"""

from __future__ import annotations

import json
import os
import re
from typing import Any

import pandas as pd

from .excepciones import (BLOQUEANTE, DOCUMENTAR, INFORMATIVA, RESOLVER,
                          Excepcion, Resultado)
from . import rutas
from .plan_contable import clasifica, es_patrimonial, es_resultados

TOLERANCIA = 1.00  # EUR. Las cuentas anuales se formulan redondeadas.




def saldos_de_presentacion(sys: pd.DataFrame,
                           diario: pd.DataFrame | None = None) -> pd.DataFrame:
    """Saldos a efectos de presentacion en las cuentas anuales.

    Si el balance esta tomado despues de la regularizacion, las cuentas de los
    grupos 6 y 7 tienen saldo cero y la cuenta de perdidas y ganancias no puede
    construirse desde el balance. En ese caso se reconstruyen sus importes desde
    el diario, excluyendo el asiento de regularizacion.

    Sin diario, se devuelve el balance tal cual y la cuenta de resultados saldra
    a cero: el comparador lo reportara como diferencia frente a las cuentas
    anuales, que es exactamente lo que debe ocurrir.
    """
    from .cuadres import esta_regularizado
    if not esta_regularizado(sys) or diario is None or diario.empty:
        return sys
    reg = set(diario[diario["cuenta"].str.startswith("129")]["asiento"].unique())
    real = diario[~diario["asiento"].isin(reg)]
    pyg = real[[es_resultados(c) for c in real["cuenta"]]]
    if pyg.empty:
        return sys
    recalculado = pyg.groupby("cuenta").apply(
        lambda g: round(float(g["debe"].sum() - g["haber"].sum()), 2),
        include_groups=False)
    out = sys.copy()
    mascara = [es_resultados(c) for c in out["cuenta"]]
    out.loc[mascara, "saldo"] = out.loc[mascara, "cuenta"].map(recalculado).fillna(0.0)
    return out


def agrega_por_epigrafe(sys: pd.DataFrame,
                        diario: pd.DataFrame | None = None) -> dict[str, float]:
    """Balance de sumas y saldos -> importes por epigrafe del modelo oficial.

    Aplica el signo de cada regla para que el epigrafe salga con el signo con el
    que figura en las cuentas anuales.
    """
    sys = saldos_de_presentacion(sys, diario)
    totales: dict[str, float] = {}
    for _, r in sys.iterrows():
        c = clasifica(r["cuenta"])
        if c["estado"] not in {"OK"}:
            continue
        saldo = float(r["saldo"])
        # En balance, activo = saldo deudor (positivo); pasivo y PN = acreedor.
        # Convencion: se presenta todo en positivo segun su naturaleza.
        if es_patrimonial(r["cuenta"]):
            masa = c["masa"]
            valor = saldo if masa.startswith("ACTIVO") else -saldo
        else:
            valor = -saldo  # ingresos (haber) positivos, gastos (debe) negativos
        clave = f"{c['masa']}|{c['epigrafe']}|{c['titulo']}"
        totales[clave] = round(totales.get(clave, 0.0) + valor * c["signo"], 2)
    return totales


def compara_importes(a: dict[str, float], b: dict[str, float],
                     etiqueta_a: str, etiqueta_b: str, area: str = "2.10",
                     codigo: str = "CMP-001", tolerancia: float = TOLERANCIA,
                     severidad: str = RESOLVER,
                     causa: str = "") -> Resultado:
    """Motor generico de comparacion. Reporta solo lo que difiere."""
    res = Resultado(f"{etiqueta_a} <-> {etiqueta_b}")
    claves = sorted(set(a) | set(b))
    diferencias = 0
    for k in claves:
        va, vb = round(a.get(k, 0.0), 2), round(b.get(k, 0.0), 2)
        d = round(va - vb, 2)
        if abs(d) <= tolerancia:
            continue
        diferencias += 1
        if k not in a:
            desc = (f"'{k}': figura en {etiqueta_b} por {vb:,.2f} EUR y no aparece en "
                    f"{etiqueta_a}.")
        elif k not in b:
            desc = (f"'{k}': figura en {etiqueta_a} por {va:,.2f} EUR y no aparece en "
                    f"{etiqueta_b}.")
        else:
            desc = (f"'{k}': {etiqueta_a} {va:,.2f} EUR frente a {etiqueta_b} "
                    f"{vb:,.2f} EUR.")
        res.add(Excepcion(
            codigo, severidad, area, desc, importe=d,
            origen=f"{etiqueta_a} / {etiqueta_b}",
            causa_sugerida=causa or "Reclasificacion no trasladada, ajuste posterior a la "
                                    "extraccion, o error de transcripcion.",
            accion="Conciliar y corregir el documento que corresponda antes de la firma.",
        ))
    res.datos = {"conceptos_comparados": len(claves), "diferencias": diferencias,
                 "importe_total_diferencias": round(
                     sum(abs(round(a.get(k, 0.0) - b.get(k, 0.0), 2)) for k in claves), 2)}
    res.conclusion = (f"Sin diferencias entre {etiqueta_a} y {etiqueta_b} "
                      f"({len(claves)} conceptos comparados, tolerancia "
                      f"{tolerancia:,.2f} EUR)." if not diferencias else
                      f"{diferencias} diferencias entre {etiqueta_a} y {etiqueta_b}.")
    return res


def ccaa_vs_sumas_y_saldos(ccaa: dict[str, float], sys: pd.DataFrame,
                           diario: pd.DataFrame | None = None,
                           area: str = "2.10") -> Resultado:
    """Cuentas anuales formuladas <-> balance de sumas y saldos.

    `ccaa` se indexa por 'MASA|EPIGRAFE|TITULO' o solo por epigrafe; se admite
    ambas formas y se normaliza.
    """
    calculado = agrega_por_epigrafe(sys, diario)
    if ccaa and "|" not in next(iter(ccaa)):
        # indexado solo por epigrafe: se reagrega el calculado igual
        reagg: dict[str, float] = {}
        for k, v in calculado.items():
            ep = k.split("|")[1]
            reagg[ep] = round(reagg.get(ep, 0.0) + v, 2)
        calculado = reagg
    return compara_importes(
        ccaa, calculado, "cuentas anuales formuladas", "balance de sumas y saldos",
        area=area, codigo="CMP-010", severidad=BLOQUEANTE,
        causa="Ajustes de auditoria o de cierre incorporados a las cuentas anuales pero "
              "no contabilizados, o al reves.")


def memoria_vs_estados(desgloses: dict[str, float], estados: dict[str, float],
                       area: str = "2.11") -> Resultado:
    """Memoria <-> cifras del balance y de la cuenta de resultados.

    `desgloses` = {concepto de memoria: total desglosado}
    `estados`   = {mismo concepto: importe del estado financiero}
    Todo desglose numerico de la memoria debe cuadrar con el estado del que
    procede. Es la comparacion que mas incidencias produce en la practica.
    """
    return compara_importes(
        desgloses, estados, "memoria", "estados financieros", area=area,
        codigo="CMP-020", severidad=RESOLVER,
        causa="Nota de memoria heredada del ejercicio anterior sin actualizar, o "
              "desglose que no recoge todos los movimientos del epigrafe.")


def ejercicio_vs_anterior(actual: dict[str, float], anterior: dict[str, float],
                          depositadas: dict[str, float] | None = None,
                          area: str = "2.12") -> Resultado:
    """Comparativa del ejercicio precedente.

    La columna comparativa de las cuentas del ejercicio debe coincidir con las
    cuentas del ejercicio anterior y con las depositadas en el Registro
    Mercantil. Una diferencia aqui es una reformulacion o una correccion de
    error que debe estar desglosada en memoria.
    """
    res = compara_importes(
        actual, anterior, "columna comparativa del ejercicio",
        "cuentas anuales del ejercicio anterior", area=area, codigo="CMP-030",
        severidad=RESOLVER,
        causa="Reformulacion, correccion de error (NRV 22ª) o reclasificacion de la "
              "comparativa no desglosada en memoria.")
    if depositadas:
        res2 = compara_importes(
            anterior, depositadas, "cuentas del ejercicio anterior",
            "cuentas depositadas en el Registro Mercantil", area=area,
            codigo="CMP-031", severidad=RESOLVER,
            causa="Las cuentas depositadas no coinciden con las aprobadas, o se "
                  "deposito una version distinta de la formulada.")
        res.excepciones.extend(res2.excepciones)
        res.datos["comparado_con_registro"] = True
        if res2.excepciones:
            res.conclusion += (f" Ademas, {len(res2.excepciones)} diferencias frente a las "
                               "cuentas depositadas en el Registro Mercantil.")
    return res


def diff_borradores(v_anterior: dict[str, float], v_nueva: dict[str, float],
                    etiqueta_ant: str = "borrador anterior",
                    etiqueta_nueva: str = "borrador nuevo",
                    area: str = "2.13") -> Resultado:
    """Diff entre versiones sucesivas de borradores, con impacto por epigrafe.

    A diferencia del resto, aqui las diferencias son INFORMATIVAS por defecto:
    no son errores, son cambios. Lo que hay que vigilar es que ningun cambio
    pase inadvertido entre una version y la firma.
    """
    res = Resultado(f"Diff {etiqueta_ant} -> {etiqueta_nueva}")
    claves = sorted(set(v_anterior) | set(v_nueva))
    cambios = 0
    for k in claves:
        va, vb = round(v_anterior.get(k, 0.0), 2), round(v_nueva.get(k, 0.0), 2)
        d = round(vb - va, 2)
        if abs(d) <= TOLERANCIA:
            continue
        cambios += 1
        pct = (d / va) if va else float("inf")
        pct_txt = f"{pct:+.1%}" if va else "nuevo"
        res.add(Excepcion(
            "CMP-040", INFORMATIVA, area,
            f"'{k}': {va:,.2f} -> {vb:,.2f} EUR ({d:+,.2f}, {pct_txt}).",
            importe=d, origen=f"{etiqueta_ant} vs {etiqueta_nueva}",
            causa_sugerida="Ajuste propuesto por el auditor, ajuste de la direccion o "
                           "correccion de la formulacion.",
            accion="Confirmar que el cambio esta identificado en el sumario de ajustes y "
                   "que no altera la conclusion de las areas ya cerradas.",
        ))
    res.datos = {"epigrafes_modificados": cambios,
                 "impacto_bruto": round(sum(abs(round(v_nueva.get(k, 0.0)
                                                      - v_anterior.get(k, 0.0), 2))
                                            for k in claves), 2)}
    res.conclusion = ("Las dos versiones son identicas." if not cambios else
                      f"{cambios} epigrafes modificados entre versiones.")
    return res


# ---------------------------------------------------------------------------
# Checklist de desgloses obligatorios de memoria
# ---------------------------------------------------------------------------
def _carga_checklist(modelo: str) -> list[dict[str, Any]]:
    with open(rutas.fichero("referencias", "desgloses-memoria.json"),
              encoding="utf-8") as fh:
        data = json.load(fh)
    modelo = modelo.upper()
    if modelo not in data["modelos"]:
        raise ValueError(f"Modelo no valido: {modelo}. Use {list(data['modelos'])}")
    aplicables = set(data["modelos"][modelo])
    return [n for n in data["notas"] if n["id"] in aplicables]


def checklist_memoria(texto_memoria: str, modelo: str = "PYME",
                      contexto: dict[str, bool] | None = None,
                      ejercicio_anterior: str | None = None,
                      area: str = "2.14") -> Resultado:
    """Memoria <-> desgloses obligatorios del modelo aplicable.

    Detecta: notas ausentes, notas presentes pero vacias, y -lo mas frecuente en
    la practica- notas heredadas del ejercicio anterior sin actualizar.

    `contexto` activa notas condicionales: {"subvenciones": True, "leasing": True...}
    """
    res = Resultado(f"Checklist de desgloses de memoria (modelo {modelo.upper()})")
    contexto = contexto or {}
    notas = _carga_checklist(modelo)
    texto = texto_memoria.lower()

    ausentes = presentes = 0
    for nota in notas:
        condicion = nota.get("condicion")
        obligatoria = nota.get("obligatoria", True)
        if condicion and not contexto.get(condicion, False):
            continue  # nota condicional cuyo supuesto no concurre
        claves = [k.lower() for k in nota["claves"]]
        encontrada = any(k in texto for k in claves)
        if not encontrada:
            ausentes += 1
            res.add(Excepcion(
                "MEM-001", RESOLVER if obligatoria else DOCUMENTAR, area,
                f"Nota {nota['id']} - {nota['titulo']}: no se ha localizado en la memoria.",
                origen="memoria", causa_sugerida="Desglose omitido o redactado con otra "
                                                 "denominacion.",
                accion=f"Verificar y, en su caso, incorporar el desglose. Contenido minimo: "
                       f"{nota['contenido']}",
                referencia_normativa=nota.get("norma", ""),
            ))
        else:
            presentes += 1

    # notas heredadas: mismo parrafo literal que el ejercicio anterior
    if ejercicio_anterior:
        heredadas = _detecta_heredadas(texto_memoria, ejercicio_anterior)
        for frag in heredadas[:20]:
            res.add(Excepcion(
                "MEM-002", RESOLVER, area,
                f"Parrafo identico al del ejercicio anterior: \"{frag[:140]}...\"",
                origen="memoria vs memoria del ejercicio anterior",
                causa_sugerida="Nota copiada del ejercicio anterior sin actualizar cifras "
                               "ni circunstancias.",
                accion="Verificar que el contenido sigue siendo aplicable y que las cifras "
                       "corresponden al ejercicio auditado.",
            ))
        res.datos["parrafos_heredados"] = len(heredadas)

    res.datos.update({"notas_aplicables": presentes + ausentes,
                      "presentes": presentes, "ausentes": ausentes})
    res.conclusion = (
        f"Los {presentes} desgloses aplicables al modelo {modelo.upper()} estan presentes."
        if not ausentes else
        f"{ausentes} desgloses obligatorios ausentes de {presentes + ausentes} aplicables.")
    return res


def _detecta_heredadas(actual: str, anterior: str, minimo_palabras: int = 25
                       ) -> list[str]:
    """Parrafos con cifras que se repiten literalmente entre ejercicios.

    Un parrafo descriptivo puede repetirse legitimamente; uno que CONTIENE CIFRAS
    y se repite literalmente es casi siempre una nota sin actualizar.
    """
    def parrafos(t: str) -> list[str]:
        return [p.strip() for p in re.split(r"\n\s*\n", t) if len(p.split()) >= minimo_palabras]

    con_cifras = re.compile(r"\d{1,3}(?:[.\s]\d{3})+(?:,\d+)?|\d+,\d{2}")
    ant = {p.strip().lower() for p in parrafos(anterior)}
    return [p for p in parrafos(actual)
            if p.strip().lower() in ant and con_cifras.search(p)]


def informe_gestion_vs_ccaa(cifras_informe: dict[str, float],
                            cifras_ccaa: dict[str, float],
                            area: str = "2.15") -> Resultado:
    """Informe de gestion <-> cuentas anuales (NIA-ES 720R).

    La responsabilidad del auditor es detectar incongruencias materiales entre
    la otra informacion y las cuentas anuales o el conocimiento obtenido.
    """
    res = compara_importes(
        cifras_informe, cifras_ccaa, "informe de gestion", "cuentas anuales",
        area=area, codigo="CMP-050", severidad=RESOLVER,
        causa="Cifra del informe de gestion tomada de una version anterior de las cuentas, "
              "o magnitud calculada con criterio distinto sin explicarlo.")
    if res.excepciones:
        res.conclusion += (" Incongruencia material entre la otra informacion y las cuentas "
                           "anuales: si no se corrige, debe describirse en la seccion "
                           "'Otra informacion' del informe de auditoria.")
    return res


def informe_vs_ccaa_definitivas(informe: dict[str, Any], ccaa: dict[str, Any],
                                area: str = "9.1") -> Resultado:
    """ULTIMA VERIFICACION ANTES DE LA FIRMA.

    Contrasta los datos identificativos del informe con las cuentas anuales
    definitivas. Los errores que se cuelan aqui -denominacion social, ejercicio,
    marco- son los que producen las incidencias mas embarazosas en inspeccion.
    """
    res = Resultado("Informe de auditoria <-> cuentas anuales definitivas")
    campos = {
        "denominacion_social": "Denominacion social",
        "nif": "NIF",
        "ejercicio": "Ejercicio auditado",
        "fecha_cierre": "Fecha de cierre",
        "marco": "Marco de informacion financiera aplicado",
        "modelo": "Modelo de cuentas (normal/abreviado/PYME)",
        "fecha_formulacion": "Fecha de formulacion",
    }
    for campo, etiqueta in campos.items():
        vi, vc = informe.get(campo), ccaa.get(campo)
        if vi is None or vc is None:
            res.add(Excepcion(
                "INF-001", RESOLVER, area,
                f"{etiqueta}: no consta en "
                f"{'el informe' if vi is None else 'las cuentas anuales'}.",
                origen="informe / cuentas anuales",
                accion="Completar el dato antes de la firma.",
            ))
            continue
        if str(vi).strip().lower() != str(vc).strip().lower():
            res.add(Excepcion(
                "INF-002", BLOQUEANTE, area,
                f"{etiqueta}: el informe dice '{vi}' y las cuentas anuales '{vc}'.",
                origen="informe / cuentas anuales",
                causa_sugerida="Informe generado sobre un borrador anterior.",
                accion="Corregir el informe antes de la firma. NO FIRMAR con esta "
                       "discrepancia.",
            ))
    # cifras clave
    for campo, etiqueta in (("total_activo", "Total activo"),
                            ("patrimonio_neto", "Patrimonio neto"),
                            ("resultado", "Resultado del ejercicio"),
                            ("cifra_negocios", "Importe neto de la cifra de negocios")):
        vi, vc = informe.get(campo), ccaa.get(campo)
        if vi is None or vc is None:
            continue
        d = round(float(vi) - float(vc), 2)
        if abs(d) > TOLERANCIA:
            res.add(Excepcion(
                "INF-003", BLOQUEANTE, area,
                f"{etiqueta}: el informe cita {float(vi):,.2f} EUR y las cuentas anuales "
                f"{float(vc):,.2f} EUR.",
                importe=d, origen="informe / cuentas anuales",
                accion="Corregir antes de la firma. NO FIRMAR con esta discrepancia.",
            ))
    res.conclusion = ("El informe es coherente con las cuentas anuales definitivas en "
                      "denominacion, ejercicio, marco y cifras." if not res.excepciones
                      else f"{len(res.excepciones)} discrepancias entre el informe y las "
                           "cuentas anuales definitivas.")
    return res


def soporte_vs_contabilidad(soporte: pd.DataFrame, contabilidad: pd.DataFrame,
                            clave: str, importe: str, area: str = "2.16",
                            tolerancia: float = TOLERANCIA) -> Resultado:
    """Documentacion soporte <-> registro contable.

    Casacion por clave (nº de factura, nº de contrato, nº de escritura) y
    contraste de importes. Reporta: en soporte y no contabilizado, contabilizado
    sin soporte, y diferencias de importe.
    """
    res = Resultado("Documentacion soporte <-> registro contable")
    s = soporte.groupby(clave)[importe].sum().round(2)
    c = contabilidad.groupby(clave)[importe].sum().round(2)
    comp = pd.concat([s, c], axis=1, keys=["soporte", "contabilidad"]).fillna(0.0)
    comp["dif"] = (comp["soporte"] - comp["contabilidad"]).round(2)

    for k, r in comp[comp["dif"].abs() > tolerancia].iterrows():
        if r["contabilidad"] == 0:
            desc = (f"{clave} {k}: documento por {r['soporte']:,.2f} EUR sin registro "
                    "contable.")
            causa = "Documento no contabilizado (posible pasivo no registrado)."
        elif r["soporte"] == 0:
            desc = (f"{clave} {k}: registro contable por {r['contabilidad']:,.2f} EUR sin "
                    "documento soporte.")
            causa = "Falta el soporte documental del asiento."
        else:
            desc = (f"{clave} {k}: soporte {r['soporte']:,.2f} EUR frente a contabilidad "
                    f"{r['contabilidad']:,.2f} EUR.")
            causa = "Contabilizacion por importe distinto al del documento."
        res.add(Excepcion(
            "CMP-060", RESOLVER, area, desc, importe=float(r["dif"]),
            origen="soporte vs contabilidad", causa_sugerida=causa,
            accion="Obtener el documento o el asiento que falta y evaluar el efecto.",
        ))
    res.datos = {"comparados": len(comp), "diferencias": int((comp["dif"].abs() > tolerancia).sum())}
    res.conclusion = ("Toda la documentacion soporte esta correctamente registrada."
                      if not res.excepciones else
                      f"{len(res.excepciones)} partidas sin correspondencia.")
    return res
