"""Perfil de complejidad, estimacion de horas y honorarios, y motor de escalado.

Los drivers y sus pesos proceden de la experiencia declarada del despacho:
encargos de 2 dias a 2 meses, con la automatizacion de la facturacion, los
instrumentos de financiacion, los leasings y la capacidad de respuesta del
cliente como factores que mas mueven la aguja.

Las tarifas por categoria se configuran en CLAUDE.md. Sin tarifas propias, el
modulo estima horas y deja los honorarios como [PENDIENTE-CLIENTE]: no inventa
un precio.
"""

from __future__ import annotations

from typing import Any

# ---------------------------------------------------------------------------
# Drivers de complejidad
# ---------------------------------------------------------------------------
DRIVERS: dict[str, dict[str, Any]] = {
    "n_asientos": {
        "etiqueta": "Volumen de asientos",
        "tramos": [(2000, 0), (10000, 5), (50000, 10), (float("inf"), 15)],
        "tipo": "tramo",
    },
    "n_cuentas": {
        "etiqueta": "Numero de cuentas activas",
        "tramos": [(150, 0), (400, 3), (1000, 6), (float("inf"), 8)],
        "tipo": "tramo",
    },
    "automatizacion_facturacion": {
        "etiqueta": "Automatizacion de la facturacion",
        "opciones": {"alta": 0, "media": 4, "manual": 8},
        "tipo": "opcion",
    },
    "n_instrumentos_financiacion": {
        "etiqueta": "Creditos, polizas, avales, confirming y factoring",
        "tramos": [(0, 0), (4, 4), (10, 9), (float("inf"), 15)],
        "tipo": "tramo",
    },
    "n_leasings": {
        "etiqueta": "Contratos de arrendamiento financiero",
        "tramos": [(0, 0), (5, 3), (25, 8), (float("inf"), 15)],
        "tipo": "tramo",
    },
    "existencias": {
        "etiqueta": "Existencias",
        "opciones": {"no": 0, "si": 6, "valoracion_compleja": 10},
        "tipo": "opcion",
    },
    "subvenciones": {
        "etiqueta": "Subvenciones",
        "opciones": {"no": 0, "si": 5, "multiples_con_condiciones": 8},
        "tipo": "opcion",
    },
    "operaciones_vinculadas": {
        "etiqueta": "Operaciones con partes vinculadas",
        "opciones": {"no": 0, "si": 5, "significativas": 10},
        "tipo": "opcion",
    },
    "moneda_extranjera": {
        "etiqueta": "Moneda extranjera",
        "opciones": {"no": 0, "si": 5},
        "tipo": "opcion",
    },
    "consolidacion": {
        "etiqueta": "Consolidacion",
        "opciones": {"no": 0, "si": 12},
        "tipo": "opcion",
    },
    "primer_encargo": {
        "etiqueta": "Primer encargo (saldos de apertura)",
        "opciones": {"no": 0, "si": 8},
        "tipo": "opcion",
    },
    "respuesta_cliente": {
        "etiqueta": "Historial de respuesta del cliente",
        "opciones": {"agil": 0, "normal": 4, "lento_o_desordenado": 8},
        "tipo": "opcion",
    },
}

LIMITES = {"LIGERO": 20, "ESTANDAR": 50}


def puntua(drivers: dict[str, Any]) -> tuple[int, list[dict[str, Any]]]:
    """Puntua los drivers. Devuelve (puntuacion, detalle)."""
    total = 0
    detalle: list[dict[str, Any]] = []
    for clave, cfg in DRIVERS.items():
        valor = drivers.get(clave)
        if valor is None:
            detalle.append({"driver": cfg["etiqueta"], "valor": "[PENDIENTE-CLIENTE]",
                            "puntos": 0, "nota": "No informado; no puntua."})
            continue
        if cfg["tipo"] == "tramo":
            v = float(valor)
            puntos = next(p for limite, p in cfg["tramos"] if v <= limite)
        else:
            v = str(valor).lower()
            if v not in cfg["opciones"]:
                detalle.append({"driver": cfg["etiqueta"], "valor": valor, "puntos": 0,
                                "nota": f"Valor no reconocido. Use {list(cfg['opciones'])}."})
                continue
            puntos = cfg["opciones"][v]
        total += puntos
        detalle.append({"driver": cfg["etiqueta"], "valor": valor, "puntos": puntos,
                        "nota": ""})
    return total, detalle


def clasifica_perfil(puntuacion: int, eip: bool = False,
                     consolidacion: bool = False) -> tuple[str, str]:
    """Perfil operativo con overrides duros."""
    if eip:
        return "COMPLEJO", (
            "Perfil COMPLEJO por override: se trata de una entidad de interes publico. "
            "Con independencia de la puntuacion obtenida, son de aplicacion el Reglamento "
            "(UE) 537/2014 y los requerimientos reforzados de rotacion, informe adicional "
            "a la comision de auditoria, cuestiones clave de la auditoria y revision de "
            "calidad del encargo."
        )
    if puntuacion <= LIMITES["LIGERO"]:
        base = "LIGERO"
    elif puntuacion <= LIMITES["ESTANDAR"]:
        base = "ESTANDAR"
    else:
        base = "COMPLEJO"
    if consolidacion and base == "LIGERO":
        return "ESTANDAR", (
            f"Perfil elevado de LIGERO a ESTANDAR (puntuacion {puntuacion}) por existir "
            "consolidacion: la NIA-ES 600 (Revisada) exige procedimientos sobre componentes "
            "que no caben en un programa de perfil ligero."
        )
    return base, (
        f"Perfil {base} con una puntuacion de complejidad de {puntuacion} sobre 100 "
        f"(LIGERO <= {LIMITES['LIGERO']}, ESTANDAR <= {LIMITES['ESTANDAR']}, "
        f"COMPLEJO > {LIMITES['ESTANDAR']})."
    )


# ---------------------------------------------------------------------------
# Estimacion de horas
# ---------------------------------------------------------------------------
# Horas base por area y perfil. Calibradas sobre encargos tipo del despacho;
# se ajustan con datos historicos propios (ver CLAUDE.md, seccion Calibracion).
HORAS_BASE = {
    "Aceptacion e independencia":   {"LIGERO": 1.0, "ESTANDAR": 2.0, "COMPLEJO": 4.0},
    "Planificacion y riesgos":      {"LIGERO": 3.0, "ESTANDAR": 8.0, "COMPLEJO": 20.0},
    "Ingesta y cuadres":            {"LIGERO": 1.5, "ESTANDAR": 3.0, "COMPLEJO": 6.0},
    "Inmovilizado":                 {"LIGERO": 1.5, "ESTANDAR": 5.0, "COMPLEJO": 14.0},
    "Existencias":                  {"LIGERO": 0.0, "ESTANDAR": 8.0, "COMPLEJO": 24.0},
    "Clientes e ingresos":          {"LIGERO": 2.5, "ESTANDAR": 10.0, "COMPLEJO": 30.0},
    "Proveedores y compras":        {"LIGERO": 2.0, "ESTANDAR": 7.0, "COMPLEJO": 20.0},
    "Tesoreria y financiacion":     {"LIGERO": 2.0, "ESTANDAR": 6.0, "COMPLEJO": 18.0},
    "Arrendamientos":               {"LIGERO": 0.5, "ESTANDAR": 3.0, "COMPLEJO": 10.0},
    "Fondos propios y reservas":    {"LIGERO": 1.0, "ESTANDAR": 2.5, "COMPLEJO": 6.0},
    "Personal":                     {"LIGERO": 1.0, "ESTANDAR": 4.0, "COMPLEJO": 12.0},
    "Fiscal":                       {"LIGERO": 2.0, "ESTANDAR": 6.0, "COMPLEJO": 16.0},
    "Provisiones y contingencias":  {"LIGERO": 0.5, "ESTANDAR": 3.0, "COMPLEJO": 10.0},
    "Subvenciones":                 {"LIGERO": 0.0, "ESTANDAR": 2.0, "COMPLEJO": 6.0},
    "Partes vinculadas":            {"LIGERO": 0.5, "ESTANDAR": 2.0, "COMPLEJO": 8.0},
    "Cierre e incorrecciones":      {"LIGERO": 1.5, "ESTANDAR": 4.0, "COMPLEJO": 10.0},
    "Informe":                      {"LIGERO": 1.5, "ESTANDAR": 3.0, "COMPLEJO": 8.0},
    "Revision de calidad":          {"LIGERO": 1.0, "ESTANDAR": 3.0, "COMPLEJO": 12.0},
}

# Multiplicadores por driver especifico sobre el area que afecta.
MULTIPLICADORES = {
    "Arrendamientos": ("n_leasings", lambda n: 1 + min(float(n or 0) / 25.0, 4.0)),
    "Tesoreria y financiacion": ("n_instrumentos_financiacion",
                                 lambda n: 1 + min(float(n or 0) / 10.0, 3.0)),
    "Existencias": ("existencias", lambda v: {"no": 0.0, "si": 1.0,
                                              "valoracion_compleja": 1.8}.get(str(v).lower(), 1.0)),
    "Subvenciones": ("subvenciones", lambda v: {"no": 0.0, "si": 1.0,
                                                "multiples_con_condiciones": 2.0}.get(str(v).lower(), 1.0)),
    "Clientes e ingresos": ("automatizacion_facturacion",
                            lambda v: {"alta": 0.8, "media": 1.0, "manual": 1.6}.get(str(v).lower(), 1.0)),
}

# Reparto por categoria profesional (suma 1 por area).
REPARTO = {
    "Aceptacion e independencia": {"socio": 0.7, "gerente": 0.3, "senior": 0.0, "ayudante": 0.0},
    "Planificacion y riesgos":    {"socio": 0.4, "gerente": 0.4, "senior": 0.2, "ayudante": 0.0},
    "Informe":                    {"socio": 0.6, "gerente": 0.3, "senior": 0.1, "ayudante": 0.0},
    "Revision de calidad":        {"socio": 0.8, "gerente": 0.2, "senior": 0.0, "ayudante": 0.0},
    "Cierre e incorrecciones":    {"socio": 0.3, "gerente": 0.4, "senior": 0.3, "ayudante": 0.0},
    "_defecto":                   {"socio": 0.05, "gerente": 0.15, "senior": 0.45, "ayudante": 0.35},
}

# Factor de correccion por capacidad de respuesta del cliente: se aplica a todo
# el trabajo de campo, porque es donde se pierde el tiempo esperando.
FACTOR_RESPUESTA = {"agil": 0.9, "normal": 1.0, "lento_o_desordenado": 1.35}

# Ahorro estimado por el uso del plugin, por area. Conservador: solo donde el
# calculo es determinista y el papel se genera solo.
AHORRO_PLUGIN = {
    "Ingesta y cuadres": 0.60, "Arrendamientos": 0.70, "Tesoreria y financiacion": 0.45,
    "Inmovilizado": 0.45, "Fiscal": 0.25, "Cierre e incorrecciones": 0.35,
    "Informe": 0.30, "Revision de calidad": 0.40, "Fondos propios y reservas": 0.35,
}


def estima(drivers: dict[str, Any], perfil: str, tarifas: dict[str, float] | None = None,
           con_plugin: bool = True) -> dict[str, Any]:
    """Horas y honorarios por area y categoria, con rango optimista/esperado/pesimista."""
    perfil = perfil.upper()
    factor_resp = FACTOR_RESPUESTA.get(
        str(drivers.get("respuesta_cliente", "normal")).lower(), 1.0)

    areas: list[dict[str, Any]] = []
    for area, base in HORAS_BASE.items():
        horas = base[perfil]
        if area in MULTIPLICADORES:
            clave, fn = MULTIPLICADORES[area]
            horas *= fn(drivers.get(clave))
        if area not in {"Aceptacion e independencia", "Planificacion y riesgos",
                        "Informe", "Revision de calidad"}:
            horas *= factor_resp
        if drivers.get("primer_encargo") == "si" and area not in {"Informe"}:
            horas *= 1.15  # saldos de apertura y ausencia de conocimiento previo
        horas_sin = round(horas, 1)
        ahorro = AHORRO_PLUGIN.get(area, 0.15) if con_plugin else 0.0
        horas_con = round(horas * (1 - ahorro), 1)
        if horas_sin <= 0:
            continue
        reparto = REPARTO.get(area, REPARTO["_defecto"])
        areas.append({
            "area": area,
            "horas_sin_plugin": horas_sin,
            "horas_estimadas": horas_con,
            "ahorro_aplicado": ahorro,
            **{f"h_{cat}": round(horas_con * pct, 1) for cat, pct in reparto.items()},
        })

    total = round(sum(a["horas_estimadas"] for a in areas), 1)
    total_sin = round(sum(a["horas_sin_plugin"] for a in areas), 1)
    por_categoria = {cat: round(sum(a[f"h_{cat}"] for a in areas), 1)
                     for cat in ("socio", "gerente", "senior", "ayudante")}

    rango = {"optimista": round(total * 0.80, 1), "esperado": total,
             "pesimista": round(total * 1.45, 1)}

    resultado: dict[str, Any] = {
        "perfil": perfil, "areas": areas,
        "horas_totales": total, "horas_sin_plugin": total_sin,
        "ahorro_horas": round(total_sin - total, 1),
        "por_categoria": por_categoria, "rango_horas": rango,
        "factor_respuesta_cliente": factor_resp,
    }

    if tarifas:
        faltan = [c for c in por_categoria if c not in tarifas]
        if faltan:
            resultado["honorarios"] = "[PENDIENTE-CLIENTE]"
            resultado["nota_honorarios"] = (
                f"Faltan tarifas para: {', '.join(faltan)}. No se estiman honorarios sin "
                "tarifa; configurelas en CLAUDE.md.")
        else:
            coste = {c: round(h * tarifas[c], 2) for c, h in por_categoria.items()}
            total_hon = round(sum(coste.values()), 2)
            resultado["honorarios"] = {
                "por_categoria": coste, "total": total_hon,
                "rango": {"optimista": round(total_hon * 0.80, 2),
                          "esperado": total_hon,
                          "pesimista": round(total_hon * 1.45, 2)},
                "tarifa_media": round(total_hon / total, 2) if total else None,
            }
            # punto muerto: honorarios que cubren el coste directo del equipo
            costes_hora = tarifas.get("_coste_hora", {})
            if costes_hora:
                coste_directo = round(sum(h * costes_hora.get(c, 0.0)
                                          for c, h in por_categoria.items()), 2)
                resultado["punto_muerto"] = {
                    "coste_directo_equipo": coste_directo,
                    "honorario_minimo": coste_directo,
                    "margen_esperado": round(total_hon - coste_directo, 2),
                    "margen_pct": round((total_hon - coste_directo) / total_hon, 4)
                    if total_hon else None,
                }
            else:
                resultado["punto_muerto"] = "[PENDIENTE-CLIENTE] - falta el coste/hora por categoria"
    else:
        resultado["honorarios"] = "[PENDIENTE-CLIENTE]"
        resultado["nota_honorarios"] = ("No se han configurado tarifas por categoria. "
                                        "Vease CLAUDE.md, seccion Tarifas.")
    return resultado


def factores_encarecedores(detalle: list[dict[str, Any]], top: int = 5
                           ) -> list[dict[str, Any]]:
    """Los drivers que mas encarecen el encargo, con la palanca para abaratarlo."""
    palancas = {
        "Contratos de arrendamiento financiero":
            "Solicitar al cliente los cuadros de amortizacion de la entidad financiera en "
            "Excel (no en PDF) y un listado unico de contratos. Reduce a la mitad el tiempo "
            "de extraccion.",
        "Creditos, polizas, avales, confirming y factoring":
            "Pedir el CIRBE y un cuadro unico con todos los instrumentos, limites, "
            "dispuesto y vencimientos antes del inicio del trabajo de campo.",
        "Automatizacion de la facturacion":
            "Obtener el listado de facturas emitidas en formato de datos desde el sistema "
            "de facturacion, no en PDF. Permite el analitico sobre el 100% de la poblacion.",
        "Historial de respuesta del cliente":
            "Fijar por escrito un unico interlocutor y un calendario de entregas con fechas "
            "comprometidas antes de aceptar el encargo.",
        "Volumen de asientos":
            "Solicitar el diario completo en formato de datos, con usuario y fecha de "
            "contabilizacion; evita el trabajo manual de muestreo.",
        "Existencias":
            "Planificar la asistencia al recuento con antelacion y obtener el fichero de "
            "valoracion con coste unitario por referencia.",
        "Operaciones con partes vinculadas":
            "Pedir a la direccion el listado completo de partes vinculadas y sus "
            "operaciones al inicio, no al cierre.",
        "Primer encargo (saldos de apertura)":
            "Autorizar la comunicacion con el auditor predecesor y solicitar acceso a sus "
            "papeles de trabajo.",
        "Consolidacion":
            "Obtener el paquete de consolidacion y los estados de las dependientes con la "
            "misma fecha de cierre y criterios homogeneos.",
        "Subvenciones":
            "Reunir las resoluciones de concesion y la justificacion presentada en un unico "
            "expediente por subvencion.",
    }
    ordenados = sorted([d for d in detalle if d["puntos"] > 0],
                       key=lambda d: -d["puntos"])[:top]
    return [{"factor": d["driver"], "puntos": d["puntos"], "valor": d["valor"],
             "palanca": palancas.get(d["driver"], "Anticipar la peticion de informacion.")}
            for d in ordenados]


# ---------------------------------------------------------------------------
# Motor de escalado
# ---------------------------------------------------------------------------
CONFIGURACION_PERFIL = {
    "LIGERO": {
        "mp_factor": 0.75,
        "enfoque": "Analitico sustantivo + examen del 100% de las partidas significativas",
        "muestreo": "dirigido",
        "circularizacion_clientes": "solo si el analitico no concluye",
        "circularizacion_proveedores": "solo si el analitico no concluye",
        "circularizacion_bancos": "siempre (todas las entidades)",
        "test_asientos_filtros": 4,
        "revision_calidad_encargo": False,
        "areas_activas": "solo areas con saldo superior a la materialidad de ejecucion",
        "extraccion_documental": "muestra dirigida",
    },
    "ESTANDAR": {
        "mp_factor": 0.65,
        "enfoque": "Mixto: analitico sustantivo + pruebas de detalle sobre muestra",
        "muestreo": "MUS en las 2-3 areas de mayor riesgo, dirigido en el resto",
        "circularizacion_clientes": "si, cobertura reducida",
        "circularizacion_proveedores": "si, sobre saldos significativos y proveedores clave",
        "circularizacion_bancos": "siempre (todas las entidades)",
        "test_asientos_filtros": 9,
        "revision_calidad_encargo": "segun politica de la firma",
        "areas_activas": "todas las areas con saldo superior al umbral de insignificancia",
        "extraccion_documental": "lote completo + muestra de verificacion documental",
    },
    "COMPLEJO": {
        "mp_factor": 0.55,
        "enfoque": "Pruebas de controles + sustantivas + muestreo estadistico",
        "muestreo": "MUS con estratificacion en todas las areas significativas",
        "circularizacion_clientes": "si, cobertura plena + procedimientos alternativos",
        "circularizacion_proveedores": "si, cobertura plena + busqueda de pasivos no registrados",
        "circularizacion_bancos": "siempre (todas las entidades)",
        "test_asientos_filtros": 9,
        "revision_calidad_encargo": True,
        "areas_activas": "todas las areas, mas las especificas del sector",
        "extraccion_documental": "lote completo + muestra ampliada",
    },
}


def configuracion(perfil: str) -> dict[str, Any]:
    return dict(CONFIGURACION_PERFIL[perfil.upper()])


def valida_simplificacion(perfil: str, hallazgos: dict[str, bool]) -> dict[str, Any]:
    """Comprueba si la simplificacion del perfil sigue siendo defendible.

    Si aparece un hallazgo que la invalida, ELEVA el perfil y avisa de que el
    trabajo ya ejecutado se ha quedado corto. La simplificacion nunca se mantiene
    cuando deja de ser justificable.
    """
    disparadores = {
        "indicio_fraude": "Se ha identificado un indicio de fraude",
        "incorreccion_material": "Se ha detectado una incorreccion material",
        "control_interno_deficiente": "Se han identificado deficiencias significativas de control interno",
        "duda_empresa_en_funcionamiento": "Existen dudas sobre la empresa en funcionamiento",
        "limitacion_alcance": "Se ha producido una limitacion al alcance",
        "covenant_incumplido": "Se ha detectado el incumplimiento de un covenant",
        "operacion_vinculada_no_declarada": "Se ha identificado una operacion vinculada no declarada",
    }
    activos = [texto for clave, texto in disparadores.items() if hallazgos.get(clave)]
    if not activos:
        return {"perfil_final": perfil.upper(), "elevado": False,
                "mensaje": f"La configuracion del perfil {perfil.upper()} sigue siendo "
                           "defendible: no ha concurrido ningun hallazgo que exija ampliar "
                           "el alcance."}
    orden = ["LIGERO", "ESTANDAR", "COMPLEJO"]
    nuevo = orden[min(orden.index(perfil.upper()) + 1, 2)]
    return {
        "perfil_final": nuevo, "elevado": True, "disparadores": activos,
        "mensaje": (
            f"PERFIL ELEVADO de {perfil.upper()} a {nuevo}. Motivo: "
            + "; ".join(activos) + ". "
            "Las pruebas ya ejecutadas se dimensionaron con la configuracion del perfil "
            "anterior y pueden haberse quedado cortas. Hay que: (1) recalcular la "
            "materialidad de ejecucion con el nuevo factor, (2) revisar si los tamanos de "
            "muestra siguen siendo suficientes, y (3) reevaluar la valoracion del riesgo de "
            "las areas ya cerradas. La simplificacion aplicada ha dejado de ser defendible."
        ),
    }
