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

from . import (amortizaciones, analiticos, asientos, bitacora, calidad,
               comparador, cuadres, estado, financiacion, ingesta, leasing,
               materialidad, muestreo, perfil)
from .encargo import Encargo
from .excel_out import PapelDeTrabajo, exporta_tablas
from .excepciones import INFORMATIVA, RESOLVER, Excepcion, Resultado
from .traza import RegistroTrazas, Traza, huella

VERSION = "1.4.0"


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
    horas = getattr(args, "horas", None)
    if horas:
        p.horas(horas)
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


def _bitacora(args, skill: str, entradas: list[str], salidas: list[str],
              res: Resultado | None = None, ref: str = "",
              parametros: dict[str, Any] | None = None) -> str | None:
    """Anota la ejecucion en uso-ia.log. Exigido por NIGC1-ES.

    Solo se registra cuando hay carpeta de encargo: fuera de un encargo el
    calculo es exploratorio y no forma parte de un archivo.
    """
    carpeta = getattr(args, "encargo", None)
    if not carpeta:
        return None
    if os.path.isfile(carpeta):
        carpeta = os.path.dirname(os.path.abspath(carpeta))
    b = bitacora.Bitacora(carpeta)
    eid = b.registra(
        skill=skill, comando=" ".join(sys.argv[1:])[:400],
        entradas=[e for e in entradas if e], salidas=[s for s in salidas if s],
        parametros=parametros or {},
        conclusion=res.conclusion if res else "",
        excepciones=len(res.excepciones) if res else 0,
        papel=ref, version_plugin=VERSION)
    print(f"Bitacora: {eid} registrada en uso-ia.log "
          f"(pendiente de validacion: `dula validar {carpeta} --entrada {eid} --quien \"...\"`)")
    return eid


def _registra(args, skill: str, ref: str, titulo: str, res: Resultado,
              entradas: list[str], salidas: list[str],
              parametros: dict[str, Any] | None = None,
              riesgos: list[str] | None = None) -> None:
    """Registra el papel en el estado del encargo y anota la bitacora.

    Un papel con excepciones bloqueantes NO se marca como concluido: eso lo
    detectaria despues `revision-de-calidad`, pero es mejor no crear el problema.
    """
    if not getattr(args, "encargo", None):
        return
    enc = Encargo.abrir(args.encargo)
    for e in entradas:
        if e and os.path.isfile(e):
            enc.registra_fuente(e, huella(e), titulo)
    enc.registra_papel(ref, titulo, getattr(args, "papel", "") or "", res.conclusion,
                       riesgos or getattr(args, "riesgos", None) or [],
                       estado="concluido" if res.ok else "en curso",
                       horas=getattr(args, "horas", None))
    enc.registra_excepciones(res.excepciones, ref)
    enc.guardar()
    print(f"Estado actualizado en {enc.ruta}")
    _bitacora(args, skill, entradas, salidas, res, ref, parametros)


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
                           estado="concluido" if ok else "en curso",
                           horas=args.horas)
        enc.registra_excepciones(todas, "2.1")
        enc.guardar()
        print(f"Estado actualizado en {enc.ruta}")
        _bitacora(args, "ingesta-y-cuadres",
                  [args.sumas_y_saldos, args.diario, args.anterior],
                  [args.papel], global_, "2.1",
                  {"ejercicio": args.ejercicio, "cuadres_ok": ok})

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
        _bitacora(args, "materialidad", [], [], None, "1.4",
                  {"magnitud": mat.magnitud, "porcentaje": mat.porcentaje,
                   "global": round(mat.global_, 2), "ejecucion": round(mat.ejecucion, 2)})
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
        _bitacora(args, "estimacion-encargo", [], [args.excel], None, "0.3",
                  {"perfil": p, "puntuacion": puntuacion,
                   "horas_totales": est["horas_totales"]})
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
    _registra(args, "area-arrendamientos", "F-1", "Arrendamientos", res,
              [args.contratos], [args.papel, args.excel],
              {"contratos": res.datos.get("contratos"),
               "deuda_viva_total": res.datos.get("deuda_viva_total")})
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
    _registra(args, "area-tesoreria-y-financiacion", "E-1", "Financiacion y tesoreria",
              res, [args.cartera, args.confirmaciones, args.covenants], [args.papel],
              {"instrumentos": res.datos.get("instrumentos"),
               "deuda_viva_total": res.datos.get("deuda_viva_total")})
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
    _registra(args, "area-inmovilizado", "A-1", "Inmovilizado", res,
              [args.inventario], [args.papel],
              {"elementos": res.datos.get("elementos"),
               "diferencia_total": res.datos.get("diferencia_total")})
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
    _registra(args, "test-asientos-diario", "2.8", "Test de asientos del diario", res,
              [args.diario], [args.papel],
              {"asientos_totales": res.datos.get("asientos_totales"),
               "seleccionados": res.datos.get("seleccionados"), "perfil": args.perfil})
    return 0


def cmd_comparar(args) -> int:
    resultados: list[Resultado] = []
    if args.ccaa and args.sumas_y_saldos:
        sys_df, _ = ingesta.normaliza_sumas_y_saldos(args.sumas_y_saldos)
        diario_df = None
        if args.diario:
            diario_df, _ = ingesta.normaliza_diario(args.diario)
        ccaa = json.load(open(args.ccaa, encoding="utf-8"))
        resultados.append(comparador.ccaa_vs_sumas_y_saldos(ccaa, sys_df, diario_df))
    if args.ccaa and args.anterior_ccaa:
        # comparativa del ejercicio precedente y, en su caso, cuentas depositadas
        actual = json.load(open(args.ccaa, encoding="utf-8"))
        anterior = json.load(open(args.anterior_ccaa, encoding="utf-8"))
        depositadas = (json.load(open(args.depositadas, encoding="utf-8"))
                       if args.depositadas else None)
        resultados.append(comparador.ejercicio_vs_anterior(actual, anterior, depositadas))
    if args.informe_gestion and args.ccaa:
        ig = json.load(open(args.informe_gestion, encoding="utf-8"))
        cc = json.load(open(args.ccaa, encoding="utf-8"))
        resultados.append(comparador.informe_gestion_vs_ccaa(ig, cc))
    if args.soporte and args.contabilidad:
        sop, _ = ingesta.lee_tabla(args.soporte)
        cont, _ = ingesta.lee_tabla(args.contabilidad)
        clave = ingesta.columna(sop, args.clave) or args.clave
        col_imp = ingesta.columna(sop, args.columna_importe) or args.columna_importe
        sop[col_imp] = ingesta.num(sop, col_imp)
        cont[col_imp] = ingesta.num(cont, col_imp)
        resultados.append(comparador.soporte_vs_contabilidad(sop, cont, clave, col_imp))
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
    ref = "9.1" if (args.informe and args.ccaa_definitivas) else "2.10"
    titulo = ("Verificacion del informe contra las cuentas definitivas"
              if ref == "9.1" else "Comparador documental")
    _papel(args, ref, titulo, total, None, None,
           alcance="Comparacion sistematica entre cuentas anuales, balance de sumas y "
                   "saldos, memoria, cuentas depositadas, borradores sucesivos, informe "
                   "de gestion, documentacion soporte e informe de auditoria.")
    _registra(args, "comparador-documental", ref, titulo, total,
              [args.ccaa, args.sumas_y_saldos, args.memoria_texto, args.soporte],
              [args.papel], {"comparaciones": list(total.datos)})
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


def cmd_reservas(args) -> int:
    """Reservas indisponibles y restringidas del patrimonio neto.

    Se comprueba en planificacion, por sus implicaciones sobre la distribucion y
    sobre el efecto fiscal, y se cierra en trabajo de campo.
    """
    from . import plan_contable
    sys_df, meta = ingesta.normaliza_sumas_y_saldos(args.sumas_y_saldos, args.hoja)
    res = Resultado("Reservas indisponibles y restringidas")
    reg = RegistroTrazas()
    filas: list[dict[str, Any]] = []

    patrimonio = sys_df[sys_df["cuenta"].str.startswith(("10", "11", "12", "13"))]
    capital = round(-float(
        sys_df[sys_df["cuenta"].str.startswith("100")]["saldo"].sum()), 2)
    legal = 0.0

    for _, r in patrimonio.iterrows():
        info = plan_contable.reserva_restringida(r["cuenta"])
        saldo = round(-float(r["saldo"]), 2)  # las reservas son de saldo acreedor
        if info is None:
            continue
        if info["cuenta_pgc"].startswith("112"):
            legal = saldo
        filas.append({
            "cuenta": r["cuenta"], "descripcion": r["descripcion"],
            "reserva": info["nombre"], "saldo": saldo,
            "disponible": "SI" if info["disponible"] else "NO",
            "norma": info.get("norma", ""), "regla": info.get("regla", ""),
        })
        reg.anota(f"{info['nombre']} ({r['cuenta']})", saldo,
                  ingesta.traza_de(meta, int(r["_fila_origen"]), "saldo"))
        if not info["disponible"]:
            res.add(Excepcion(
                "RES-001", INFORMATIVA, "G",
                f"{info['nombre']} (cuenta {r['cuenta']}): {saldo:,.2f} EUR, "
                f"INDISPONIBLE. {info.get('regla', '')}".strip(),
                importe=saldo, cuenta=r["cuenta"],
                origen=f"fila {int(r['_fila_origen'])}",
                accion="Verificar dotacion, mantenimiento dentro del plazo legal y su "
                       "desglose expreso en la nota de fondos propios de la memoria.",
                referencia_normativa=info.get("norma", ""),
            ))

    # la reserva legal tiene una regla verificable de forma determinista
    if capital > 0:
        minimo = round(capital * 0.20, 2)
        if legal < minimo - 0.01:
            res.add(Excepcion(
                "RES-010", RESOLVER, "G",
                f"Reserva legal dotada {legal:,.2f} EUR frente al minimo exigible de "
                f"{minimo:,.2f} EUR (20% del capital social de {capital:,.2f} EUR).",
                importe=round(minimo - legal, 2), cuenta="112",
                origen="balance de sumas y saldos",
                causa_sugerida="Dotacion insuficiente, o la sociedad aun no ha alcanzado "
                               "el limite por no haber obtenido beneficios suficientes.",
                accion="Verificar que se ha dotado el 10% del beneficio del ejercicio. "
                       "Mientras no se alcance el 20% del capital, la dotacion es "
                       "obligatoria y limita la distribucion de dividendos.",
                referencia_normativa="art. 274 LSC",
            ))
        else:
            res.datos["reserva_legal_completa"] = True

    detalle = pd.DataFrame(filas)
    total_indisp = round(float(detalle[detalle["disponible"] == "NO"]["saldo"].sum()), 2) \
        if not detalle.empty else 0.0
    res.datos.update({
        "capital_social": capital,
        "reserva_legal": legal,
        "reservas_identificadas": len(filas),
        "total_indisponible": total_indisp,
    })
    res.conclusion = (
        f"Identificadas {len(filas)} reservas, de las que {total_indisp:,.2f} EUR son "
        f"INDISPONIBLES. Reserva legal {legal:,.2f} EUR sobre un capital de "
        f"{capital:,.2f} EUR."
        + (" Sin incidencias en la dotacion." if res.ok and not res.excepciones
           or all(e.severidad == INFORMATIVA for e in res.excepciones)
           else " Ver excepciones."))
    print(res.resumen())
    print("\nCada reserva indisponible debe figurar identificada en la nota de fondos "
          "propios de la memoria, con su restriccion y su plazo. Es un desglose que se "
          "omite con frecuencia.")
    _papel(args, "G-2", "Reservas indisponibles y restringidas", res,
           {"Reservas": (detalle, ["saldo"])}, reg,
           alcance="Identificacion de las reservas indisponibles y restringidas del "
                   "patrimonio neto, verificacion de la dotacion minima de la reserva "
                   "legal y comprobacion de su desglose en memoria.",
           fundamento="arts. 274 y 273.4 LSC; arts. 25 y 105 LIS.")
    _registra(args, "area-fondos-propios-y-reservas", "G-2",
              "Reservas indisponibles y restringidas", res,
              [args.sumas_y_saldos], [getattr(args, "papel", "")],
              {"total_indisponible": total_indisp, "capital_social": capital})
    return 0


def cmd_doctor(args) -> int:
    """Comprobacion previa de la instalacion y de la configuracion.

    Se ejecuta antes del primer encargo, y cuando algo no funciona. Distingue lo
    que impide trabajar de lo que solo degrada el resultado.
    """
    # .../<plugin>/shared/scripts/dula/cli.py -> cuatro niveles hasta la raiz.
    # El lanzador `dula` la exporta en DULA_RAIZ; al invocar `python -m dula.cli`
    # directamente hay que deducirla, y equivocarse aqui hace que doctor declare
    # ausentes ficheros que si estan.
    raiz = os.environ.get("DULA_RAIZ") or os.path.abspath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
    bloqueantes: list[str] = []
    avisos: list[str] = []
    print("dula-audit - comprobacion de la instalacion")
    print("=" * 70)
    print(f"Raiz del plugin: {raiz}")
    print(f"Version de la libreria: {VERSION}")
    print(f"Python: {sys.version.split()[0]}")

    if sys.version_info < (3, 10):
        bloqueantes.append(f"Python {sys.version.split()[0]} es anterior a 3.10.")

    for mod in ("pandas", "openpyxl"):
        try:
            m = __import__(mod)
            print(f"  {mod}: {getattr(m, '__version__', 'instalado')}")
        except ImportError:
            bloqueantes.append(f"Falta la dependencia '{mod}'. "
                               f"Instalela con: pip install {mod}")

    from . import rutas
    print("\nFicheros de referencia")
    try:
        dir_ref = rutas.directorio("referencias")
        dir_tpl = rutas.directorio("plantillas")
        print(f"  referencias: {dir_ref}")
        print(f"  plantillas:  {dir_tpl}")
    except FileNotFoundError as exc:
        bloqueantes.append(str(exc).split("\n")[0])
        dir_ref = dir_tpl = None
    for base, nombre, critico in ((dir_ref, "mapeo-pgc.json", True),
                                  (dir_ref, "desgloses-memoria.json", True),
                                  (dir_ref, "catalogo-riesgos.md", False),
                                  (dir_tpl, "informe-auditoria.md", True),
                                  (dir_ref, "tarifas.json", False),
                                  (dir_ref, "historico-encargos.json", False)):
        ruta = os.path.join(base, nombre) if base else ""
        existe = bool(ruta) and os.path.exists(ruta)
        print(f"  [{'OK' if existe else '--'}] {nombre}")
        if not existe and critico:
            bloqueantes.append(f"Falta el fichero de referencia {nombre}.")

    # el mapeo y la checklist deben cargarse de verdad, no solo existir
    try:
        from . import plan_contable
        c = plan_contable.clasifica("4300000001")
        if c["estado"] != "OK":
            bloqueantes.append("El mapeo PGC no resuelve una cuenta de clientes.")
        else:
            print(f"  Mapeo PGC operativo (430 -> {c['epigrafe']} {c['titulo']}).")
    except Exception as exc:  # noqa: BLE001
        bloqueantes.append(f"El mapeo PGC no se puede cargar: {exc}")
    try:
        r = comparador.checklist_memoria("", "PYME")
        print(f"  Checklist de memoria operativa "
              f"({r.datos['notas_aplicables']} notas para el modelo PYME).")
    except Exception as exc:  # noqa: BLE001
        bloqueantes.append(f"La checklist de desgloses no se puede cargar: {exc}")

    print("\nConfiguracion del despacho")
    conf = next((c for c in (os.path.join(raiz, "skills", "convenciones-dula", "SKILL.md"),
                             os.path.join(raiz, "procedimientos", "convenciones-dula.md"))
                 if os.path.exists(c)), "")
    if not conf:
        avisos.append("No se localiza el fichero de convenciones del despacho.")
    else:
        texto = open(conf, encoding="utf-8").read()
        pendientes = texto.count("«")
        if pendientes:
            avisos.append(
                f"{pendientes} campos sin completar en skills/convenciones-dula/SKILL.md "
                "(numeros de ROAC, ruta base, festivos locales). El plugin funciona, pero "
                "los dejara como [PENDIENTE-CLIENTE] en los documentos.")
        else:
            print("  Configuracion completada.")
    if not (dir_ref and os.path.exists(os.path.join(dir_ref, "tarifas.json"))):
        avisos.append("No hay tarifas.json: `estimacion-encargo` calculara horas pero "
                      "devolvera los honorarios como [PENDIENTE-CLIENTE]. Copie "
                      "shared/references/tarifas.json.ejemplo y ponga las suyas.")
    hist = os.path.join(dir_ref, "historico-encargos.json") if dir_ref else ""
    if hist and os.path.exists(hist):
        try:
            if not json.load(open(hist, encoding="utf-8")).get("encargos"):
                avisos.append("El estimador no esta calibrado con encargos reales del "
                              "despacho: trate el rango de horas como orientativo.")
        except Exception:  # noqa: BLE001
            avisos.append("historico-encargos.json no es JSON valido.")

    plantilla = os.path.join(dir_tpl, "informe-auditoria.md") if dir_tpl else ""
    if plantilla and os.path.exists(plantilla):
        n = open(plantilla, encoding="utf-8").read().count("[VERIFICAR-LITERAL-ICAC]")
        if n:
            avisos.append(
                f"{n} parrafos del modelo de informe marcados [VERIFICAR-LITERAL-ICAC]: "
                "contrastelos una vez contra el PDF oficial de la NIA-ES 700R del ICAC "
                "antes del primer uso real, y borre la marca.")

    print("\n" + "=" * 70)
    for b in bloqueantes:
        print(f"  BLOQUEANTE  {b}")
    for a in avisos:
        print(f"  AVISO       {a}")
    if not bloqueantes and not avisos:
        print("  Todo correcto. El plugin esta listo para trabajar.")
    elif not bloqueantes:
        print(f"\n  El plugin es operativo. {len(avisos)} avisos de configuracion.")
    else:
        print(f"\n  {len(bloqueantes)} problemas impiden ejecutar los calculos.")
    return 1 if bloqueantes else 0


def cmd_estado(args) -> int:
    enc = Encargo.abrir(args.encargo)
    b = bitacora.Bitacora(enc.carpeta)
    print(estado.panel(enc.datos, b.resumen() if b.entradas() else None))
    return 0


def cmd_validar(args) -> int:
    """Valida una entrada de la bitacora de uso de IA (NIGC1-ES)."""
    carpeta = args.encargo
    if os.path.isfile(carpeta):
        carpeta = os.path.dirname(os.path.abspath(carpeta))
    b = bitacora.Bitacora(carpeta)
    if args.listar or not args.entrada:
        print(b.informe())
        return 0
    if not b.valida(args.entrada, args.quien):
        print(f"ERROR: no existe la entrada {args.entrada} en uso-ia.log", file=sys.stderr)
        return 1
    print(f"Entrada {args.entrada} validada por {args.quien}.")
    return 0


def cmd_horas(args) -> int:
    enc = Encargo.abrir(args.encargo)
    if args.papel_ref and args.imputar:
        total = enc.imputa_horas(args.papel_ref, args.imputar, args.quien)
        enc.guardar()
        print(f"Papel {args.papel_ref}: {total} h acumuladas.")
    est = estado.horas_estimadas(enc.datos)
    cons = enc.horas_consumidas
    print(f"\nHoras consumidas: {cons} h" + (f" | estimadas: {est} h | "
          f"desviacion {cons - est:+.1f} h ({(cons - est) / est:+.0%})" if est else ""))
    filas = [{"Papel": p["ref"], "Titulo": p["titulo"], "Horas": p.get("horas", 0.0),
              "Estado": p.get("estado", "")} for p in enc.datos.get("papeles", [])]
    for f in sorted(filas, key=lambda x: -float(x["Horas"] or 0)):
        print(f"  {f['Papel']:<6} {f['Titulo'][:45]:<47} {float(f['Horas'] or 0):>6.1f} h  "
              f"{f['Estado']}")
    return 0


def cmd_pbc(args) -> int:
    """Gestiona los pendientes del cliente."""
    enc = Encargo.abrir(args.encargo)
    if args.añadir:
        p = enc.añade_pendiente(args.area or "?", args.añadir, args.prioridad,
                                args.responsable or "", args.comprometido or "")
        enc.guardar()
        print(f"Pendiente {p['id']} registrado (prioridad {p['prioridad']}).")
    if args.recibido:
        if enc.recibe_pendiente(args.recibido):
            enc.guardar(); print(f"Pendiente {args.recibido} marcado como recibido.")
        else:
            print(f"ERROR: no existe {args.recibido}", file=sys.stderr); return 1
    if args.recordar:
        if enc.recuerda_pendiente(args.recordar):
            enc.guardar(); print(f"Recordatorio anotado en {args.recordar}.")
        else:
            print(f"ERROR: no existe {args.recordar}", file=sys.stderr); return 1
    pend = estado.pendientes_ordenados(enc.datos)
    print(f"\nPENDIENTES DEL CLIENTE ({len(pend)}, ruta critica primero)")
    for p in pend:
        print(f"  {p['id']} [P{p['prioridad']}] {p.get('area', '?'):<4} "
              f"{p['descripcion'][:60]:<62} {p['estado']}"
              + (f" ({p['recordatorios']} recordatorios)" if p.get("recordatorios") else ""))
    if not pend:
        print("  Ninguno pendiente.")
    return 0


def cmd_calidad(args) -> int:
    enc = Encargo.abrir(args.encargo)
    res = calidad.revisa(enc.datos, pre_vuelo=args.pre_vuelo, carpeta=enc.carpeta)
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

    b = bitacora.Bitacora(enc.carpeta)
    sin_validar = b.sin_validar
    if sin_validar:
        print(f"\nBITACORA: {len(sin_validar)} ejecuciones asistidas SIN VALIDAR "
              f"({', '.join(e['id'] for e in sin_validar[:8])}"
              f"{'...' if len(sin_validar) > 8 else ''}).")
        print("  Toda ejecucion cuyo resultado se haya incorporado a un papel concluido "
              "debe estar validada (NIGC1-ES).")
    if not args.pre_vuelo:
        informe_ia = os.path.join(enc.carpeta, "02-documentos",
                                  "Registro de asistencia automatizada.txt")
        os.makedirs(os.path.dirname(informe_ia), exist_ok=True)
        with open(informe_ia, "w", encoding="utf-8") as fh:
            fh.write(b.informe())
        print(f"Registro de asistencia automatizada: {informe_ia}")
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
        sp.add_argument("--horas", type=float,
                        help="horas dedicadas, para el seguimiento del presupuesto")
        sp.add_argument("--riesgos", nargs="*",
                        help="ids de los riesgos que responde este papel (p.ej. R001 R002)")

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
    s.add_argument("--diario", help="para reconstruir la PyG si el balance esta regularizado")
    s.add_argument("--anterior-ccaa", help="cuentas anuales del ejercicio anterior")
    s.add_argument("--depositadas", help="cuentas depositadas en el Registro Mercantil")
    s.add_argument("--informe-gestion", help="cifras del informe de gestion (JSON)")
    s.add_argument("--soporte", help="documentacion soporte (facturas, contratos...)")
    s.add_argument("--contabilidad", help="registro contable a casar con el soporte")
    s.add_argument("--clave", default="documento", help="columna de casacion")
    s.add_argument("--columna-importe", default="importe")
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
    s.add_argument("--horas", type=float)
    s.set_defaults(fn=cmd_calidad)

    s = sub.add_parser("reservas", help="reservas indisponibles y restringidas")
    s.add_argument("sumas_y_saldos"); s.add_argument("--hoja", default=0)
    comunes(s); s.set_defaults(fn=cmd_reservas)

    s = sub.add_parser("doctor", help="comprueba la instalacion y la configuracion")
    s.set_defaults(fn=cmd_doctor)

    s = sub.add_parser("estado", help="donde esta el encargo y cual es el siguiente paso")
    s.add_argument("encargo")
    s.set_defaults(fn=cmd_estado)

    s = sub.add_parser("validar", help="valida una ejecucion de la bitacora de uso de IA")
    s.add_argument("encargo")
    s.add_argument("--entrada", help="id de la entrada (p.ej. IA-0003)")
    s.add_argument("--quien", default="", help="nombre de quien valida el resultado")
    s.add_argument("--listar", action="store_true", help="muestra el registro completo")
    s.set_defaults(fn=cmd_validar)

    s = sub.add_parser("horas", help="imputa y consulta horas por papel de trabajo")
    s.add_argument("encargo")
    s.add_argument("--papel-ref", help="referencia del papel (p.ej. F-1)")
    s.add_argument("--imputar", type=float, help="horas a imputar")
    s.add_argument("--quien", default="")
    s.set_defaults(fn=cmd_horas)

    s = sub.add_parser("pbc", help="gestiona los pendientes de documentacion del cliente")
    s.add_argument("encargo")
    s.add_argument("--anadir", "--añadir", dest="añadir", help="descripcion del pendiente")
    s.add_argument("--area", help="area del indice (p.ej. F)")
    s.add_argument("--prioridad", type=int, default=3, choices=[1, 2, 3, 4],
                   help="1 bloqueante, 2 calendario, 3 alto impacto, 4 resto")
    s.add_argument("--responsable"); s.add_argument("--comprometido")
    s.add_argument("--recibido", help="id del pendiente recibido")
    s.add_argument("--recordar", help="id del pendiente a recordar")
    s.set_defaults(fn=cmd_pbc)

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
