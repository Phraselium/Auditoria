"""Estado del encargo: donde estamos y cual es el siguiente paso.

Con treinta y tantas skills y un estado persistente, "que falta" no es un lujo:
es lo primero que pregunta cualquiera que retoma un encargo despues de unos dias.
"""

from __future__ import annotations

from typing import Any

from .excepciones import BLOQUEANTE, DOCUMENTAR, INFORMATIVA, RESOLVER

ORDEN_FASES = ("aceptacion", "planificacion", "campo", "cierre")
SIMBOLO = {"completa": "OK", "en curso": "..", "pendiente": "--"}


def horas_consumidas(datos: dict[str, Any]) -> float:
    return round(sum(float(p.get("horas") or 0.0) for p in datos.get("papeles", [])), 1)


def horas_estimadas(datos: dict[str, Any]) -> float | None:
    est = (datos.get("perfil") or {}).get("estimacion") or {}
    return est.get("horas_totales")


def pendientes_ordenados(datos: dict[str, Any]) -> list[dict[str, Any]]:
    """Pendientes del cliente, ruta critica primero."""
    return sorted(
        [p for p in datos.get("pendientes", []) if p.get("estado") != "recibido"],
        key=lambda p: (int(p.get("prioridad", 4)), p.get("area", "")))


def siguiente_paso(datos: dict[str, Any]) -> tuple[str, str]:
    """Devuelve (accion, motivo). La prioridad no es negociable: cada nivel
    bloquea a los siguientes."""
    excs = datos.get("excepciones", [])
    papeles = {p["ref"]: p for p in datos.get("papeles", [])}

    bloq = [e for e in excs if e.get("severidad") == BLOQUEANTE]
    if bloq:
        return ("Resolver las excepciones bloqueantes",
                f"{len(bloq)} excepciones bloqueantes impiden avanzar. La primera: "
                f"[{bloq[0].get('codigo')}] {bloq[0].get('descripcion', '')[:120]}")

    p21 = papeles.get("2.1")
    if not p21 or p21.get("estado") != "concluido":
        return ("Ejecutar `ingesta-y-cuadres` (papel 2.1)",
                "Es la puerta de entrada: ninguna prueba de area se ejecuta sobre una "
                "contabilidad que no ha pasado los cuadres de integridad.")

    criticos = [p for p in pendientes_ordenados(datos) if int(p.get("prioridad", 4)) <= 2]
    if criticos:
        cual = criticos[0]
        return (f"Reclamar la documentacion de ruta critica: {cual.get('descripcion', '')}",
                f"{len(criticos)} pendientes de prioridad 1-2. Su plazo de respuesta "
                "-circularizaciones, recuento de existencias- es lo que marca el calendario "
                "del encargo.")

    sin_respuesta = [r for r in datos.get("riesgos", []) if not r.get("respuestas")]
    if sin_respuesta:
        return ("Ejecutar `diseno-de-pruebas` para los riesgos sin respuesta",
                f"{len(sin_respuesta)} riesgos identificados sin procedimiento asignado "
                f"(el primero: {sin_respuesta[0].get('id')} - "
                f"{sin_respuesta[0].get('descripcion', '')[:80]}).")

    en_curso = [p for p in datos.get("papeles", []) if p.get("estado") != "concluido"]
    if en_curso:
        return (f"Concluir el papel {en_curso[0]['ref']} ({en_curso[0].get('titulo', '')})",
                f"{len(en_curso)} papeles abiertos.")

    fases = datos.get("fases", {})
    if fases.get("campo") != "completa":
        return ("Continuar el trabajo de campo con `/auditoria-nia-es:campo <area>`",
                "Quedan areas activas sin ejecutar segun el perfil del encargo.")
    if fases.get("cierre") != "completa":
        return ("Ejecutar `/auditoria-nia-es:cerrar`",
                "El trabajo de campo esta completo: procede el cierre, la evaluacion de "
                "incorrecciones y el informe.")

    resolver = [e for e in excs if e.get("severidad") == RESOLVER]
    if resolver:
        return ("Resolver las excepciones pendientes antes de firmar",
                f"{len(resolver)} excepciones marcadas como 'a resolver antes de firmar'.")

    return ("Ejecutar `revision-de-calidad` completa y proceder a la firma",
            "Todas las fases estan cerradas y no quedan excepciones bloqueantes ni "
            "pendientes de resolver.")


def panel(datos: dict[str, Any], bitacora_resumen: dict[str, Any] | None = None) -> str:
    """Panel operativo del encargo, en una pantalla."""
    cliente = (datos.get("cliente") or {}).get("nombre", "?")
    ejercicio = datos.get("ejercicio", "?")
    perf = datos.get("perfil") or {}
    mats = datos.get("materialidad") or []
    mat = mats[-1] if mats else None
    papeles = datos.get("papeles", [])
    concluidos = sum(1 for p in papeles if p.get("estado") == "concluido")
    riesgos = datos.get("riesgos", [])
    sin_resp = sum(1 for r in riesgos if not r.get("respuestas"))
    excs = datos.get("excepciones", [])
    cuenta = {s: sum(1 for e in excs if e.get("severidad") == s)
              for s in (BLOQUEANTE, RESOLVER, DOCUMENTAR, INFORMATIVA)}

    L = [
        f"ENCARGO: {cliente} - ejercicio {ejercicio}",
        f"Marco: {datos.get('marco', '?')}    "
        f"Perfil: {perf.get('perfil', 'no determinado')}"
        + (f" ({perf.get('puntuacion')} pts)" if perf.get("puntuacion") is not None else "")
        + f"    Actualizado: {datos.get('actualizado', '?')[:19]}",
        "",
        "FASES        " + "   ".join(
            f"{f} [{SIMBOLO.get(datos.get('fases', {}).get(f, 'pendiente'), '--')}]"
            for f in ORDEN_FASES),
        "",
    ]

    if mat:
        L.append(f"MATERIALIDAD Global {mat.get('global', 0):,.2f} EUR | "
                 f"Ejecucion {mat.get('ejecucion', 0):,.2f} EUR | "
                 f"version {mat.get('version')} de {len(mats)}")
        ev = mat.get("evaluacion_recalculo") or {}
        if ev.get("afecta_alcance"):
            L.append("             *** " + ev.get("mensaje", "")[:150])
    else:
        L.append("MATERIALIDAD NO DETERMINADA")

    L += [
        f"PAPELES      {concluidos}/{len(papeles)} concluidos"
        + (f"   Abiertos: {', '.join(p['ref'] for p in papeles if p.get('estado') != 'concluido')}"
           if concluidos < len(papeles) else ""),
        f"RIESGOS      {len(riesgos)}"
        + (f", de los cuales {sin_resp} SIN RESPUESTA" if sin_resp else ", todos con respuesta"),
        f"EXCEPCIONES  {cuenta[BLOQUEANTE]} bloqueantes | {cuenta[RESOLVER]} a resolver | "
        f"{cuenta[DOCUMENTAR]} de documentacion | {cuenta[INFORMATIVA]} informativas",
    ]

    pend = pendientes_ordenados(datos)
    L.append("")
    if pend:
        L.append(f"PENDIENTES DEL CLIENTE ({len(pend)}, ruta critica primero)")
        for p in pend[:8]:
            L.append(f"  [P{p.get('prioridad', 4)}] {p.get('area', '?'):<4} "
                     f"{p.get('descripcion', '')[:60]:<60} "
                     f"solicitado {p.get('solicitado', '?')[:10]}")
        if len(pend) > 8:
            L.append(f"  ... y {len(pend) - 8} mas")
    else:
        L.append("PENDIENTES DEL CLIENTE  ninguno registrado")

    est = horas_estimadas(datos)
    cons = horas_consumidas(datos)
    L.append("")
    if est:
        L.append(f"HORAS        Estimadas {est} h | consumidas {cons} h | "
                 f"desviacion {cons - est:+.1f} h ({(cons - est) / est:+.0%})")
    else:
        L.append(f"HORAS        Consumidas {cons} h (sin estimacion registrada)")

    if bitacora_resumen:
        L.append(f"BITACORA IA  {bitacora_resumen['ejecuciones']} ejecuciones | "
                 f"{bitacora_resumen['validadas']} validadas | "
                 f"{bitacora_resumen['sin_validar']} SIN VALIDAR")

    accion, motivo = siguiente_paso(datos)
    L += ["", "-" * 78, "SIGUIENTE PASO RECOMENDADO", f"  {accion}", f"  Motivo: {motivo}"]
    return "\n".join(L)
