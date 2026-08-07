#!/usr/bin/env python3
"""Construye el paquete .zip de dula-audit para claude.ai.

claude.ai no admite plugins: admite SKILLS SUELTAS en .zip, subidas desde
Ajustes. Y su frontmatter solo acepta los seis campos de la especificacion
Agent Skills (name, description, license, compatibility, metadata,
allowed-tools). Los campos `when_to_use`, `argument-hint` y `user-invocable`
que usa Claude Code producirian el error:

    Unexpected key(s) in SKILL.md frontmatter: argument-hint.

Por eso no se puede subir el plugin tal cual. Este script GENERA el paquete a
partir del plugin, de modo que ambos salen siempre de la misma fuente y no se
desincronizan:

  - Las 35 skills se convierten en ficheros de `procedimientos/`, que Claude lee
    solo cuando los necesita (divulgacion progresiva). Su coste en contexto es
    cero hasta que se abren.
  - Un unico SKILL.md hace de indice: dice que hay y cuando usar cada cosa.
  - La libreria Python y las referencias viajan enteras.

    python3 tools/construir_claude_ai.py
"""

from __future__ import annotations

import glob
import os
import re
import shutil
import sys
import zipfile

import yaml

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DESTINO = os.path.join(RAIZ, "build")
NOMBRE = "dula-audit"

# Limites de la especificacion Agent Skills
MAX_NOMBRE = 64
MAX_DESCRIPCION = 1024
CAMPOS_PERMITIDOS = {"name", "description", "license", "compatibility",
                     "metadata", "allowed-tools"}

# Orden en que se presentan los procedimientos en el indice
FASES = [
    ("Fase 0 — Captación y aceptación", [
        "estimacion-encargo", "aceptacion-e-independencia", "escalado-del-encargo"]),
    ("Fase 1 — Planificación", [
        "entendimiento-entidad", "materialidad", "mapa-de-riesgos",
        "diseno-de-pruebas", "plan-y-solicitud-informacion"]),
    ("Fase 2 — Trabajo de campo (transversales)", [
        "ingesta-y-cuadres", "comparador-documental", "analiticos", "muestreo",
        "test-asientos-diario", "area-runner"]),
    ("Fase 2 — Áreas", [
        "area-inmovilizado", "area-existencias", "area-clientes-e-ingresos",
        "area-proveedores-y-compras", "area-tesoreria-y-financiacion",
        "area-arrendamientos", "area-fondos-propios-y-reservas", "area-personal",
        "area-fiscal", "area-provisiones-y-contingencias", "area-subvenciones",
        "area-partes-vinculadas", "saldos-apertura"]),
    ("Fase 3 — Cierre e informe", [
        "evaluacion-de-incorrecciones", "hechos-posteriores-y-empresa-en-funcionamiento",
        "comunicaciones-y-manifestaciones", "redaccion-informe", "revision-de-calidad",
        "archivo-y-cierre"]),
    ("Transversal", ["estado-del-encargo", "convenciones-dula"]),
]

DESCRIPCION = (
    "Auditoría de cuentas anuales españolas bajo NIA-ES, ciclo completo: estimación de "
    "honorarios, aceptación e independencia, materialidad, mapa de riesgos, ingesta y "
    "cuadres de la contabilidad de cualquier ERP, las doce áreas de trabajo de campo "
    "(inmovilizado, existencias, clientes e ingresos, proveedores, tesorería y "
    "financiación, arrendamientos, fondos propios y reservas, personal, fiscal, "
    "provisiones, subvenciones y partes vinculadas), comparador documental de cuentas "
    "anuales y memoria, evaluación de incorrecciones, informe conforme a la Resolución "
    "del ICAC de 22/01/2026 y revisión de calidad del archivo. Todo cálculo por script, "
    "con traza a fichero, hoja y celda, y reporte por excepción. Úsala al trabajar en una "
    "auditoría española: cuadrar un balance de sumas y saldos, recalcular leasings o "
    "amortizaciones, fijar la materialidad, seleccionar una muestra, cuadrar la memoria, "
    "redactar el informe o revisar el archivo antes de firmar."
)

LANZADOR = """#!/usr/bin/env bash
# Lanzador de la libreria de calculo de dula-audit para claude.ai.
#
#   bash bin/dula <subcomando> [argumentos]
#
# Se localiza a si mismo, asi que funciona desde cualquier directorio.
set -euo pipefail
origen="${BASH_SOURCE[0]}"
while [ -L "$origen" ]; do
  destino="$(readlink "$origen")"
  case "$destino" in
    /*) origen="$destino" ;;
    *)  origen="$(cd -P "$(dirname "$origen")" && pwd)/$destino" ;;
  esac
done
RAIZ="$(cd -P "$(dirname "$origen")/.." && pwd)"

PY=""
for cand in python3 python; do
  command -v "$cand" >/dev/null 2>&1 && PY="$cand" && break
done
[ -z "$PY" ] && { echo "ERROR: no se ha encontrado Python 3." >&2; exit 127; }

if ! "$PY" -c 'import pandas, openpyxl' 2>/dev/null; then
  echo "Faltan pandas u openpyxl. Instalandolas..." >&2
  "$PY" -m pip install --quiet pandas openpyxl >&2 || {
    echo "ERROR: no se han podido instalar. Ejecute: $PY -m pip install pandas openpyxl" >&2
    exit 127; }
fi

export PYTHONPATH="$RAIZ/scripts${PYTHONPATH:+:$PYTHONPATH}"
export DULA_RAIZ="$RAIZ"
exec "$PY" -m dula.cli "$@"
"""


def lee_skill(nombre: str) -> tuple[dict, str]:
    ruta = os.path.join(RAIZ, "skills", nombre, "SKILL.md")
    t = open(ruta, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", t, re.S)
    return yaml.safe_load(m.group(1)), m.group(2)


def construye_indice(metadatos: dict[str, dict]) -> str:
    # el frontmatter se serializa, no se concatena: las descripciones llevan dos
    # puntos y romperian el YAML si se escribieran a mano
    import io
    buf = io.StringIO()
    for k, v in (("name", NOMBRE),
                 ("description", DESCRIPCION),
                 ("license", "Propietaria - Dula Auditores"),
                 ("compatibility", "Requiere Python 3.10+ con pandas y openpyxl"),
                 ("metadata", {"version": "1.4.0", "autor": "Dula Auditores",
                               "marco": "NIA-ES; PGC y PGC PYMES; RICAC de 22/01/2026"})):
        yaml.safe_dump({k: v}, buf, allow_unicode=True, width=10**6,
                       default_flow_style=False, sort_keys=False)
    L = [
        "---",
        buf.getvalue().rstrip("\n"),
        "---",
        "",
        "# Auditoría de cuentas — Dula Auditores",
        "",
        "Equipo de auditoría senior para encargos españoles bajo NIA-ES. **Esta página es",
        "el índice**: abre solo el procedimiento que necesites, cuando lo necesites.",
        "",
        "## Cómo trabajar con esta skill",
        "",
        "1. **Localiza la carpeta de la skill** una sola vez por conversación:",
        "   ```bash",
        "   find / -name 'SKILL.md' -path '*dula-audit*' 2>/dev/null | head -1",
        "   ```",
        "   Llámala `$D` (el directorio que la contiene). Todo lo demás es relativo a ella.",
        "",
        "2. **Lee el procedimiento** que corresponda de la tabla de abajo:",
        "   ```bash",
        "   cat $D/procedimientos/<nombre>.md",
        "   ```",
        "",
        "3. **Ejecuta los cálculos** con la librería. Nunca calcules «a ojo»:",
        "   ```bash",
        "   bash $D/bin/dula doctor          # comprueba el entorno",
        "   bash $D/bin/dula <subcomando> --help",
        "   ```",
        "",
        "4. **Antes de nada, carga las convenciones del despacho**:",
        "   `cat $D/procedimientos/convenciones-dula.md` — lleva los umbrales, el índice de",
        "   papeles de trabajo, el marco normativo aplicado y las once reglas de",
        "   comportamiento que no se negocian.",
        "",
        "## Las once reglas que no se negocian",
        "",
        "1. **El script calcula, tú interpretas.** Todo cuadre, recálculo, amortización,",
        "   extrapolación de muestra o comparación numérica se ejecuta con la librería",
        "   Python. Ningún importe sale de una estimación mental.",
        "2. **Cero invención.** Ninguna cifra, fecha, cláusula o referencia normativa sin",
        "   origen verificable. Si falta un dato: `[PENDIENTE-CLIENTE]`. Si hace falta",
        "   criterio profesional: `[JUICIO-AUDITOR]`. Nunca se rellena en silencio.",
        "3. **Reporte por excepción.** Conclusión + excepciones + evidencia. Nunca volcados",
        "   masivos. Máximo 15 líneas en pantalla.",
        "4. **Proporcionalidad graduada.** El alcance lo fija el perfil calculado del",
        "   encargo (LIGERO / ESTÁNDAR / COMPLEJO), no una plantilla única.",
        "5. **Justificabilidad.** Cada decisión metodológica queda documentada para que un",
        "   revisor externo la reconstruya sin preguntar nada.",
        "6. **Autocontrol.** Ningún procedimiento cierra sin pasar su checklist final.",
        "7. **Asiste, no decide ni firma.** Toda conclusión es una propuesta sujeta a la",
        "   validación del auditor firmante.",
        "8. **Si la evidencia no basta, se dice.** Nunca se concluye igualmente.",
        "9. **Nunca se recorta el alcance por debajo de lo defendible.** Si el atajo no es",
        "   justificable, se dice y se propone la alternativa correcta con su coste.",
        "10. **Confidencialidad.** La documentación del cliente está sujeta a deber de",
        "    secreto (art. 31 LAC), a la normativa de blanqueo y al RGPD.",
        "11. **Deja constancia** de que el trabajo se ha realizado con asistencia de",
        "    herramientas automatizadas (NIGC1-ES).",
        "",
        "> La dirección, supervisión y revisión del encargo es responsabilidad",
        "> **indelegable** del socio firmante (NIA-ES 220 Revisada). Esta skill no la",
        "> sustituye: la hace viable en minutos.",
        "",
        "## Procedimientos disponibles",
        "",
        "Cada uno en `procedimientos/<nombre>.md`. Ábrelos de uno en uno.",
        "",
    ]
    for titulo, nombres in FASES:
        L += [f"### {titulo}", "", "| Procedimiento | Qué hace |", "|---|---|"]
        for n in nombres:
            if n not in metadatos:
                continue
            L.append(f"| `{n}` | {metadatos[n]['description']} |")
        L.append("")
    L += [
        "## Qué más hay en el paquete",
        "",
        "| Carpeta | Contenido |",
        "|---|---|",
        "| `scripts/dula/` | La librería de cálculo: ingesta, cuadres, materialidad, muestreo, leasings, financiación, amortizaciones, comparador, test de asientos y revisión de calidad |",
        "| `referencias/` | Mapeo del PGC a epígrafes, checklist de las 25 notas de memoria por modelo, catálogo de riesgos y los doce programas de trabajo por área |",
        "| `plantillas/` | Modelo de informe conforme a la RICAC de 22/01/2026, cartas de encargo y de manifestaciones, comunicaciones y solicitudes de confirmación |",
        "",
        "## Subcomandos de la librería",
        "",
        "```",
        "doctor       comprueba el entorno y la configuración",
        "nuevo        crea la carpeta y el estado del encargo",
        "estimar      perfil de complejidad, horas y honorarios",
        "ingesta      normaliza la contabilidad y ejecuta los cuadres  ← empieza por aquí",
        "materialidad materialidad global, de ejecución y específicas",
        "leasing      procesa el lote de contratos de arrendamiento",
        "financiacion cartera, confirmaciones bancarias y covenants",
        "amortizaciones  recálculo integral del inmovilizado",
        "reservas     reservas indisponibles y restringidas",
        "asientos     test de asientos del diario (NIA-ES 240)",
        "muestreo     MUS, atributos o dirigido, con semilla registrada",
        "analiticos   variaciones, ratios y expectativas",
        "comparar     comparador documental",
        "calidad      revisión del archivo y panel del socio",
        "estado       dónde está el encargo y cuál es el siguiente paso",
        "horas / pbc / validar   seguimiento del encargo y bitácora de uso de IA",
        "```",
        "",
        "## Primer uso",
        "",
        "Ejecuta `bash $D/bin/dula doctor`. Te dirá qué falta por configurar: los",
        "campos entre `«»` de `procedimientos/convenciones-dula.md` (números de ROAC,",
        "ruta base), las tarifas por categoría y los párrafos del modelo de informe",
        "pendientes de contrastar con el PDF oficial del ICAC.",
    ]
    return "\n".join(L) + "\n"


def valida(pkg: str) -> list[str]:
    """Comprueba el paquete contra la especificación Agent Skills."""
    errores = []
    ruta = os.path.join(pkg, "SKILL.md")
    t = open(ruta, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", t, re.S)
    if not m:
        return ["SKILL.md sin frontmatter"]
    try:
        fm = yaml.safe_load(m.group(1))
    except Exception as exc:  # noqa: BLE001
        return [f"frontmatter YAML invalido: {exc}"]

    sobrantes = set(fm) - CAMPOS_PERMITIDOS
    if sobrantes:
        errores.append(f"campos no admitidos fuera de Claude Code: {sorted(sobrantes)}")
    if not fm.get("name") or not fm.get("description"):
        errores.append("name y description son obligatorios")
    n = fm.get("name", "")
    if len(n) > MAX_NOMBRE:
        errores.append(f"name de {len(n)} caracteres (maximo {MAX_NOMBRE})")
    if not re.fullmatch(r"[a-z0-9-]+", n):
        errores.append(f"name '{n}' debe ser minusculas, numeros y guiones")
    if any(p in n.lower() for p in ("claude", "anthropic")):
        errores.append(f"name '{n}' contiene una palabra reservada")
    d = fm.get("description", "")
    if len(d) > MAX_DESCRIPCION:
        errores.append(f"description de {len(d)} caracteres (maximo {MAX_DESCRIPCION})")
    if "<" in d or "<" in n:
        errores.append("name/description no pueden contener etiquetas XML")
    cuerpo = len(m.group(2))
    if cuerpo > 20_000:
        errores.append(f"cuerpo de SKILL.md de {cuerpo} caracteres: pasa de ~5k tokens")
    for req in ("procedimientos", "referencias", "plantillas", "scripts"):
        if not os.path.isdir(os.path.join(pkg, req)):
            errores.append(f"falta la carpeta {req}/")
    if not os.path.exists(os.path.join(pkg, "scripts", "dula", "cli.py")):
        errores.append("falta la libreria en scripts/dula/")
    return errores


def main() -> int:
    if os.path.isdir(DESTINO):
        shutil.rmtree(DESTINO)
    pkg = os.path.join(DESTINO, NOMBRE)
    os.makedirs(os.path.join(pkg, "procedimientos"))

    # 1. procedimientos = cuerpos de las skills, sin frontmatter de Claude Code
    metadatos: dict[str, dict] = {}
    for ruta in sorted(glob.glob(os.path.join(RAIZ, "skills", "*", "SKILL.md"))):
        nombre = os.path.basename(os.path.dirname(ruta))
        fm, cuerpo = lee_skill(nombre)
        metadatos[nombre] = fm
        cabecera = [f"# {nombre}", "", f"> {fm['description']}"]
        if fm.get("when_to_use"):
            cabecera += ["", f"> **Cuándo:** {fm['when_to_use']}"]
        if fm.get("argument-hint"):
            cabecera += ["", f"> **Necesita:** `{fm['argument-hint']}`"]
        cabecera += ["", "---", ""]
        # se quita el H1 original del cuerpo para no duplicar titulo
        cuerpo = re.sub(r"^# .*?\n", "", cuerpo.lstrip(), count=1)
        with open(os.path.join(pkg, "procedimientos", f"{nombre}.md"),
                  "w", encoding="utf-8") as fh:
            fh.write("\n".join(cabecera) + cuerpo)

    faltan = {n for _, ns in FASES for n in ns} ^ set(metadatos)
    if faltan:
        print(f"ERROR: procedimientos sin clasificar en el indice: {sorted(faltan)}")
        return 1

    # 2. indice
    with open(os.path.join(pkg, "SKILL.md"), "w", encoding="utf-8") as fh:
        fh.write(construye_indice(metadatos))

    # 3. librería, referencias y plantillas
    shutil.copytree(os.path.join(RAIZ, "shared", "scripts"), os.path.join(pkg, "scripts"))
    shutil.copytree(os.path.join(RAIZ, "shared", "references"),
                    os.path.join(pkg, "referencias"))
    shutil.copytree(os.path.join(RAIZ, "shared", "templates"),
                    os.path.join(pkg, "plantillas"))
    for basura in glob.glob(os.path.join(pkg, "scripts", "**", "__pycache__"),
                            recursive=True):
        shutil.rmtree(basura, ignore_errors=True)

    # el lanzador no puede llamarse igual que el paquete python `dula/`
    os.makedirs(os.path.join(pkg, "bin"), exist_ok=True)
    lanz = os.path.join(pkg, "bin", "dula")
    with open(lanz, "w", encoding="utf-8") as fh:
        fh.write(LANZADOR)
    os.chmod(lanz, 0o755)

    # 4. validacion contra la especificacion
    errores = valida(pkg)
    if errores:
        print("PAQUETE INVALIDO:")
        for e in errores:
            print("  -", e)
        return 1

    # 5. zip con la carpeta de la skill en la raiz
    zpath = os.path.join(DESTINO, f"{NOMBRE}-claude-ai.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for base, _, ficheros in os.walk(pkg):
            for f in ficheros:
                completo = os.path.join(base, f)
                z.write(completo, os.path.relpath(completo, DESTINO))

    tam = os.path.getsize(zpath) / 1024
    n_proc = len(glob.glob(os.path.join(pkg, "procedimientos", "*.md")))
    print(f"Paquete para claude.ai: {zpath}")
    print(f"  {n_proc} procedimientos, {tam:,.0f} KB")
    print(f"  frontmatter: solo los campos de la especificacion Agent Skills")
    print(f"  cuerpo de SKILL.md: {os.path.getsize(os.path.join(pkg, 'SKILL.md')):,} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
