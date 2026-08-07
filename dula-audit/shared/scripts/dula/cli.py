"""Interfaz de linea de comandos.

Todas las skills invocan la libreria a traves de este CLI, de forma que el
calculo sea reproducible por un revisor ejecutando el mismo comando.

    python -m dula.cli <subcomando> --help
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any

import pandas as pd

from . import (amortizaciones, analiticos, asientos, calidad, comparador,
               cuadres, financiacion, ingesta, leasing, materialidad, muestreo,
               perfil)
from .encargo import Encargo
from .excel_out import PapelDeTrabajo, exporta_tablas
from .excepciones import Resultado
from .traza import RegistroTrazas, Traza, huella


def _salida(res: Resultado, json_out: bool = False) -> None:
    if json_out:
        print(json.dumps({
            "concepto": res.concepto, "conclusion": res.conclusion,
            "datos": res.datos,
            "excepciones": [e.dict() for e in res.ordenadas()],
        }, ensure_ascii=False, indent=2, default=str))
    else:
        print(res.resumen())


def _papel(args, ref: str, titulo: str, res: Resultado,
           detalles: dict[str, tuple[pd.DataFrame, list[str]]] | None = None,
           reg: RegistroTrazas | None = None, alcance: str = "",
           fundamento: str = "") -> str | None:
    if not getattr(args, "papel", None):
        return None
    p = PapelDeTrabajo(ref, titulo, getattr(args, "cliente", "") or "(cliente)",
                       getattr(args, "ejercicio", 0) or 0)
    p.alcance(alcance or res.concepto).fundamento(fundamento)
    p.concluye(res.conclusion, "CON EXCEPCIONES" if res.excepciones else "LIMPIO")
    for nombre, valor in res.datos.items():
        p.indicador(nombre.replace("_", " ").capitalize(), valor)
    for nombre, (df, totales) in (detalles or {}).items():
        p.detalle(df, nombre, totales)
    if reg:
        p.trazas(reg)
    p.excepciones(res.excepciones)
    ruta = p.guardar(args.papel)
    print(f"\nPapel de trabajo: {ruta}")
    return ruta


# ---------------------------------------------------------------------------
def cmd_nuevo(args) -> int:
    enc = Encargo.crear(args.carpeta, args.cliente, args.ejercicio, args.marco)
    print(f"Encargo creado en {enc.carpeta}")
    print(f"  {enc.ruta}")
    for sub in ("00-fuentes", "01-papeles", "02-documentos"):
        print(f"  {os.path.join(enc.carpeta, sub)}/")
    return 0


def cmd_ingesta(args) -> int:
    sys_df, meta = ingesta.normaliza_sumas_y_saldos(args.sumas_y_saldos, args.hoja)
    print(f"Balance de sumas y saldos: {meta['registros']} cuentas, "
          f"grupos {''.join(meta['grupos'])}, longitudes {meta['longitudes_cuenta']}")
    print(f"  Cabecera en la fila {meta['fila_cabecera']}; columnas {meta['columnas']}")

    diario_df = None
    if args.diario:
        diario_df, meta_d = ingesta.normaliza_diario(args.diario, args.hoja_diario)
        print(f"Diario: {meta_d['apuntes']} apuntes en {meta_d['asientos']} asientos")

    anterior_df = None
    if args.anterior:
        anterior_df, _ = ingesta.normaliza_sumas_y_saldos(args.anterior)

    resultados, ok = cuadres.ejecuta_todos(sys_df, diario_df, anterior_df, args.ejercicio)

    reg = RegistroTrazas()
    reg.anota("Total debe", round(float(sys_df["debe"].sum()), 2),
              Traza(meta["fichero"], meta["hoja"], "columna " + meta["columnas"].get("debe", "?")))
    reg.anota("Total haber", round(float(sys_df["haber"].sum()), 2),
              Traza(meta["fichero"], meta["hoja"], "columna " + meta["columnas"].get("haber", "?")))
    reg.anota("Numero de cuentas", meta["registros"], Traza(meta["fichero"], meta["hoja"]))

    todas: list[Any] = []
    for r in resultados:
        print()
        print(r.resumen())
        todas.extend(r.excepciones)

    global_ = Resultado("Ingesta y cuadres de integridad")
    global_.excepciones = todas
    global_.datos = {r.concepto: r.datos for r in resultados}
    global_.conclusion = ("Todos los cuadres de integridad pasan. Se puede continuar con el "
                          "trabajo de campo." if ok else
                          "HAY CUADRES QUE NO PASAN. El trabajo de campo queda detenido "
                          "hasta su resolucion.")
    print()
    print("=" * 70)
    print(global_.conclusion)

    if args.papel:
        epigrafes = comparador.agrega_por_epigrafe(sys_df)
        df_ep = pd.DataFrame([{"epigrafe": k, "importe": v}
                              for k, v in sorted(epigrafes.items())])
        _papel(args, "2.1", "Ingesta y cuadres de integridad", global_,
               {"Sumas y saldos": (sys_df, ["debe", "haber", "saldo"]),
                "Epigrafes": (df_ep, ["importe"])}, reg,
               alcance="Normalizacion del balance de sumas y saldos y del libro diario, y "
                       "ejecucion de la bateria de cuadres de integridad previa al trabajo "
                       "de campo.")

    if args.encargo:
        enc = Encargo.abrir(args.encargo)
        enc.registra_fuente(args.sumas_y_saldos, huella(args.sumas_y_saldos),
                            "Balance de sumas y saldos")
        if args.diario:
            enc.registra_fuente(args.diario, huella(args.diario), "Libro diario")
        enc.registra_papel("2.1", "Ingesta y cuadres de integridad",
                           args.papel or "", global_.conclusion,
                           estado="concluido" if ok else "en curso")
        enc.registra_excepciones(todas, "2.1")
        enc.guardar()
        print(f"Estado actualizado en {enc.ruta}")

    return 0 if ok else 2


def cmd_materialidad(args) -> int:
    cifras = json.loads(args.cifras) if args.cifras.strip().startswith("{") \
        else json.load(open(args.cifras, encoding="utf-8"))
    mat = materialidad.calcula(cifras, args.perfil, args.magnitud, args.porcentaje,
                               traza=args.traza or "")
    for spec in args.especifica or []:
        area, factor, motivo = spec.split(":", 2)
        materialidad.especifica(mat, area, motivo, float(factor))
    print(mat.resumen())
    print()
    print("FUNDAMENTO:")
    print(mat.fundamento)

    if args.encargo:
        enc = Encargo.abrir(args.encargo)
        anterior = enc.materialidad_vigente
        registro = mat.dict()
        if anterior:
            ev = materialidad.evalua_recalculo(anterior, mat)
            registro["recalculo_evaluado"] = True
            registro["evaluacion_recalculo"] = ev
            print()
            print(ev["mensaje"])
        enc.fija_materialidad(registro)
        enc.guardar()
        print(f"\nMaterialidad registrada en {enc.ruta}")
    return 0


def cmd_estimar(args) -> int:
    drivers = json.loads(args.drivers) if args.drivers.strip().startswith("{") \
        else json.load(open(args.drivers, encoding="utf-8"))
    tarifas = None
    if args.tarifas:
        tarifas = json.loads(args.tarifas) if args.tarifas.strip().startswith("{") \
            else json.load(open(args.tarifas, encoding="utf-8"))

    puntuacion, detalle = perfil.puntua(drivers)
    p, motivo = perfil.clasifica_perfil(
        puntuacion, eip=bool(drivers.get("eip")),
        consolidacion=str(drivers.get("consolidacion", "no")).lower() == "si")
    est = perfil.estima(drivers, p, tarifas)
    factores = perfil.factores_encarecedores(detalle)
    cfg = perfil.configuracion(p)

    print(f"PERFIL: {p}  (puntuacion {puntuacion}/100)")
    print(motivo)
    print()
    print(f"Horas estimadas con plugin: {est['horas_totales']} h "
          f"(sin plugin: {est['horas_sin_plugin']} h, ahorro {est['ahorro_horas']} h)")
    print(f"Rango: optimista {est['rango_horas']['optimista']} h / esperado "
          f"{est['rango_horas']['esperado']} h / pesimista "
          f"{est['rango_horas']['pesimista']} h")
    print(f"Por categoria: {est['por_categoria']}")
    if isinstance(est.get("honorarios"), dict):
        h = est["honorarios"]
        print(f"Honorarios estimados: {h['total']:,.2f} EUR "
              f"(rango {h['rango']['optimista']:,.2f} - {h['rango']['pesimista']:,.2f})")
        if isinstance(est.get("punto_muerto"), dict):
            pm = est["punto_muerto"]
            print(f"Punto muerto (coste directo del equipo): "
                  f"{pm['coste_directo_equipo']:,.2f} EUR | margen "
                  f"{pm['margen_esperado']:,.2f} EUR ({pm['margen_pct']:.1%})")
    else:
        print(f"Honorarios: {est['honorarios']} - {est.get('nota_honorarios', '')}")

    print("\nFACTORES QUE MAS ENCARECEN EL ENCARGO:")
    for f in factores:
        print(f"  [{f['puntos']:2d} pts] {f['factor']} = {f['valor']}")
        print(f"           Palanca: {f['palanca']}")

    print("\nCONFIGURACION DEL PERFIL:")
    for k, v in cfg.items():
        print(f"  {k}: {v}")

    if args.excel:
        exporta_tablas(args.excel, {
            "Drivers": pd.DataFrame(detalle),
            "Horas por area": pd.DataFrame(est["areas"]),
            "Factores": pd.DataFrame(factores),
            "Configuracion": pd.DataFrame([{"parametro": k, "valor": str(v)}
                                           for k, v in cfg.items()]),
        })
        print(f"\nInforme de estimacion: {os.path.abspath(args.excel)}")

    if args.encargo:
        enc = Encargo.abrir(args.encargo)
        enc.datos["perfil"] = {"puntuacion": puntuacion, "perfil": p, "motivo": motivo,
                               "drivers": drivers, "detalle": detalle,
                               "estimacion": est, "configuracion": cfg}
        enc.guardar()
        print(f"\nPerfil registrado en {enc.ruta}")
    return 0


def cmd_leasing(args) -> int:
    df, meta = ingesta.lee_tabla(args.contratos, args.hoja)
    res, resumen, cuadros = leasing.procesa_lote(df, args.cierre,
                                                 os.path.basename(args.contratos))
    print(res.resumen())
    por_ejercicio = leasing.cuadro_por_ejercicio(cuadros)

    if args.saldo_174 is not None or args.saldo_524 is not None:
        conc = leasing.conciliacion_contable(resumen, args.saldo_174 or 0.0,
                                             args.saldo_524 or 0.0)
        print()
        print(conc.resumen())
        res.excepciones.extend(conc.excepciones)
        res.datos.update(conc.datos)

    reg = RegistroTrazas()
    for _, r in resumen.head(500).iterrows():
        reg.anota(f"Deuda viva {r['id']}", r.get("deuda_viva_cierre"),
                  Traza(meta["fichero"], meta["hoja"], f"fila del contrato {r['id']}"))

    _papel(args, "F-1", "Arrendamientos - recalculo y clasificacion", res,
           {"Resumen contratos": (resumen, ["importe_financiado", "deuda_viva_cierre",
                                            "corriente_524", "no_corriente_174",
                                            "intereses_ejercicio"]),
            "Cuadro por ejercicio": (por_ejercicio, ["cuotas", "carga_financiera",
                                                     "amortizacion_capital"]),
            "Cuadro detallado": (cuadros.head(20000), ["cuota", "interes",
                                                       "amortizacion_capital"])},
           reg,
           alcance="Ingesta en lote de los contratos de arrendamiento, recalculo del tipo "
                   "implicito, clasificacion financiero/operativo motivada, construccion "
                   "del cuadro de cuotas, periodificacion de la carga financiera, reparto "
                   "corriente/no corriente y conciliacion con la contabilidad.",
           fundamento="Se procesa el 100% de la poblacion de contratos mediante recalculo "
                      "determinista, por lo que no procede muestreo para la verificacion "
                      "aritmetica. El muestreo se reserva para la verificacion documental "
                      "de los terminos contra el contrato original.")
    if args.excel:
        exporta_tablas(args.excel, {"Resumen": resumen, "Por ejercicio": por_ejercicio,
                                    "Cuadro completo": cuadros})
        print(f"Anexo: {os.path.abspath(args.excel)}")
    return 0 if res.ok else 2


def cmd_financiacion(args) -> int:
    df, meta = ingesta.lee_tabla(args.cartera, args.hoja)
    res, resumen = financiacion.procesa_cartera(df, args.cierre,
                                                os.path.basename(args.cartera))
    print(res.resumen())
    detalles = {"Cartera": (resumen, ["nominal_limite", "deuda_viva", "corriente",
                                      "no_corriente", "intereses_ejercicio"])}
    if args.confirmaciones:
        dfc, _ = ingesta.lee_tabla(args.confirmaciones)
        rc = financiacion.seguimiento_confirmaciones(dfc)
        print()
        print(rc.resumen())
        res.excepciones.extend(rc.excepciones)
        detalles["Confirmaciones"] = (dfc, [])
    if args.covenants:
        dfv, _ = ingesta.lee_tabla(args.covenants)
        rv = financiacion.verifica_covenants(dfv)
        print()
        print(rv.resumen())
        res.excepciones.extend(rv.excepciones)
        detalles["Covenants"] = (dfv, [])
    _papel(args, "E-1", "Financiacion - recalculo de la cartera", res, detalles,
           alcance="Recalculo del coste amortizado, la deuda viva, el reparto "
                   "corriente/no corriente y los intereses devengados de la totalidad de "
                   "los instrumentos de financiacion, seguimiento de las confirmaciones "
                   "bancarias y verificacion de covenants.")
    return 0 if res.ok else 2


def cmd_amortizaciones(args) -> int:
    df, meta = ingesta.lee_tabla(args.inventario, args.hoja)
    res, detalle = amortizaciones.recalcula(df, args.inicio, args.fin,
                                            fichero_origen=os.path.basename(args.inventario))
    print(res.resumen())
    det = amortizaciones.indicios_deterioro(detalle)
    print()
    print(det.resumen())
    res.excepciones.extend(det.excepciones)
    _papel(args, "A-1", "Inmovilizado - recalculo de amortizaciones", res,
           {"Inventario": (detalle, ["coste", "aa_inicial", "dotacion_recalculada",
                                     "dotacion_contable", "diferencia",
                                     "vnc_recalculado"])},
           alcance="Recalculo integral de la amortizacion del ejercicio elemento a "
                   "elemento, con prorrateo por dias en altas y bajas, y contraste contra "
                   "la dotacion contabilizada.")
    return 0 if res.ok else 2


def cmd_asientos(args) -> int:
    diario, meta = ingesta.normaliza_diario(args.diario, args.hoja)
    res, seleccion = asientos.analiza(diario, args.cierre, args.materialidad,
                                      args.perfil)
    print(res.resumen())
    _papel(args, "2.8", "Test de asientos del diario", res,
           {"Asientos seleccionados": (seleccion, ["importe"])},
           alcance="Analisis de la totalidad de los asientos del ejercicio mediante "
                   "filtros de inusualidad, con priorizacion por puntuacion, en respuesta "
                   "al riesgo de elusion de los controles por la direccion.",
           fundamento="NIA-ES 240.32.a). El riesgo de elusion de controles por la direccion "
                      "se presume presente en todas las entidades, con independencia de la "
                      "valoracion del riesgo de fraude.")
    return 0


def cmd_comparar(args) -> int:
    resultados: list[Resultado] = []
    if args.ccaa and args.sumas_y_saldos:
        sys_df, _ = ingesta.normaliza_sumas_y_saldos(args.sumas_y_saldos)
        ccaa = json.load(open(args.ccaa, encoding="utf-8"))
        resultados.append(comparador.ccaa_vs_sumas_y_saldos(ccaa, sys_df))
    if args.memoria_desgloses and args.estados:
        d = json.load(open(args.memoria_desgloses, encoding="utf-8"))
        e = json.load(open(args.estados, encoding="utf-8"))
        resultados.append(comparador.memoria_vs_estados(d, e))
    if args.memoria_texto:
        texto = open(args.memoria_texto, encoding="utf-8").read()
        anterior = (open(args.memoria_anterior, encoding="utf-8").read()
                    if args.memoria_anterior else None)
        contexto = json.loads(args.contexto) if args.contexto else {}
        resultados.append(comparador.checklist_memoria(texto, args.modelo, contexto,
                                                       anterior))
    if args.borrador_anterior and args.borrador_nuevo:
        a = json.load(open(args.borrador_anterior, encoding="utf-8"))
        b = json.load(open(args.borrador_nuevo, encoding="utf-8"))
        resultados.append(comparador.diff_borradores(a, b))
    if args.informe and args.ccaa_definitivas:
        i = json.load(open(args.informe, encoding="utf-8"))
        c = json.load(open(args.ccaa_definitivas, encoding="utf-8"))
        resultados.append(comparador.informe_vs_ccaa_definitivas(i, c))

    if not resultados:
        print("Nada que comparar. Vease --help para las combinaciones disponibles.")
        return 1

    total = Resultado("Comparador documental")
    for r in resultados:
        print(r.resumen())
        print()
        total.excepciones.extend(r.excepciones)
        total.datos[r.concepto] = r.datos
    total.conclusion = ("Todas las comparaciones cuadran." if total.ok and not total.excepciones
                        else f"{len(total.excepciones)} diferencias detectadas.")
    print("=" * 70)
    print(total.conclusion)
    _papel(args, "2.10", "Comparador documental", total, None, None,
           alcance="Comparacion sistematica entre cuentas anuales, balance de sumas y "
                   "saldos, memoria, borradores sucesivos e informe de auditoria.")
    return 0 if total.ok else 2


def cmd_muestreo(args) -> int:
    df, meta = ingesta.lee_tabla(args.poblacion, args.hoja)
    col = args.columna
    df[col] = ingesta.num(df, col)
    if args.metodo == "mus":
        m = muestreo.mus(df, col, args.materialidad, args.riesgo, args.errores,
                         args.semilla)
    elif args.metodo == "atributos":
        m = muestreo.atributos(df, args.frecuencia, args.semilla)
    else:
        m = muestreo.dirigido(df, col, args.materialidad, semilla=args.semilla)
    print(m.resumen())
    print()
    print("FUNDAMENTO:")
    print(m.fundamento)
    if args.excel:
        exporta_tablas(args.excel, {"Seleccion": m.seleccion,
                                    "Examen individual": m.estrato_alto})
        print(f"\nSeleccion: {os.path.abspath(args.excel)}")
    return 0


def cmd_calidad(args) -> int:
    enc = Encargo.abrir(args.encargo)
    res = calidad.revisa(enc.datos, pre_vuelo=args.pre_vuelo)
    print(calidad.panel_del_socio(enc.datos, res))
    print()
    print("=" * 78)
    print("LISTADO COMPLETO DE EXCEPCIONES")
    print("=" * 78)
    for e in res.ordenadas():
        print(f"[{e.severidad:11s}] {e.codigo} {e.area:6s} {e.descripcion}")
        print(f"{'':14s} -> {e.accion}")
        if e.referencia_normativa:
            print(f"{'':14s}    ({e.referencia_normativa})")
    if not res.excepciones:
        print("Sin excepciones.")
    print()
    print(res.conclusion)
    _papel(args, "9.2", "Revision de calidad del archivo", res, None, None,
           alcance="Revision independiente del archivo completo: cobertura de riesgos, "
                   "conclusiones soportadas, cuadres, materialidad vigente, evaluacion de "
                   "incorrecciones, reconstruibilidad de la documentacion y coherencia del "
                   "informe con el archivo.")
    if args.panel:
        with open(args.panel, "w", encoding="utf-8") as fh:
            fh.write(calidad.panel_del_socio(enc.datos, res))
        print(f"\nPanel del socio: {os.path.abspath(args.panel)}")
    return 0 if res.datos["puede_firmarse"] else 2


def cmd_analiticos(args) -> int:
    actual = json.load(open(args.actual, encoding="utf-8"))
    anterior = json.load(open(args.anterior, encoding="utf-8"))
    umbral = analiticos.umbral_investigacion(args.materialidad, args.factor)
    print(umbral["fundamento"])
    print()
    res, detalle = analiticos.variaciones(actual, anterior, umbral)
    print(res.resumen())
    res_r, ratios_df = analiticos.ratios(actual, anterior)
    print()
    print(res_r.resumen())
    res.excepciones.extend(res_r.excepciones)
    _papel(args, "1.6", "Procedimientos analiticos", res,
           {"Variaciones": (detalle, ["ejercicio_actual", "ejercicio_anterior",
                                      "variacion"]),
            "Ratios": (ratios_df, [])},
           alcance="Procedimientos analiticos con umbral de investigacion definido con "
                   "caracter previo al analisis de las cifras.",
           fundamento=umbral["fundamento"])
    return 0


# ---------------------------------------------------------------------------
def construye_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="dula", description="Libreria de calculo determinista de dula-audit.")
    p.add_argument("--json", action="store_true", help="salida en JSON")
    sub = p.add_subparsers(dest="cmd", required=True)

    def comunes(sp):
        sp.add_argument("--papel", help="ruta del papel de trabajo .xlsx a generar")
        sp.add_argument("--cliente", default="", help="denominacion del cliente")
        sp.add_argument("--ejercicio", type=int, default=0)
        sp.add_argument("--encargo", help="ruta de encargo.json o de su carpeta")

    s = sub.add_parser("nuevo", help="crea la carpeta y el estado del encargo")
    s.add_argument("carpeta"); s.add_argument("cliente")
    s.add_argument("ejercicio", type=int)
    s.add_argument("--marco", default="PGC-PYMES",
                   choices=["PGC", "PGC-PYMES", "PGC-CONSOLIDADO"])
    s.set_defaults(fn=cmd_nuevo)

    s = sub.add_parser("ingesta", help="normaliza y ejecuta los cuadres de integridad")
    s.add_argument("sumas_y_saldos"); s.add_argument("--diario")
    s.add_argument("--anterior", help="sumas y saldos del ejercicio anterior")
    s.add_argument("--hoja", default=0); s.add_argument("--hoja-diario", default=0)
    comunes(s); s.set_defaults(fn=cmd_ingesta)

    s = sub.add_parser("materialidad", help="determina la materialidad")
    s.add_argument("cifras", help="JSON inline o ruta a fichero JSON")
    s.add_argument("--perfil", default="ESTANDAR",
                   choices=["LIGERO", "ESTANDAR", "COMPLEJO"])
    s.add_argument("--magnitud"); s.add_argument("--porcentaje", type=float)
    s.add_argument("--traza", default="")
    s.add_argument("--especifica", action="append",
                   help="area:factor:motivo (p.ej. 'M:0.25:retribuciones de la direccion')")
    comunes(s); s.set_defaults(fn=cmd_materialidad)

    s = sub.add_parser("estimar", help="perfil de complejidad, horas y honorarios")
    s.add_argument("drivers"); s.add_argument("--tarifas")
    s.add_argument("--excel"); comunes(s); s.set_defaults(fn=cmd_estimar)

    s = sub.add_parser("leasing", help="procesa el lote de contratos de arrendamiento")
    s.add_argument("contratos"); s.add_argument("cierre")
    s.add_argument("--hoja", default=0)
    s.add_argument("--saldo-174", type=float); s.add_argument("--saldo-524", type=float)
    s.add_argument("--excel"); comunes(s); s.set_defaults(fn=cmd_leasing)

    s = sub.add_parser("financiacion", help="recalcula la cartera de financiacion")
    s.add_argument("cartera"); s.add_argument("cierre")
    s.add_argument("--hoja", default=0)
    s.add_argument("--confirmaciones"); s.add_argument("--covenants")
    comunes(s); s.set_defaults(fn=cmd_financiacion)

    s = sub.add_parser("amortizaciones", help="recalculo integral de amortizaciones")
    s.add_argument("inventario"); s.add_argument("inicio"); s.add_argument("fin")
    s.add_argument("--hoja", default=0); comunes(s)
    s.set_defaults(fn=cmd_amortizaciones)

    s = sub.add_parser("asientos", help="test de asientos del diario")
    s.add_argument("diario"); s.add_argument("cierre")
    s.add_argument("--materialidad", type=float); s.add_argument("--hoja", default=0)
    s.add_argument("--perfil", default="ESTANDAR")
    comunes(s); s.set_defaults(fn=cmd_asientos)

    s = sub.add_parser("comparar", help="comparador documental")
    s.add_argument("--ccaa"); s.add_argument("--sumas-y-saldos")
    s.add_argument("--memoria-desgloses"); s.add_argument("--estados")
    s.add_argument("--memoria-texto"); s.add_argument("--memoria-anterior")
    s.add_argument("--modelo", default="PYME", choices=["PYME", "ABREVIADA", "NORMAL"])
    s.add_argument("--contexto", help='JSON, p.ej. \'{"subvenciones": true}\'')
    s.add_argument("--borrador-anterior"); s.add_argument("--borrador-nuevo")
    s.add_argument("--informe"); s.add_argument("--ccaa-definitivas")
    comunes(s); s.set_defaults(fn=cmd_comparar)

    s = sub.add_parser("muestreo", help="selecciona la muestra")
    s.add_argument("poblacion"); s.add_argument("columna")
    s.add_argument("--metodo", default="mus", choices=["mus", "atributos", "dirigido"])
    s.add_argument("--materialidad", type=float, default=0.0)
    s.add_argument("--riesgo", type=float, default=0.05)
    s.add_argument("--errores", type=int, default=0)
    s.add_argument("--frecuencia", default="mensual")
    s.add_argument("--semilla", type=int); s.add_argument("--hoja", default=0)
    s.add_argument("--excel"); comunes(s); s.set_defaults(fn=cmd_muestreo)

    s = sub.add_parser("analiticos", help="procedimientos analiticos")
    s.add_argument("actual"); s.add_argument("anterior")
    s.add_argument("--materialidad", type=float, required=True)
    s.add_argument("--factor", type=float, default=0.5)
    comunes(s); s.set_defaults(fn=cmd_analiticos)

    s = sub.add_parser("calidad", help="revision de calidad del archivo")
    s.add_argument("encargo"); s.add_argument("--pre-vuelo", action="store_true")
    s.add_argument("--panel", help="ruta del panel del socio en texto")
    s.add_argument("--papel"); s.add_argument("--cliente", default="")
    s.add_argument("--ejercicio", type=int, default=0)
    s.set_defaults(fn=cmd_calidad)

    return p


def main(argv: list[str] | None = None) -> int:
    args = construye_parser().parse_args(argv)
    try:
        return args.fn(args)
    except Exception as exc:  # noqa: BLE001 - el CLI reporta, no traza
        print(f"ERROR: {exc}", file=sys.stderr)
        if os.environ.get("DULA_DEBUG"):
            raise
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
