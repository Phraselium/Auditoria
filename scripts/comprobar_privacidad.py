#!/usr/bin/env python3
"""Comprueba que no se sube al repositorio nada del despacho ni de sus clientes.

El plugin es codigo publicable; los papeles de trabajo, la cartera y los datos
de los clientes no lo son, y estan sujetos al deber de secreto del art. 31 LAC,
a la normativa de prevencion del blanqueo y al RGPD.

    python3 scripts/comprobar_privacidad.py              # lo versionado
    python3 scripts/comprobar_privacidad.py --staged     # lo que va al commit
    python3 scripts/comprobar_privacidad.py --historial  # todo el historial
    python3 scripts/comprobar_privacidad.py --instalar-hook

Solo biblioteca estandar. Codigo de salida 1 si encuentra algo.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Ficheros que no deben versionarse jamas, ni siquiera vacios.
PROHIBIDOS = re.compile(
    r"(^|/)(encargos|clientes|salidas)/"
    r"|\.(xlsx|xlsm|xls|ods|csv|pfx|p12|key|pem)$"
    r"|(^|/)encargo\.json$"
    r"|(^|/)uso-ia\.log$"
    r"|(^|/)config/configuracion\.md$"
    r"|(^|/)datos/nombres_privados\.txt$"
    r"|(^|/)referencias/tarifas\.json$",
    re.I)

# Extensiones cuyo contenido se inspecciona
TEXTO = (".md", ".py", ".json", ".txt", ".yaml", ".yml", ".toml", ".cfg")

# Rutas que se saltan: ejemplos sinteticos y material generado
EXENTAS = re.compile(r"(^|/)(ejemplos|dist|tests/fixtures|tests/salida)/")

LETRAS_NIF = "TRWAGMYFPDXBNJZSQVHLCKE"
LETRAS_CIF = "JABCDEFGHI"


def nif_valido(s: str) -> bool:
    """NIF de persona fisica: 8 digitos + letra de control."""
    return len(s) == 9 and s[:8].isdigit() and s[8].upper() == LETRAS_NIF[int(s[:8]) % 23]


def nie_valido(s: str) -> bool:
    """NIE: X/Y/Z + 7 digitos + letra de control."""
    if len(s) != 9 or s[0].upper() not in "XYZ" or not s[1:8].isdigit():
        return False
    n = int(str("XYZ".index(s[0].upper())) + s[1:8])
    return s[8].upper() == LETRAS_NIF[n % 23]


def cif_valido(s: str) -> bool:
    """CIF de persona juridica: letra + 7 digitos + digito o letra de control."""
    if len(s) != 9 or s[0].upper() not in "ABCDEFGHJNPQRSUVW" or not s[1:8].isdigit():
        return False
    pares = sum(int(d) for d in s[2:8:2])
    impares = 0
    for d in s[1:8:2]:
        x = int(d) * 2
        impares += x // 10 + x % 10
    control = (10 - (pares + impares) % 10) % 10
    return s[8].upper() in (str(control), LETRAS_CIF[control])


def iban_valido(s: str) -> bool:
    """IBAN por el resto 97 de la ISO 13616."""
    s = s.replace(" ", "").upper()
    if not re.fullmatch(r"[A-Z]{2}\d{2}[A-Z0-9]{10,30}", s):
        return False
    r = s[4:] + s[:4]
    return int("".join(str(int(c, 36)) for c in r)) % 97 == 1


PATRONES = [
    ("NIF/NIE/CIF", re.compile(r"\b[A-Za-z0-9]\d{7}[A-Za-z0-9]\b|\b\d{8}[A-Za-z]\b"),
     lambda s: nif_valido(s) or nie_valido(s) or cif_valido(s)),
    ("IBAN", re.compile(r"\b[A-Z]{2}\d{2}[ ]?[A-Z0-9]{4}(?:[ ]?[A-Z0-9]{4}){2,7}\b"),
     iban_valido),
    ("correo", re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.]{2,}\b"),
     lambda s: not s.lower().endswith((".example", "@example.com", "@ejemplo.es"))),
    ("telefono", re.compile(r"\b(?:\+34[ -]?)?[6789]\d{2}[ -]?\d{3}[ -]?\d{3}\b"),
     lambda s: True),
]


def nombres_privados() -> list[str]:
    ruta = os.path.join(RAIZ, "datos", "nombres_privados.txt")
    if not os.path.exists(ruta):
        return []
    return [l.strip() for l in open(ruta, encoding="utf-8")
            if l.strip() and not l.startswith("#")]


def ficheros(modo: str) -> list[str]:
    if modo == "staged":
        cmd = ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"]
    else:
        cmd = ["git", "ls-files"]
    r = subprocess.run(cmd, cwd=RAIZ, capture_output=True, text=True)
    return [l for l in r.stdout.splitlines() if l]


def revisa(rutas: list[str], privados: list[str]) -> list[str]:
    hallazgos = []
    for rel in rutas:
        if PROHIBIDOS.search(rel):
            hallazgos.append(f"{rel}: fichero que no debe versionarse")
            continue
        if EXENTAS.search(rel) or not rel.endswith(TEXTO):
            continue
        completo = os.path.join(RAIZ, rel)
        if not os.path.exists(completo):
            continue
        try:
            texto = open(completo, encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        for n, linea in enumerate(texto.splitlines(), 1):
            for etiqueta, patron, valida in PATRONES:
                for m in patron.findall(linea):
                    if valida(m):
                        hallazgos.append(f"{rel}:{n}: {etiqueta} con formato real: {m}")
            for nombre in privados:
                if nombre.lower() in linea.lower():
                    hallazgos.append(f"{rel}:{n}: nombre de su lista privada: {nombre}")
    return hallazgos


HOOK = """#!/bin/sh
# Instalado por scripts/comprobar_privacidad.py --instalar-hook
exec python3 "$(git rev-parse --show-toplevel)/scripts/comprobar_privacidad.py" --staged
"""


def instala_hook() -> int:
    d = subprocess.run(["git", "rev-parse", "--git-path", "hooks"], cwd=RAIZ,
                       capture_output=True, text=True).stdout.strip()
    destino = os.path.join(RAIZ, d, "pre-commit")
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    with open(destino, "w", encoding="utf-8") as fh:
        fh.write(HOOK)
    os.chmod(destino, 0o755)
    print(f"Hook de pre-commit instalado en {destino}")
    print("Ningun commit se creara sin pasar esta comprobacion.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--staged", action="store_true", help="solo lo que va al commit")
    ap.add_argument("--historial", action="store_true", help="todo el historial de git")
    ap.add_argument("--instalar-hook", action="store_true")
    a = ap.parse_args()

    if a.instalar_hook:
        return instala_hook()

    privados = nombres_privados()
    if a.historial:
        r = subprocess.run(["git", "log", "--all", "--pretty=format:", "--name-only",
                            "--diff-filter=ACM"], cwd=RAIZ, capture_output=True, text=True)
        rutas = sorted({l for l in r.stdout.splitlines() if l})
        print(f"Revisando {len(rutas)} rutas que han existido en el historial.")
        print("Aviso: solo se comprueba el contenido de las que siguen en el arbol.")
    else:
        rutas = ficheros("staged" if a.staged else "versionado")

    hallazgos = revisa(rutas, privados)
    if not privados:
        print("Aviso: no hay datos/nombres_privados.txt. No se comprueban razones "
              "sociales de su cartera, solo identificadores y ficheros.")
    if hallazgos:
        print(f"\nPRIVACIDAD: {len(hallazgos)} hallazgos\n")
        for h in hallazgos[:40]:
            print("  -", h)
        if len(hallazgos) > 40:
            print(f"  ... y {len(hallazgos) - 40} mas")
        print("\nCorrijalos antes de subir nada. Si ya se ha subido, no basta con un "
              "commit nuevo:\nhay que reescribir el historial y forzar el push.")
        return 1
    print(f"Sin datos privados en {len(rutas)} ficheros revisados.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
