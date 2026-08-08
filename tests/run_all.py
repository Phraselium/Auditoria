"""Ejecuta el banco de pruebas completo y mide la cobertura de la libreria.

    python3 tests/run_all.py

Devuelve 0 solo si las dos baterias pasan y la cobertura de funciones publicas
alcanza el minimo exigido. Este script es el que hay que ejecutar tras instalar
el plugin y tras cualquier cambio en la libreria.
"""

from __future__ import annotations

import ast
import glob
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, os.path.join(RAIZ, "scripts"))
sys.path.insert(0, AQUI)

DIR_LIB = os.path.join(RAIZ, "scripts", "audita")
COBERTURA_MINIMA = 0.95


def funciones_publicas() -> set[str]:
    """Funciones publicas de la libreria mas los subcomandos del CLI.

    El CLI cuenta: es la interfaz por la que las skills invocan todo. Un
    subcomando que nunca se ha ejecutado es una skill que no produce papel.
    """
    out: set[str] = set()
    for f in glob.glob(os.path.join(DIR_LIB, "*.py")):
        mod = os.path.basename(f)[:-3]
        if mod == "__init__":
            continue
        for n in ast.parse(open(f, encoding="utf-8").read()).body:
            if isinstance(n, ast.FunctionDef):
                if mod == "cli" and not n.name.startswith("cmd_"):
                    continue  # del CLI solo interesan los subcomandos
                if not mod == "cli" and n.name.startswith("_"):
                    continue
                out.add(f"{mod}.{n.name}")
            elif isinstance(n, ast.ClassDef) and mod != "cli":
                for m in n.body:
                    if isinstance(m, ast.FunctionDef) and not m.name.startswith("_"):
                        out.add(f"{mod}.{n.name}.{m.name}")
    return out


def main() -> int:
    os.chdir(RAIZ)
    ejecutadas: set[str] = set()

    def perfilador(frame, event, arg):
        if event == "call" and frame.f_code.co_filename.startswith(DIR_LIB):
            ejecutadas.add(f"{os.path.basename(frame.f_code.co_filename)[:-3]}."
                           f"{frame.f_code.co_name}")
        return None

    import test_aceptacion
    import test_libreria

    codigos = []
    sys.setprofile(perfilador)
    try:
        codigos.append(("Aceptacion (6 criterios del encargo)", test_aceptacion.main()))
        codigos.append(("Unitarias de la libreria", test_libreria.main()))
    finally:
        sys.setprofile(None)

    pub = funciones_publicas()
    # los metodos de clase se registran por su nombre simple
    simples = {k.split(".")[0] + "." + k.split(".")[-1] for k in pub}
    cubiertas = {k for k in simples if k in ejecutadas}
    sin_cubrir = sorted(simples - cubiertas)
    cobertura = len(cubiertas) / len(simples) if simples else 1.0

    print("\n" + "=" * 78)
    print("RESULTADO GLOBAL")
    print("=" * 78)
    for nombre, code in codigos:
        print(f"  [{'OK  ' if code == 0 else 'FALLA'}] {nombre}")
    print(f"\n  Cobertura de la libreria: {len(cubiertas)}/{len(simples)} "
          f"funciones publicas ejecutadas ({cobertura:.0%}, minimo exigido "
          f"{COBERTURA_MINIMA:.0%})")
    if sin_cubrir:
        print(f"\n  Sin ejecutar ({len(sin_cubrir)}):")
        for k in sin_cubrir:
            print("    -", k)

    ok = all(c == 0 for _, c in codigos) and cobertura >= COBERTURA_MINIMA
    print("\n  " + ("TODO CORRECTO. El plugin esta listo para uso."
                    if ok else "HAY FALLOS. Revise la salida anterior."))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
