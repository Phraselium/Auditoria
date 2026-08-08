"""Ingesta y normalizacion de ficheros contables.

Objetivo: que el despacho no tenga que tocar el fichero que le manda el cliente.
Se aceptan xlsx/xls/csv/txt con cabeceras en cualquier fila, columnas en
cualquier orden y nombres en cualquiera de las variantes habituales de los ERP
espanoles (A3, Sage, Contasol, Holded, SAP B1) y de las extracciones de
Data Sniper / OCR.

Salida normalizada de un balance de sumas y saldos:
    cuenta | descripcion | debe | haber | saldo | apertura (opcional)
Salida normalizada de un diario:
    asiento | fecha | cuenta | descripcion | debe | haber | usuario | documento
"""

from __future__ import annotations

import os
import re
from typing import Any

import pandas as pd

from .plan_contable import normaliza_cuenta
from .traza import Traza

# ---------------------------------------------------------------------------
# Diccionario de sinonimos de cabecera. Se compara en minusculas y sin acentos.
# ---------------------------------------------------------------------------
SINONIMOS = {
    "cuenta": ["cuenta", "codigo", "cod", "codcuenta", "cta", "nº cuenta", "n cuenta",
               "numero cuenta", "cuenta contable", "account", "codigo cuenta"],
    "descripcion": ["descripcion", "concepto", "titulo", "nombre", "denominacion",
                    "desc", "nombre cuenta", "descripcion cuenta", "detalle"],
    "debe": ["debe", "cargo", "cargos", "importe debe", "suma debe", "debito",
             "total debe", "d"],
    "haber": ["haber", "abono", "abonos", "importe haber", "suma haber", "credito",
              "total haber", "h"],
    "saldo": ["saldo", "saldo final", "saldo actual", "sdo", "saldo cuenta",
              "saldo periodo"],
    "saldo_deudor": ["saldo deudor", "sdo deudor", "deudor", "saldo d"],
    "saldo_acreedor": ["saldo acreedor", "sdo acreedor", "acreedor", "saldo h"],
    "apertura": ["apertura", "saldo apertura", "saldo inicial", "saldo anterior",
                 "inicial", "saldo ejercicio anterior", "ejercicio anterior",
                 "ano anterior", "n-1"],
    "asiento": ["asiento", "n asiento", "nº asiento", "numero asiento", "apunte",
                "num asiento", "diario", "n. asiento"],
    "fecha": ["fecha", "f. asiento", "fecha asiento", "fecha operacion", "date"],
    "usuario": ["usuario", "user", "operador", "creado por", "alta usuario"],
    "documento": ["documento", "doc", "n documento", "factura", "referencia", "ref"],
}

_ACENTOS = str.maketrans("áàäâéèëêíìïîóòöôúùüûñ", "aaaaeeeeiiiioooouuuun")


def _norm(txt: Any) -> str:
    return str(txt).strip().lower().translate(_ACENTOS).replace(".", "").replace("_", " ")


def _empareja(cabeceras: list[Any]) -> dict[str, int]:
    """Devuelve {campo_normalizado: indice_columna}."""
    encontrado: dict[str, int] = {}
    normalizadas = [_norm(c) for c in cabeceras]
    for campo, variantes in SINONIMOS.items():
        for i, cab in enumerate(normalizadas):
            if i in encontrado.values():
                continue
            if cab in variantes:
                encontrado[campo] = i
                break
        if campo in encontrado:
            continue
        # segunda pasada: coincidencia por inclusion (mas laxa)
        for i, cab in enumerate(normalizadas):
            if i in encontrado.values() or not cab:
                continue
            if any(cab.startswith(v) or v == cab for v in variantes):
                encontrado[campo] = i
                break
    return encontrado


def _a_numero(v: Any) -> float:
    """Convierte importes en formato espanol ('1.234,56', '(1.234,56)', '1 234,56')."""
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return 0.0
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip()
    if not s or s in {"-", "--"}:
        return 0.0
    negativo = s.startswith("(") and s.endswith(")")
    s = s.strip("()").replace("€", "").replace(" ", "").replace(" ", "")
    if "," in s and "." in s:
        # el ultimo separador que aparece es el decimal
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")
        else:
            s = s.replace(",", "")
    elif "," in s:
        s = s.replace(".", "").replace(",", ".")
    try:
        n = float(s)
    except ValueError:
        return 0.0
    return -n if negativo else n


def lee_bruto(path: str, hoja: Any = 0) -> pd.DataFrame:
    """Lee el fichero sin interpretar cabeceras (header=None)."""
    ext = os.path.splitext(path)[1].lower()
    if ext in {".xlsx", ".xlsm", ".xls"}:
        return pd.read_excel(path, sheet_name=hoja, header=None, dtype=object)
    if ext in {".csv", ".txt", ".tsv"}:
        for sep in (";", ",", "\t", "|"):
            try:
                df = pd.read_csv(path, sep=sep, header=None, dtype=object,
                                 encoding="utf-8-sig", engine="python")
                if df.shape[1] > 1:
                    return df
            except Exception:
                continue
        return pd.read_csv(path, header=None, dtype=object, encoding="utf-8-sig")
    raise ValueError(f"Formato no soportado: {ext}")


def localiza_cabecera(bruto: pd.DataFrame, minimo: int = 2,
                      max_filas: int = 30) -> tuple[int, dict[str, int]]:
    """Busca la fila de cabecera. Devuelve (indice_fila, mapa_columnas).

    Los ERP suelen meter 3-8 filas de titulo, NIF, fechas y logotipo antes de la
    tabla real; por eso no se asume header=0.
    """
    mejor = (-1, {})
    for i in range(min(max_filas, len(bruto))):
        mapa = _empareja(list(bruto.iloc[i].values))
        if len(mapa) > len(mejor[1]):
            mejor = (i, mapa)
        if "cuenta" in mapa and len(mapa) >= minimo + 1:
            return i, mapa
    if len(mejor[1]) < minimo:
        raise ValueError(
            "No se ha localizado la fila de cabecera. Cabeceras detectadas: "
            f"{list(bruto.iloc[0].values)[:10]}"
        )
    return mejor


def _letra_columna(i: int) -> str:
    letra = ""
    i += 1
    while i:
        i, r = divmod(i - 1, 26)
        letra = chr(65 + r) + letra
    return letra


def normaliza_sumas_y_saldos(path: str, hoja: Any = 0) -> tuple[pd.DataFrame, dict]:
    """Balance de sumas y saldos al maximo detalle -> DataFrame normalizado.

    Soporta cuentas de 8 a 10 digitos y de 6 a 8 grupos. Conserva la fila de
    origen de cada registro (columna `_fila_origen`) para la traza.
    """
    bruto = lee_bruto(path, hoja)
    fila_cab, mapa = localiza_cabecera(bruto)
    if "cuenta" not in mapa:
        raise ValueError("No se ha identificado la columna de cuenta.")

    datos = bruto.iloc[fila_cab + 1:].reset_index(drop=True)
    filas: list[dict[str, Any]] = []
    for pos, (_, r) in enumerate(datos.iterrows()):
        cuenta_bruta = r.iloc[mapa["cuenta"]]
        cuenta = normaliza_cuenta(cuenta_bruta)
        if not cuenta:
            continue
        # descartar filas de totales/subtotales que arrastran texto en la columna cuenta
        if len(cuenta) < 3:
            continue
        reg: dict[str, Any] = {
            "cuenta": cuenta,
            "cuenta_original": str(cuenta_bruta).strip(),
            "descripcion": (str(r.iloc[mapa["descripcion"]]).strip()
                            if "descripcion" in mapa else ""),
            "debe": _a_numero(r.iloc[mapa["debe"]]) if "debe" in mapa else 0.0,
            "haber": _a_numero(r.iloc[mapa["haber"]]) if "haber" in mapa else 0.0,
            "apertura": _a_numero(r.iloc[mapa["apertura"]]) if "apertura" in mapa else 0.0,
            "_fila_origen": fila_cab + 2 + pos,  # 1-based, como lo ve Excel
        }
        if reg["descripcion"] in {"nan", "None"}:
            reg["descripcion"] = ""
        # saldo: explicito, o deudor/acreedor separados, o debe - haber
        if "saldo" in mapa:
            reg["saldo"] = _a_numero(r.iloc[mapa["saldo"]])
        elif "saldo_deudor" in mapa or "saldo_acreedor" in mapa:
            d = _a_numero(r.iloc[mapa["saldo_deudor"]]) if "saldo_deudor" in mapa else 0.0
            h = _a_numero(r.iloc[mapa["saldo_acreedor"]]) if "saldo_acreedor" in mapa else 0.0
            reg["saldo"] = d - h
        else:
            reg["saldo"] = reg["debe"] - reg["haber"]
        filas.append(reg)

    df = pd.DataFrame(filas)
    if df.empty:
        raise ValueError(f"No se han extraido registros de {os.path.basename(path)}")

    df["grupo"] = df["cuenta"].str[0]
    df["longitud"] = df["cuenta"].str.len()

    meta = {
        "fichero": os.path.abspath(path),
        "hoja": hoja if isinstance(hoja, str) else "1",
        "fila_cabecera": fila_cab + 1,
        "columnas": {k: _letra_columna(v) for k, v in mapa.items()},
        "registros": len(df),
        "grupos": sorted(df["grupo"].unique().tolist()),
        "longitudes_cuenta": sorted(df["longitud"].unique().tolist()),
        "tiene_apertura": "apertura" in mapa,
    }
    return df, meta


def traza_de(meta: dict, fila_origen: int, campo: str) -> Traza:
    """Traza a celda concreta del fichero de origen."""
    col = meta["columnas"].get(campo, "")
    return Traza(meta["fichero"], hoja=meta.get("hoja"), ref=f"{col}{fila_origen}")


def normaliza_diario(path: str, hoja: Any = 0) -> tuple[pd.DataFrame, dict]:
    """Libro diario -> DataFrame normalizado."""
    bruto = lee_bruto(path, hoja)
    fila_cab, mapa = localiza_cabecera(bruto)
    if "cuenta" not in mapa:
        raise ValueError("No se ha identificado la columna de cuenta en el diario.")

    datos = bruto.iloc[fila_cab + 1:].reset_index(drop=True)
    filas: list[dict[str, Any]] = []
    asiento_actual: Any = None
    for pos, (_, r) in enumerate(datos.iterrows()):
        cuenta = normaliza_cuenta(r.iloc[mapa["cuenta"]])
        if not cuenta or len(cuenta) < 3:
            continue
        asiento = r.iloc[mapa["asiento"]] if "asiento" in mapa else None
        if asiento is None or (isinstance(asiento, float) and pd.isna(asiento)) \
                or str(asiento).strip() == "":
            asiento = asiento_actual  # ERP que solo imprime el nº en la 1ª linea
        else:
            asiento_actual = asiento
        fecha = pd.NaT
        if "fecha" in mapa:
            fecha = pd.to_datetime(r.iloc[mapa["fecha"]], errors="coerce", dayfirst=True)
        filas.append({
            "asiento": str(asiento).strip() if asiento is not None else "",
            "fecha": fecha,
            "cuenta": cuenta,
            "descripcion": (str(r.iloc[mapa["descripcion"]]).strip()
                            if "descripcion" in mapa else ""),
            "debe": _a_numero(r.iloc[mapa["debe"]]) if "debe" in mapa else 0.0,
            "haber": _a_numero(r.iloc[mapa["haber"]]) if "haber" in mapa else 0.0,
            "usuario": (str(r.iloc[mapa["usuario"]]).strip()
                        if "usuario" in mapa else ""),
            "documento": (str(r.iloc[mapa["documento"]]).strip()
                          if "documento" in mapa else ""),
            "_fila_origen": fila_cab + 2 + pos,
        })

    df = pd.DataFrame(filas)
    if df.empty:
        raise ValueError(f"No se han extraido apuntes de {os.path.basename(path)}")
    df["descripcion"] = df["descripcion"].replace({"nan": "", "None": ""})
    meta = {
        "fichero": os.path.abspath(path),
        "hoja": hoja if isinstance(hoja, str) else "1",
        "fila_cabecera": fila_cab + 1,
        "columnas": {k: _letra_columna(v) for k, v in mapa.items()},
        "apuntes": len(df),
        "asientos": df["asiento"].nunique(),
        "tiene_fecha": "fecha" in mapa,
        "tiene_usuario": "usuario" in mapa,
    }
    return df, meta


def lee_tabla(path: str, hoja: Any = 0) -> tuple[pd.DataFrame, dict]:
    """Lectura generica con deteccion de cabecera, para ficheros auxiliares
    (cuadros de leasing, extractos, listados de inmovilizado, extracciones de
    Data Sniper). No normaliza nombres: devuelve las columnas tal cual, ya
    limpias, y la traza."""
    bruto = lee_bruto(path, hoja)
    fila_cab = 0
    for i in range(min(30, len(bruto))):
        no_vacias = sum(1 for v in bruto.iloc[i].values
                        if v is not None and str(v).strip() not in {"", "nan"})
        if no_vacias >= max(2, int(bruto.shape[1] * 0.5)):
            fila_cab = i
            break
    cabeceras = [str(c).strip() for c in bruto.iloc[fila_cab].values]
    df = bruto.iloc[fila_cab + 1:].reset_index(drop=True)
    df.columns = cabeceras
    df = df.dropna(how="all")
    df["_fila_origen"] = [fila_cab + 2 + i for i in range(len(df))]
    meta = {
        "fichero": os.path.abspath(path),
        "hoja": hoja if isinstance(hoja, str) else "1",
        "fila_cabecera": fila_cab + 1,
        "columnas": {c: _letra_columna(i) for i, c in enumerate(cabeceras)},
        "registros": len(df),
    }
    return df, meta


def _tokens(texto: Any) -> list[str]:
    """Descompone un nombre de columna en palabras comparables.

    'Nº Contrato' -> ['n', 'contrato']   |   'importe_financiado' -> ['importe',
    'financiado']   |   '% Amortizacion' -> ['amortizacion']
    """
    return [t for t in re.split(r"[^a-z0-9]+", _norm(texto)) if t]


def columna(df: pd.DataFrame, *candidatos: str) -> str | None:
    """Localiza una columna por cualquiera de sus nombres probables.

    El emparejamiento es por PALABRAS, no por subcadena. La comparacion por
    subcadena produce falsos positivos graves con candidatos cortos: 'id' esta
    contenido en 'Entidad', y eso hace que el identificador del contrato acabe
    siendo el nombre del banco. Con tokens, 'id' solo casa con una columna que
    tenga la palabra 'id'.
    """
    cols = {c: _tokens(c) for c in df.columns}
    # 1. misma secuencia de palabras
    for cand in candidatos:
        ct = _tokens(cand)
        if not ct:
            continue
        for c, t in cols.items():
            if t == ct:
                return c
    # 2. todas las palabras del candidato presentes en la columna
    for cand in candidatos:
        ct = _tokens(cand)
        if not ct:
            continue
        for c, t in cols.items():
            if all(x in t for x in ct):
                return c
    return None


def num(df: pd.DataFrame, col: str | None) -> pd.Series:
    """Serie numerica robusta a formatos espanoles."""
    if col is None or col not in df.columns:
        return pd.Series([0.0] * len(df), index=df.index)
    return df[col].map(_a_numero)
