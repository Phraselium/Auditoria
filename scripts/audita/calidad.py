"""Revision de calidad del archivo. El segundo par de ojos.

Modo PRE-VUELO: ejecutable en cualquier momento del encargo, no solo antes de la
firma. Si el socio solo ve las excepciones el ultimo dia, el problema no se ha
resuelto, se ha concentrado.

Salida en dos capas:
  (a) PANEL DEL SOCIO: las cuestiones que exigen su juicio, en una pagina.
  (b) LISTADO COMPLETO de excepciones por severidad.

Este modulo NO sustituye la revision del socio firmante, que es indelegable bajo
la NIA-ES 220 (Revisada) y el sistema de gestion de la calidad. La hace viable
en minutos, entregandole cuadrado y evidenciado todo lo demas.
"""

from __future__ import annotations

from typing import Any

from .excepciones import (BLOQUEANTE, DOCUMENTAR, INFORMATIVA, RESOLVER,
                          ORDEN_SEVERIDAD, Excepcion, Resultado)


def _exc(codigo: str, sev: str, area: str, desc: str, accion: str,
         norma: str = "", importe: float | None = None) -> Excepcion:
    return Excepcion(codigo, sev, area, desc, importe=importe, origen="encargo.json",
                     accion=accion, referencia_normativa=norma)


# ---------------------------------------------------------------------------
# Comprobaciones individuales
# ---------------------------------------------------------------------------
def riesgos_sin_respuesta(datos: dict[str, Any]) -> list[Excepcion]:
    """Todo riesgo identificado debe tener una respuesta ejecutada y concluida."""
    out: list[Excepcion] = []
    papeles = {p["ref"]: p for p in datos.get("papeles", [])}
    for r in datos.get("riesgos", []):
        if not r.get("respuestas"):
            sev = BLOQUEANTE if r.get("significativo") or r.get("fraude") else RESOLVER
            out.append(_exc(
                "CAL-001", sev, r.get("area", "?"),
                f"Riesgo {r['id']} ({r['descripcion']}) sin ningun procedimiento que lo "
                f"responda.",
                "Disenar y ejecutar el procedimiento que responde al riesgo, o eliminar el "
                "riesgo del mapa si no procede.",
                "NIA-ES 330.6"))
            continue
        sin_concluir = [ref for ref in r["respuestas"]
                        if papeles.get(ref, {}).get("estado") != "concluido"]
        if sin_concluir:
            out.append(_exc(
                "CAL-002", RESOLVER, r.get("area", "?"),
                f"Riesgo {r['id']}: sus respuestas {', '.join(sin_concluir)} no estan "
                "concluidas.",
                "Concluir los papeles pendientes antes de cerrar el area.",
                "NIA-ES 330.28"))
    return out


def papeles_sin_conclusion(datos: dict[str, Any]) -> list[Excepcion]:
    """Un papel sin conclusion no es evidencia: es un listado."""
    out: list[Excepcion] = []
    for p in datos.get("papeles", []):
        if not str(p.get("conclusion", "")).strip():
            out.append(_exc(
                "CAL-010", RESOLVER, p.get("ref", "?"),
                f"Papel {p['ref']} ({p['titulo']}) sin conclusion redactada.",
                "Redactar la conclusion: que se ha probado, con que alcance y a que "
                "resultado se llega respecto de las afirmaciones cubiertas.",
                "NIA-ES 230.8"))
        elif p.get("estado") == "concluido" and len(str(p["conclusion"]).split()) < 8:
            out.append(_exc(
                "CAL-011", DOCUMENTAR, p.get("ref", "?"),
                f"Papel {p['ref']} ({p['titulo']}): conclusion demasiado escueta "
                f"(\"{p['conclusion']}\").",
                "Ampliar la conclusion para que un tercero competente pueda reconstruir el "
                "razonamiento sin explicaciones adicionales.",
                "NIA-ES 230.8"))
        if not p.get("riesgos"):
            out.append(_exc(
                "CAL-012", DOCUMENTAR, p.get("ref", "?"),
                f"Papel {p['ref']} ({p['titulo']}) no esta vinculado a ningun riesgo.",
                "Vincularlo al riesgo que responde, o justificar por que se ejecuta un "
                "procedimiento que no responde a ningun riesgo identificado."))
    return out


def materialidad_vigente(datos: dict[str, Any]) -> list[Excepcion]:
    out: list[Excepcion] = []
    mats = datos.get("materialidad", [])
    if not mats:
        out.append(_exc(
            "CAL-020", BLOQUEANTE, "1.4",
            "No consta materialidad determinada para el encargo.",
            "Determinar la materialidad global, la de ejecucion y el umbral de "
            "incorrecciones claramente insignificantes.",
            "NIA-ES 320"))
        return out
    vigente = mats[-1]
    if not str(vigente.get("fundamento", "")).strip():
        out.append(_exc(
            "CAL-021", RESOLVER, "1.4",
            "La materialidad no documenta el fundamento de la magnitud ni del porcentaje "
            "elegidos.",
            "Documentar por que se ha elegido esa magnitud de referencia y ese porcentaje.",
            "NIA-ES 320.14"))
    if len(mats) > 1 and not vigente.get("recalculo_evaluado"):
        out.append(_exc(
            "CAL-022", RESOLVER, "1.4",
            f"La materialidad se ha revisado {len(mats)} veces y no consta la evaluacion "
            "del efecto del cambio sobre el alcance ya ejecutado.",
            "Ejecutar materialidad.evalua_recalculo() y documentar si procede ampliar "
            "pruebas ya realizadas.",
            "NIA-ES 320.12-13"))
    return out


def cuadres_pendientes(datos: dict[str, Any]) -> list[Excepcion]:
    out: list[Excepcion] = []
    bloqueantes = [e for e in datos.get("excepciones", [])
                   if e.get("severidad") == BLOQUEANTE]
    for e in bloqueantes:
        out.append(_exc(
            "CAL-030", BLOQUEANTE, e.get("area", "?"),
            f"Excepcion bloqueante sin resolver: [{e.get('codigo')}] {e.get('descripcion')}",
            e.get("accion", "Resolver antes de la firma."),
            e.get("referencia_normativa", ""),
            e.get("importe")))
    return out


def incorrecciones_evaluadas(datos: dict[str, Any]) -> list[Excepcion]:
    """Las incorrecciones no corregidas deben estar evaluadas cuantitativa Y
    cualitativamente, y comunicadas a la direccion."""
    out: list[Excepcion] = []
    incs = datos.get("incorrecciones", [])
    no_corregidas = [i for i in incs if not i.get("corregida")]
    if not incs:
        return out
    mat = datos.get("materialidad", [])
    mg = float(mat[-1].get("global", 0.0)) if mat else 0.0

    efecto = round(sum(float(i.get("efecto_resultado", 0.0)) for i in no_corregidas), 2)
    if mg and abs(efecto) > mg:
        out.append(_exc(
            "CAL-040", BLOQUEANTE, "8.1",
            f"El efecto agregado de las incorrecciones no corregidas ({efecto:,.2f} EUR) "
            f"supera la materialidad global ({mg:,.2f} EUR).",
            "La opinion no puede ser favorable. Solicitar la correccion o emitir opinion "
            "con salvedades / desfavorable segun la generalizacion del efecto.",
            "NIA-ES 450.11; NIA-ES 705 (Revisada)", efecto))
    for i in no_corregidas:
        if not str(i.get("cualitativa", "")).strip():
            out.append(_exc(
                "CAL-041", RESOLVER, i.get("area", "8.1"),
                f"Incorreccion {i['id']} ({i['descripcion']}) no corregida y sin evaluacion "
                "cualitativa.",
                "Evaluar si, con independencia de su importe, es cualitativamente "
                "significativa (afecta a covenants, a la clasificacion de partidas, a "
                "retribuciones de la direccion o revela un sesgo de la direccion).",
                "NIA-ES 450.A16-A23"))
    return out


def fases_incompletas(datos: dict[str, Any]) -> list[Excepcion]:
    out: list[Excepcion] = []
    orden = ["aceptacion", "planificacion", "campo", "cierre"]
    fases = datos.get("fases", {})
    ultima_completa = -1
    for i, f in enumerate(orden):
        if fases.get(f) == "completa":
            ultima_completa = i
    for i, f in enumerate(orden):
        if i < ultima_completa and fases.get(f) != "completa":
            out.append(_exc(
                "CAL-050", RESOLVER, "9.2",
                f"La fase '{f}' no consta completa pero hay fases posteriores cerradas.",
                f"Cerrar formalmente la fase '{f}' o documentar por que se ha avanzado."))
    return out


def informe_coherente(datos: dict[str, Any]) -> list[Excepcion]:
    """El informe debe ser coherente con el archivo."""
    out: list[Excepcion] = []
    inf = datos.get("informe", {})
    if not inf:
        return out
    opinion = str(inf.get("tipo_opinion", "")).lower()
    incs = [i for i in datos.get("incorrecciones", []) if not i.get("corregida")]
    mat = datos.get("materialidad", [])
    mg = float(mat[-1].get("global", 0.0)) if mat else 0.0
    efecto = round(sum(float(i.get("efecto_resultado", 0.0)) for i in incs), 2)

    if opinion.startswith("favorable") and mg and abs(efecto) > mg:
        out.append(_exc(
            "CAL-060", BLOQUEANTE, "9.1",
            f"El informe propone opinion favorable pero las incorrecciones no corregidas "
            f"({efecto:,.2f} EUR) superan la materialidad global ({mg:,.2f} EUR).",
            "Revisar el tipo de opinion. No firmar hasta resolver la incoherencia.",
            "NIA-ES 700 (Revisada); NIA-ES 705 (Revisada)", efecto))

    if inf.get("incertidumbre_empresa_en_funcionamiento") and \
            not inf.get("parrafo_empresa_en_funcionamiento"):
        out.append(_exc(
            "CAL-061", BLOQUEANTE, "9.1",
            "Se ha concluido que existe una incertidumbre material relativa a la empresa en "
            "funcionamiento y el informe no incluye la seccion correspondiente.",
            "Incluir la seccion 'Incertidumbre material relacionada con la empresa en "
            "funcionamiento'.",
            "NIA-ES 570 (Revisada).22"))

    if not inf.get("seccion_impuesto_sociedades"):
        out.append(_exc(
            "CAL-062", RESOLVER, "9.1",
            "El informe no incluye el apartado relativo al informe sobre el impuesto sobre "
            "sociedades o impuestos de naturaleza identica o analoga, exigible desde la "
            "Resolucion del ICAC de 22 de enero de 2026.",
            "Incluir el apartado dentro de la seccion 'Informe sobre otros requerimientos "
            "legales y reglamentarios'. En la practica totalidad de los encargos del "
            "despacho sera la redaccion de entidad NO obligada (umbral de 750 M EUR de "
            "cifra de negocios consolidada).",
            "DA 11ª LAC; RICAC 22/01/2026"))

    if inf.get("salvedades") and not inf.get("efecto_cuantificado") and \
            not inf.get("motivo_no_cuantificacion"):
        out.append(_exc(
            "CAL-063", RESOLVER, "9.1",
            "El informe incluye salvedades sin cuantificar el efecto ni explicar por que no "
            "es posible cuantificarlo.",
            "Cuantificar el efecto de la salvedad o explicar la imposibilidad de hacerlo.",
            "NIA-ES 705 (Revisada).18-20"))
    return out


def documentacion_reconstruible(datos: dict[str, Any]) -> list[Excepcion]:
    """Un tercero competente debe poder reconstruir el trabajo (NIA-ES 230.8)."""
    out: list[Excepcion] = []
    if not datos.get("fuentes"):
        out.append(_exc(
            "CAL-070", RESOLVER, "9.2",
            "No consta registro de los ficheros fuente recibidos del cliente ni sus huellas.",
            "Registrar los ficheros fuente con su SHA-256 para acreditar sobre que version "
            "de la informacion se ha trabajado.",
            "NIA-ES 230"))
    sin_fichero = [p["ref"] for p in datos.get("papeles", [])
                   if p.get("estado") == "concluido" and not p.get("fichero")]
    if sin_fichero:
        out.append(_exc(
            "CAL-071", RESOLVER, "9.2",
            f"Papeles concluidos sin fichero asociado en el archivo: "
            f"{', '.join(sin_fichero[:10])}.",
            "Adjuntar el papel de trabajo al archivo del encargo."))
    return out


def sistema_gestion_calidad(datos: dict[str, Any]) -> list[Excepcion]:
    """Elementos que exige el sistema de gestion de la calidad del despacho."""
    out: list[Excepcion] = []
    perfil = (datos.get("perfil") or {}).get("perfil", "")
    eip = (datos.get("cliente") or {}).get("eip", False)
    inf = datos.get("informe", {})

    if (eip or perfil == "COMPLEJO") and not inf.get("revision_calidad_encargo"):
        out.append(_exc(
            "CAL-080", BLOQUEANTE if eip else RESOLVER, "9.2",
            "El encargo requiere revision de calidad del encargo por un revisor "
            "independiente y no consta realizada.",
            "Designar al revisor de calidad del encargo y completar la revision ANTES de "
            "la fecha del informe.",
            "NIGC2-ES; NIA-ES 220 (Revisada).36"))
    if not datos.get("fases", {}).get("aceptacion") == "completa":
        out.append(_exc(
            "CAL-081", RESOLVER, "0.1",
            "La fase de aceptacion y evaluacion de independencia no consta completa.",
            "Completar y firmar la declaracion de independencia y la evaluacion de "
            "amenazas y salvaguardas.",
            "LAC arts. 14-20; NIA-ES 220 (Revisada).16-21"))
    if not (datos.get("cliente") or {}).get("nif"):
        out.append(_exc(
            "CAL-082", DOCUMENTAR, "0.1",
            "No consta el NIF de la entidad auditada en el estado del encargo.",
            "Completar los datos identificativos."))
    return out


def asistencia_automatizada(datos: dict[str, Any], carpeta: str | None) -> list[Excepcion]:
    """Ejecuciones asistidas por IA sin validar (NIGC1-ES; ISO/IEC 42001).

    Solo se exige la validacion de las ejecuciones cuyo resultado se ha
    incorporado a un papel de trabajo YA CONCLUIDO. Exigirla sobre trabajo en
    curso generaria ruido sin aportar control.
    """
    out: list[Excepcion] = []
    if not carpeta:
        return out
    from .bitacora import Bitacora
    b = Bitacora(carpeta)
    entradas = b.entradas()
    if not entradas:
        if datos.get("papeles"):
            out.append(_exc(
                "CAL-090", RESOLVER, "9.2",
                "Hay papeles de trabajo en el archivo y no consta ninguna ejecucion "
                "registrada en uso-ia.log.",
                "Verificar que las ejecuciones asistidas se estan registrando. El sistema "
                "de gestion de la calidad exige dejar constancia del uso de herramientas "
                "automatizadas.",
                "NIGC1-ES"))
        return out

    concluidos = {p["ref"] for p in datos.get("papeles", [])
                  if p.get("estado") == "concluido"}
    pendientes = [e for e in b.sin_validar if e.get("papel") in concluidos]
    for e in pendientes:
        out.append(_exc(
            "CAL-091", RESOLVER, e.get("papel") or "9.2",
            f"Ejecucion {e['id']} ({e['skill']}) sin validar, y su resultado se ha "
            f"incorporado al papel {e.get('papel')}, que consta concluido.",
            f"Validarla: `audita validar <encargo> --entrada {e['id']} --quien \"<nombre>\"`. "
            "La validacion acredita que un auditor ha revisado el resultado de la "
            "herramienta, no solo que la herramienta se ejecuto.",
            "NIGC1-ES; NIA-ES 220 (Revisada)"))
    sin_papel = [e for e in b.sin_validar if not e.get("papel")]
    if sin_papel:
        out.append(_exc(
            "CAL-092", DOCUMENTAR, "9.2",
            f"{len(sin_papel)} ejecuciones asistidas sin validar y sin papel de trabajo "
            "asociado (calculos exploratorios).",
            "Revisar si alguna deberia haber generado papel de trabajo."))
    return out


# ---------------------------------------------------------------------------
# Motor
# ---------------------------------------------------------------------------
COMPROBACIONES = (
    riesgos_sin_respuesta,
    papeles_sin_conclusion,
    materialidad_vigente,
    cuadres_pendientes,
    incorrecciones_evaluadas,
    fases_incompletas,
    informe_coherente,
    documentacion_reconstruible,
    sistema_gestion_calidad,
)


def revisa(datos: dict[str, Any], pre_vuelo: bool = False,
           carpeta: str | None = None) -> Resultado:
    """Revision completa del archivo.

    `pre_vuelo=True` degrada los bloqueantes que solo lo son en el momento de la
    firma (revision de calidad del encargo, fases posteriores) para que el modo
    continuo no genere alarmas prematuras.

    `carpeta` habilita la comprobacion del registro de asistencia por IA.
    """
    res = Resultado("Revision de calidad del archivo"
                    + (" (modo pre-vuelo)" if pre_vuelo else " (previa a la firma)"))
    hallazgos = [e for fn in COMPROBACIONES for e in fn(datos)]
    hallazgos += asistencia_automatizada(datos, carpeta)
    for e in hallazgos:
        if pre_vuelo and e.codigo in {"CAL-080", "CAL-050", "CAL-062"} \
                and e.severidad == BLOQUEANTE:
            e.severidad = RESOLVER
        res.add(e)

    cuenta = {s: sum(1 for e in res.excepciones if e.severidad == s)
              for s in ORDEN_SEVERIDAD}
    res.datos = {
        "bloqueantes": cuenta[BLOQUEANTE],
        "a_resolver": cuenta[RESOLVER],
        "documentacion": cuenta[DOCUMENTAR],
        "informativas": cuenta[INFORMATIVA],
        "riesgos": len(datos.get("riesgos", [])),
        "papeles": len(datos.get("papeles", [])),
        "papeles_concluidos": sum(1 for p in datos.get("papeles", [])
                                  if p.get("estado") == "concluido"),
        "puede_firmarse": cuenta[BLOQUEANTE] == 0 and cuenta[RESOLVER] == 0,
    }
    res.conclusion = (
        "El archivo esta en condiciones de ser firmado: no hay excepciones bloqueantes ni "
        "pendientes de resolver. Queda la revision de juicio del socio firmante, que es "
        "indelegable."
        if res.datos["puede_firmarse"] else
        f"El archivo NO esta en condiciones de firma: {cuenta[BLOQUEANTE]} excepciones "
        f"bloqueantes y {cuenta[RESOLVER]} a resolver antes de firmar."
    )
    return res


def panel_del_socio(datos: dict[str, Any], resultado: Resultado,
                    max_cuestiones: int = 20) -> str:
    """Capa (a): una pagina con lo que exige el juicio del socio.

    Todo lo demas ya esta cuadrado y evidenciado. Aqui solo va lo que no puede
    resolver un script.
    """
    cliente = (datos.get("cliente") or {}).get("nombre", "?")
    ejercicio = datos.get("ejercicio", "?")
    perfil = (datos.get("perfil") or {}).get("perfil", "no determinado")
    mats = datos.get("materialidad", [])
    mg = mats[-1].get("global") if mats else None
    mp = mats[-1].get("ejecucion") if mats else None
    d = resultado.datos

    lineas = [
        f"PANEL DEL SOCIO - {cliente} - ejercicio {ejercicio}",
        "=" * 78,
        f"Perfil del encargo: {perfil}   |   Papeles concluidos: "
        f"{d['papeles_concluidos']}/{d['papeles']}   |   Riesgos: {d['riesgos']}",
        f"Materialidad global: {mg:,.2f} EUR   |   De ejecucion: {mp:,.2f} EUR"
        if mg else "Materialidad: NO DETERMINADA",
        "",
        f"ESTADO: {'APTO PARA FIRMA' if d['puede_firmarse'] else 'NO APTO PARA FIRMA'}"
        f"   ({d['bloqueantes']} bloqueantes, {d['a_resolver']} a resolver, "
        f"{d['documentacion']} de documentacion)",
        "",
        "CUESTIONES QUE REQUIEREN SU JUICIO",
        "-" * 78,
    ]
    criticas = [e for e in resultado.ordenadas()
                if e.severidad in (BLOQUEANTE, RESOLVER)][:max_cuestiones]
    if not criticas:
        lineas.append("  Ninguna. El archivo esta cuadrado, evidenciado y concluido.")
    for i, e in enumerate(criticas, start=1):
        imp = f" [{e.importe:,.2f} EUR]" if e.importe is not None else ""
        lineas.append(f"{i:2d}. [{e.severidad}] {e.area}{imp} {e.descripcion}")
        lineas.append(f"     -> {e.accion}")
    lineas += [
        "",
        "-" * 78,
        "El resto del archivo esta cuadrado y trazado. Este panel no sustituye la",
        "direccion, supervision y revision del encargo, que es responsabilidad",
        "indelegable del socio firmante (NIA-ES 220 Revisada).",
    ]
    return "\n".join(lineas)
