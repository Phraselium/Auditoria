"""Test de asientos del diario (NIA-ES 240.32).

Respuesta al riesgo de elusion de controles por la direccion, que se presume
siempre presente. La salida es por excepcion y priorizada: lo que importa no es
listar 400 asientos raros, sino los 15 que hay que mirar.

Cada filtro puntua; la puntuacion total ordena la revision.
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from .excepciones import DOCUMENTAR, INFORMATIVA, RESOLVER, Excepcion, Resultado

# Festivos nacionales de aplicacion general en Espana (sin autonomicos ni locales,
# que se anaden por configuracion en skills/convenciones-dula/SKILL.md).
FESTIVOS_FIJOS = [(1, 1), (1, 6), (5, 1), (8, 15), (10, 12), (11, 1),
                  (12, 6), (12, 8), (12, 25)]

PESOS = {
    "fin_de_semana": 2,
    "festivo": 2,
    "ultimos_dias": 3,
    "importe_redondo": 2,
    "sin_descripcion": 3,
    "cuenta_rara": 3,
    "contrapartida_atipica": 4,
    "usuario_infrecuente": 3,
    "ingreso_contra_no_cliente": 5,
    "importe_muy_alto": 2,
}


def _es_festivo(f: pd.Timestamp) -> bool:
    return (f.month, f.day) in FESTIVOS_FIJOS


def analiza(diario: pd.DataFrame, fin_ejercicio: str | pd.Timestamp,
            materialidad_ejecucion: float | None = None,
            perfil: str = "ESTANDAR", umbral_puntuacion: int = 4,
            max_reportados: int = 40) -> tuple[Resultado, pd.DataFrame]:
    """Aplica los filtros y devuelve los asientos priorizados.

    En perfil LIGERO se aplican solo los 4 filtros de mayor rendimiento; en
    ESTANDAR y COMPLEJO, los nueve. La reduccion en LIGERO es de eficiencia, no
    de alcance: los filtros omitidos son los que en poblaciones pequenas generan
    ruido sin aportar (perfilado de usuarios, cuentas raras).
    """
    fin = pd.Timestamp(fin_ejercicio)
    d = diario.copy()
    if "fecha" not in d.columns:
        d["fecha"] = pd.NaT
    d["fecha"] = pd.to_datetime(d["fecha"], errors="coerce")

    reducido = perfil.upper() == "LIGERO"
    filtros_activos = ({"ultimos_dias", "importe_redondo", "sin_descripcion",
                        "ingreso_contra_no_cliente"} if reducido else set(PESOS))

    # --- agregacion por asiento ---
    asientos = d.groupby("asiento").agg(
        fecha=("fecha", "min"),
        importe=("debe", "sum"),
        lineas=("cuenta", "count"),
        cuentas=("cuenta", lambda s: sorted(set(s))),
        usuario=("usuario", "first") if "usuario" in d.columns else ("cuenta", "first"),
        descripcion=("descripcion", lambda s: " ".join(
            str(x) for x in s if str(x).strip() not in {"", "nan"})),
    ).reset_index()

    # --- estadisticas de la poblacion ---
    frecuencia_cuenta = d["cuenta"].value_counts()
    cuentas_raras = set(frecuencia_cuenta[frecuencia_cuenta <= 2].index)
    if "usuario" in d.columns and d["usuario"].astype(str).str.strip().ne("").any():
        frec_usuario = d["usuario"].value_counts()
        usuarios_raros = set(frec_usuario[frec_usuario < max(frec_usuario.max() * 0.02, 3)].index)
    else:
        usuarios_raros = set()

    pares = {}
    for _, r in asientos.iterrows():
        cs = r["cuentas"]
        for i in range(len(cs)):
            for j in range(i + 1, len(cs)):
                clave = (cs[i][:3], cs[j][:3])
                pares[clave] = pares.get(clave, 0) + 1
    pares_raros = {k for k, v in pares.items() if v == 1}

    umbral_alto = (materialidad_ejecucion if materialidad_ejecucion
                   else float(asientos["importe"].quantile(0.99)))

    filas: list[dict[str, Any]] = []
    for _, r in asientos.iterrows():
        motivos: list[str] = []
        puntos = 0
        f = r["fecha"]

        if "fin_de_semana" in filtros_activos and pd.notna(f) and f.weekday() >= 5:
            motivos.append("Contabilizado en fin de semana")
            puntos += PESOS["fin_de_semana"]
        if "festivo" in filtros_activos and pd.notna(f) and _es_festivo(f):
            motivos.append("Contabilizado en festivo nacional")
            puntos += PESOS["festivo"]
        if "ultimos_dias" in filtros_activos and pd.notna(f) and \
                0 <= (fin - f).days <= 5:
            motivos.append("Asiento de los ultimos 5 dias del ejercicio")
            puntos += PESOS["ultimos_dias"]

        imp = abs(float(r["importe"]))
        if "importe_redondo" in filtros_activos and imp >= 1000 and imp % 1000 == 0:
            motivos.append(f"Importe redondo ({imp:,.2f} EUR)")
            puntos += PESOS["importe_redondo"]
        if "importe_muy_alto" in filtros_activos and imp >= umbral_alto:
            motivos.append(f"Importe superior a la materialidad de ejecucion")
            puntos += PESOS["importe_muy_alto"]

        if "sin_descripcion" in filtros_activos and not str(r["descripcion"]).strip():
            motivos.append("Sin descripcion / concepto")
            puntos += PESOS["sin_descripcion"]

        cs = r["cuentas"]
        if "cuenta_rara" in filtros_activos:
            raras = [c for c in cs if c in cuentas_raras]
            if raras:
                motivos.append(f"Usa cuentas de utilizacion excepcional ({', '.join(raras[:3])})")
                puntos += PESOS["cuenta_rara"]
        if "contrapartida_atipica" in filtros_activos and len(cs) >= 2:
            atipicos = [p for i in range(len(cs)) for j in range(i + 1, len(cs))
                        if (p := (cs[i][:3], cs[j][:3])) in pares_raros]
            if atipicos:
                motivos.append(f"Contrapartida no habitual ({atipicos[0][0]} / {atipicos[0][1]})")
                puntos += PESOS["contrapartida_atipica"]
        if "usuario_infrecuente" in filtros_activos and r["usuario"] in usuarios_raros:
            motivos.append(f"Usuario de baja frecuencia ({r['usuario']})")
            puntos += PESOS["usuario_infrecuente"]

        # presuncion de fraude en el reconocimiento de ingresos: ingreso cuya
        # contrapartida no es un derecho de cobro ni tesoreria
        if "ingreso_contra_no_cliente" in filtros_activos:
            tiene_ingreso = any(c.startswith("70") for c in cs)
            contrapartida_normal = any(c[:2] in {"43", "44", "57", "47"} for c in cs)
            if tiene_ingreso and not contrapartida_normal:
                motivos.append("Ingreso sin contrapartida en clientes ni tesoreria")
                puntos += PESOS["ingreso_contra_no_cliente"]

        if puntos >= umbral_puntuacion:
            filas.append({
                "asiento": r["asiento"], "fecha": f, "importe": round(imp, 2),
                "lineas": int(r["lineas"]), "usuario": r["usuario"],
                "descripcion": str(r["descripcion"])[:120],
                "cuentas": ", ".join(cs[:6]),
                "puntuacion": puntos, "motivos": "; ".join(motivos),
            })

    seleccion = pd.DataFrame(filas)
    if not seleccion.empty:
        seleccion = seleccion.sort_values(["puntuacion", "importe"],
                                          ascending=[False, False]).reset_index(drop=True)

    res = Resultado("Test de asientos del diario")
    for _, r in seleccion.head(max_reportados).iterrows():
        res.add(Excepcion(
            "DIA-001", RESOLVER if r["puntuacion"] >= 7 else DOCUMENTAR, "2.8",
            f"Asiento {r['asiento']} ({r['fecha'].date() if pd.notna(r['fecha']) else 's/f'}, "
            f"{r['importe']:,.2f} EUR): {r['motivos']}.",
            importe=float(r["importe"]), origen=f"diario, asiento {r['asiento']}",
            causa_sugerida="Puede responder a una operacion legitima; el objetivo del filtro "
                           "es dirigir la inspeccion, no presumir irregularidad.",
            accion="Obtener el soporte del asiento y verificar su razonabilidad y su "
                   "correcta imputacion.",
            referencia_normativa="NIA-ES 240.32",
        ))
    if len(seleccion) > max_reportados:
        res.add(Excepcion(
            "DIA-002", INFORMATIVA, "2.8",
            f"Se han seleccionado {len(seleccion)} asientos por encima del umbral de "
            f"puntuacion; se reportan los {max_reportados} de mayor prioridad. El resto "
            "figura en la hoja de detalle del papel de trabajo.",
            origen="diario",
            accion="Ampliar la revision si los examinados revelan incidencias.",
        ))

    res.datos = {
        "asientos_totales": int(len(asientos)),
        "seleccionados": int(len(seleccion)),
        "filtros_aplicados": sorted(filtros_activos),
        "umbral_puntuacion": umbral_puntuacion,
        "reportados": min(len(seleccion), max_reportados),
    }
    res.conclusion = (
        f"Analizados {len(asientos)} asientos con {len(filtros_activos)} filtros. "
        + ("Ningun asiento supera el umbral de priorizacion; no se han identificado "
           "indicios de asientos inusuales que requieran investigacion."
           if seleccion.empty else
           f"{len(seleccion)} asientos superan el umbral; se someten a revision los "
           f"{min(len(seleccion), max_reportados)} de mayor puntuacion."))
    return res, seleccion
