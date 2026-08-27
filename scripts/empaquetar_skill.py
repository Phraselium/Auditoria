#!/usr/bin/env python3
"""Construye el paquete .zip de auditoria-nia-es para claude.ai.

claude.ai no admite plugins: admite SKILLS SUELTAS en .zip, subidas desde
Ajustes. Y su frontmatter solo acepta los seis campos de la especificacion
Agent Skills (name, description, license, compatibility, metadata,
allowed-tools). Los campos `when_to_use`, `argument-hint` y `user-invocable`
que usa Claude Code producirian el error:

    Unexpected key(s) in SKILL.md frontmatter: argument-hint.

Por eso no se puede subir el plugin tal cual. Este script GENERA el paquete a
partir del plugin, de modo que ambos salen siempre de la misma fuente y no se
desincronizan:

  - Las 10 skills del plugin y los ficheros de `procedimientos/` se
    consolidan en el `procedimientos/` del paquete, que Claude lee solo cuando los
    necesita (divulgacion progresiva). Su coste en contexto es cero hasta que se
    abren.
  - Un unico SKILL.md hace de indice: dice que hay y cuando usar cada cosa.
  - La libreria Python y las referencias viajan enteras.

    python3 scripts/empaquetar_skill.py
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
DESTINO = os.path.join(RAIZ, "dist")
NOMBRE = "auditoria-nia-es"

# Limites de la especificacion Agent Skills
MAX_NOMBRE = 64
MAX_DESCRIPCION = 1024
CAMPOS_PERMITIDOS = {"name", "description", "license", "compatibility",
                     "metadata", "allowed-tools"}

# Orden en que se presentan los procedimientos en el indice. Los marcados como
# GUIA son los diez que en Claude Code son skills: hacen de puerta de entrada de
# su fase y remiten al procedimiento concreto.
GUIAS = {"convenciones-despacho", "ingesta-y-cuadres", "comparador-documental",
         "redaccion-informe", "revision-de-calidad", "areas-de-campo",
         "planificacion", "cierre-del-encargo", "estimacion-y-aceptacion",
         "tecnicas-de-prueba"}

FASES = [
    ("Fase 0 — Captación y aceptación", [
        "estimacion-y-aceptacion", "estimacion-encargo",
        "aceptacion-e-independencia", "escalado-del-encargo"]),
    ("Fase 1 — Planificación", [
        "planificacion", "entendimiento-entidad", "materialidad",
        "mapa-de-riesgos", "diseno-de-pruebas", "plan-y-solicitud-informacion"]),
    ("Fase 2 — Trabajo de campo (transversales)", [
        "convenciones-despacho", "ingesta-y-cuadres", "comparador-documental",
        "tecnicas-de-prueba", "muestreo", "analiticos", "test-asientos-diario"]),
    ("Fase 2 — Áreas", [
        "areas-de-campo",
        "area-inmovilizado", "area-existencias", "area-clientes-e-ingresos",
        "area-proveedores-y-compras", "area-tesoreria-y-financiacion",
        "area-arrendamientos", "area-fondos-propios-y-reservas", "area-personal",
        "area-fiscal", "area-provisiones-y-contingencias", "area-subvenciones",
        "area-partes-vinculadas", "saldos-apertura"]),
    ("Fase 3 — Cierre e informe", [
        "cierre-del-encargo", "hechos-posteriores-y-empresa-en-funcionamiento",
        "evaluacion-de-incorrecciones", "comunicaciones-y-manifestaciones",
        "archivo-y-cierre", "redaccion-informe"]),
    ("Transversal — seguimiento y revisión", [
        "revision-de-calidad", "estado-del-encargo"]),
]

# En claude.ai no existe CLAUDE_PLUGIN_ROOT ni el lanzador `audita` en el PATH:
# todo cuelga de la carpeta de la skill y las rutas quedan relativas a ella.
SUSTITUCIONES = [
    ('"${CLAUDE_PLUGIN_ROOT}"/', ""),
    ("${CLAUDE_PLUGIN_ROOT:-.}/", ""),
    ("${CLAUDE_PLUGIN_ROOT}/", ""),
    ("$CLAUDE_PLUGIN_ROOT/", ""),
]

DESCRIPCION = (
    "Auditoría de cuentas anuales españolas bajo NIA-ES para despacho profesional. "
    "Cuadres de la contabilidad de cualquier ERP, materialidad, mapa de riesgos, "
    "muestreo, las doce áreas de trabajo de campo, recálculo de leasings y de "
    "financiación, comparador de cuentas anuales y memoria, informe y revisión de "
    "calidad del archivo. Úsala para cualquier trabajo de auditoría española: cuadrar "
    "un balance de sumas y saldos, fijar la materialidad, seleccionar una muestra, "
    "recalcular arrendamientos, redactar el informe o revisar el archivo antes de firmar."
)

ENTRADA = '''#!/usr/bin/env python3
"""Punto de entrada de la libreria de calculo de auditoria-nia-es.

    python3 audita.py <subcomando> [argumentos]
    python3 audita.py doctor

Es Python plano, sin bit de ejecucion y sin instalar nada: el paquete no lleva
ningun script de shell ejecutable, para no disparar los controles de seguridad
de la plataforma.
"""
import os
import sys

RAIZ = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(RAIZ, "scripts"))
os.environ.setdefault("AUDITA_RAIZ", RAIZ)

try:
    import pandas  # noqa: F401
    import openpyxl  # noqa: F401
except ImportError as exc:
    print(f"Falta una dependencia de Python: {exc.name}.\n"
          f"El plugin necesita dos paquetes de PyPI, pandas y openpyxl.\n"
          f"Instalelos en este interprete: {sys.executable}", file=sys.stderr)
    raise SystemExit(127)

from audita.cli import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
'''


def lee_skill(ruta: str) -> tuple[dict, str]:
    """Devuelve (metadatos, cuerpo) de una skill de Claude Code."""
    t = open(ruta, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", t, re.S)
    if not m:
        raise ValueError(f"{ruta}: sin frontmatter")
    return yaml.safe_load(m.group(1)), m.group(2)


def lee_procedimiento(ruta: str) -> tuple[dict, str]:
    """Los procedimientos de `procedimientos/` ya llevan su cabecera en
    prosa: `# nombre`, luego `> descripción` y opcionalmente `> **Cuándo:**`."""
    t = open(ruta, encoding="utf-8").read()
    m = re.search(r"^> (?!\*\*)(.+)$", t, re.M)
    if not m:
        raise ValueError(f"{ruta}: sin línea de descripción")
    return {"description": m.group(1).strip(), "_ya_tiene_cabecera": True}, t


def reescribe_rutas(texto: str) -> str:
    for viejo, nuevo in SUSTITUCIONES:
        texto = texto.replace(viejo, nuevo)
    # el lanzador `audita` no está en el PATH de claude.ai
    return re.sub(r"(?m)^(\s*)audita ", r"\1python3 audita.py ", texto)


def construye_indice(metadatos: dict[str, dict]) -> str:
    # el frontmatter se serializa, no se concatena: las descripciones llevan dos
    # puntos y romperian el YAML si se escribieran a mano
    # SOLO name y description. `license` y `compatibility` admiten unicamente
    # valores normalizados (SPDX / mapa de versiones); con texto libre el
    # validador de claude.ai rechaza la subida ("no se ha podido sincronizar").
    # Todo lo demas va al cuerpo, donde no lo valida nadie.
    import io
    buf = io.StringIO()
    for k, v in (("name", NOMBRE), ("description", DESCRIPCION),
                 ("license", "MIT")):
        yaml.safe_dump({k: v}, buf, allow_unicode=True, width=10**6,
                       default_flow_style=False, sort_keys=False)
    L = [
        "---",
        buf.getvalue().rstrip("\n"),
        "---",
        "",
        "# Auditoría de cuentas anuales — NIA-ES",
        "",
        "Conocimiento y herramientas para auditar cuentas anuales españolas bajo NIA-ES.",
        "Todas las rutas de este documento son **relativas a la carpeta de esta skill**.",
        "",
        "## Cómo usar esta skill",
        "",
        "1. **Lee siempre primero** `procedimientos/convenciones-despacho.md`. Son las",
        "   reglas de trabajo: qué se calcula por script y qué no, la prohibición de",
        "   inventar cifras, los umbrales del despacho y el índice de papeles.",
        "2. **Abre el procedimiento** de la tabla de abajo que corresponda, y solo ese:",
        "   `cat procedimientos/<nombre>.md`.",
        "3. **Calcula con la librería**, nunca a ojo: `python3 audita.py <subcomando>`.",
        "   Empieza por `python3 audita.py doctor` para ver qué falta por configurar.",
        "",
        "## Las cinco reglas que no se negocian",
        "",
        "1. **El script calcula, tú interpretas.** Ningún importe sale de una estimación",
        "   mental: todo cuadre, recálculo y extrapolación se ejecuta en Python.",
        "2. **Cero invención.** Falta un dato → `[PENDIENTE-CLIENTE]`. Hace falta criterio",
        "   → `[JUICIO-AUDITOR]`. Nunca se rellena en silencio.",
        "3. **Reporte por excepción.** Conclusión, excepciones y evidencia. Máximo 15",
        "   líneas en pantalla; el detalle va al papel de trabajo.",
        "4. **Asiste, no decide ni firma.** Toda conclusión es una propuesta sujeta a la",
        "   validación del auditor firmante. Si la evidencia no basta, se dice.",
        "5. **Confidencialidad.** La documentación del cliente está sujeta al deber de",
        "   secreto (art. 31 LAC), a la normativa de blanqueo y al RGPD.",
        "",
        "Las once completas, con su fundamento normativo, en",
        "`procedimientos/convenciones-despacho.md`.",
        "",
        "## Procedimientos",
        "",
        "Uno por fichero en `procedimientos/`. Los marcados **▸** son guías de fase:",
        "ábrelas primero y te dicen cuál de su fase toca y en qué orden.",
        "",
    ]
    for titulo, nombres in FASES:
        presentes = [n for n in nombres if n in metadatos]
        if not presentes:
            continue
        L.append(f"**{titulo}**")
        L.append("")
        L.append("  " + " · ".join(
            (f"**▸ {n}**" if n in GUIAS else f"`{n}`") for n in presentes))
        L.append("")
    L += [
        "El catálogo con una línea de descripción por procedimiento está en",
        "`procedimientos/00-catalogo.md`.",
        "",
        "## Qué más hay",
        "",
        "| Carpeta | Contenido |",
        "|---|---|",
        "| `scripts/audita/` | Librería de cálculo: ingesta, cuadres, materialidad, muestreo, leasings, financiación, amortizaciones, comparador y calidad |",
        "| `referencias/` | Mapeo del PGC, desgloses de memoria, catálogo de riesgos y los doce programas por área |",
        "| `plantillas/` | Informe conforme a la RICAC de 22/01/2026, cartas y comunicaciones |",
        "",
        "## Subcomandos",
        "",
        "```",
        "doctor  nuevo  estimar  ingesta  materialidad  leasing  financiacion",
        "amortizaciones  reservas  asientos  muestreo  analiticos  comparar",
        "calidad  estado  horas  pbc  validar",
        "```",
        "",
        "`ingesta` es la puerta de entrada: sin la contabilidad cuadrada no se trabaja",
        "ninguna área. `python3 audita.py <subcomando> --help` para cada uno.",
        "",
        "> La dirección, supervisión y revisión del encargo es responsabilidad",
        "> **indelegable** del socio firmante (NIA-ES 220 Revisada).",
    ]
    return "\n".join(L) + "\n"


def construye_catalogo(metadatos: dict[str, dict]) -> str:
    """El catalogo anotado, fuera del SKILL.md.

    El indice se carga en cada conversacion; este fichero solo cuando alguien
    pregunta que hay. Sacarlo de ahi baja el coste fijo a la mitad.
    """
    L = ["# Catálogo de procedimientos", "",
         "Qué hace cada uno. Ábrelos con `cat procedimientos/<nombre>.md`.",
         "Los marcados **▸** son guías de fase.", ""]
    for titulo, nombres in FASES:
        presentes = [n for n in nombres if n in metadatos]
        if not presentes:
            continue
        L += [f"## {titulo}", "", "| Procedimiento | Qué hace |", "|---|---|"]
        for n in presentes:
            marca = "▸ " if n in GUIAS else ""
            L.append(f"| {marca}`{n}` | {metadatos[n]['description']} |")
        L.append("")
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
    # reglas de quick_validate.py que no son evidentes en la especificacion
    if n.startswith("-") or n.endswith("-") or "--" in n:
        errores.append(f"name '{n}' no puede empezar o acabar en guion, ni llevar dos seguidos")
    if len(fm.get("compatibility", "")) > 500:
        errores.append("compatibility pasa de 500 caracteres")
    if any(p in n.lower() for p in ("claude", "anthropic")):
        errores.append(f"name '{n}' contiene una palabra reservada")
    d = fm.get("description", "")
    if len(d) > MAX_DESCRIPCION:
        errores.append(f"description de {len(d)} caracteres (maximo {MAX_DESCRIPCION})")
    if any(c in d or c in n for c in "<>"):
        errores.append("name/description no pueden contener < ni >")
    cuerpo = len(m.group(2))
    if cuerpo > 8_000:
        errores.append(f"cuerpo de SKILL.md de {cuerpo} caracteres. Es lo unico que "
                       f"se carga siempre: mantengalo por debajo de 8.000 y mueva el "
                       f"detalle a procedimientos/")
    for req in ("procedimientos", "referencias", "plantillas", "scripts"):
        if not os.path.isdir(os.path.join(pkg, req)):
            errores.append(f"falta la carpeta {req}/")
    if not os.path.exists(os.path.join(pkg, "scripts", "audita", "cli.py")):
        errores.append("falta la libreria en scripts/audita/")
    if not os.path.exists(os.path.join(pkg, "audita.py")):
        errores.append("falta el punto de entrada audita.py")
    # ningun ejecutable ni script de shell: los controles de seguridad de la
    # plataforma rechazan paquetes que traen binarios o instalan dependencias
    for base, _, ficheros in os.walk(pkg):
        for f in ficheros:
            ruta = os.path.join(base, f)
            rel = os.path.relpath(ruta, pkg)
            if os.stat(ruta).st_mode & 0o111:
                errores.append(f"{rel} tiene bit de ejecucion")
            if f.endswith((".sh", ".bash", ".exe", ".bat", ".dll", ".so")):
                errores.append(f"{rel} es un ejecutable o script de shell")
            if rel.endswith(".py") or rel.endswith(".md"):
                texto = open(ruta, encoding="utf-8", errors="ignore").read()
                if "pip install" in texto:
                    errores.append(f"{rel} contiene una orden de instalacion "
                                   f"de dependencias")
    return errores


def main() -> int:
    if os.path.isdir(DESTINO):
        shutil.rmtree(DESTINO)
    pkg = os.path.join(DESTINO, NOMBRE)
    os.makedirs(os.path.join(pkg, "procedimientos"))

    # 1. procedimientos: las diez skills (sin su frontmatter de Claude Code, que
    #    claude.ai rechaza) mas los procedimientos de procedimientos/
    fuentes = [(os.path.basename(os.path.dirname(r)), r, lee_skill)
               for r in sorted(glob.glob(os.path.join(RAIZ, "skills", "*", "SKILL.md")))]
    fuentes += [(os.path.splitext(os.path.basename(r))[0], r, lee_procedimiento)
                for r in sorted(glob.glob(
                    os.path.join(RAIZ, "procedimientos", "*.md")))]

    metadatos: dict[str, dict] = {}
    for nombre, ruta, lector in fuentes:
        if nombre in metadatos:
            print(f"ERROR: '{nombre}' esta duplicado entre skills y procedimientos")
            return 1
        fm, cuerpo = lector(ruta)
        metadatos[nombre] = fm
        if fm.get("_ya_tiene_cabecera"):
            texto = cuerpo
        else:
            cabecera = [f"# {nombre}", "", f"> {fm['description']}"]
            if fm.get("when_to_use"):
                cabecera += ["", f"> **Cuándo:** {fm['when_to_use']}"]
            if fm.get("argument-hint"):
                cabecera += ["", f"> **Necesita:** `{fm['argument-hint']}`"]
            cabecera += ["", "---", ""]
            # se quita el H1 original del cuerpo para no duplicar titulo
            texto = "\n".join(cabecera) + re.sub(r"^# .*?\n", "", cuerpo.lstrip(), count=1)
        with open(os.path.join(pkg, "procedimientos", f"{nombre}.md"),
                  "w", encoding="utf-8") as fh:
            fh.write(reescribe_rutas(texto))

    faltan = {n for _, ns in FASES for n in ns} ^ set(metadatos)
    if faltan:
        print(f"ERROR: procedimientos sin clasificar en el indice: {sorted(faltan)}")
        return 1

    # 2. indice, y el catalogo anotado como fichero aparte para que el
    #    SKILL.md quede corto: es lo que se carga siempre, y cada byte cuenta
    with open(os.path.join(pkg, "SKILL.md"), "w", encoding="utf-8") as fh:
        fh.write(construye_indice(metadatos))
    with open(os.path.join(pkg, "procedimientos", "00-catalogo.md"),
              "w", encoding="utf-8") as fh:
        fh.write(construye_catalogo(metadatos))

    # 3. librería, referencias y plantillas
    # SOLO la libreria de calculo. Ni el empaquetador ni el verificador de
    # privacidad tienen sentido dentro del paquete: son herramientas del
    # repositorio, no del encargo. Y son justo la clase de fichero que un
    # analisis automatico mira con lupa —uno escribe ficheros y menciona
    # `pip install`, el otro busca NIF, IBAN y correos— sin aportar nada aqui.
    shutil.copytree(os.path.join(RAIZ, "scripts", "audita"),
                    os.path.join(pkg, "scripts", "audita"))
    shutil.copytree(os.path.join(RAIZ, "referencias"),
                    os.path.join(pkg, "referencias"))
    shutil.copytree(os.path.join(RAIZ, "plantillas"),
                    os.path.join(pkg, "plantillas"))
    for basura in glob.glob(os.path.join(pkg, "scripts", "**", "__pycache__"),
                            recursive=True):
        shutil.rmtree(basura, ignore_errors=True)

    # punto de entrada Python plano en la raiz de la skill: ni shell ni bit de
    # ejecucion, para no disparar los controles de seguridad de la plataforma
    entrada = os.path.join(pkg, "audita.py")
    with open(entrada, "w", encoding="utf-8") as fh:
        fh.write(ENTRADA)
    os.chmod(entrada, 0o644)

    # 4. validacion contra la especificacion
    errores = valida(pkg)
    if errores:
        print("PAQUETE INVALIDO:")
        for e in errores:
            print("  -", e)
        return 1

    # 5. El empaquetado replica exactamente el de `package_skill.py` de
    #    anthropics/skills, que es el empaquetador canonico:
    #      - la carpeta de la skill va en la raiz del archivo (arcname relativo
    #        al PADRE de la carpeta), no su contenido suelto;
    #      - la extension es .skill, no .zip;
    #      - se excluyen __pycache__, node_modules, *.pyc y .DS_Store.
    #    Se genera ademas la copia .zip porque la pantalla de subida de
    #    claude.ai documenta esa extension: mismo contenido, dos nombres.
    def escribe(destino: str) -> None:
        with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as z:
            for base, dirs, ficheros in os.walk(pkg):
                dirs[:] = [d for d in dirs if d not in ("__pycache__", "node_modules")]
                for f in sorted(ficheros):
                    if f.endswith(".pyc") or f == ".DS_Store":
                        continue
                    completo = os.path.join(base, f)
                    z.write(completo, os.path.relpath(completo, DESTINO))

    skpath = os.path.join(DESTINO, f"{NOMBRE}.skill")
    zpath = os.path.join(DESTINO, f"{NOMBRE}.zip")
    escribe(skpath)
    escribe(zpath)

    n_proc = len(glob.glob(os.path.join(pkg, "procedimientos", "*.md")))
    print(f"Paquete para claude.ai: {skpath}")
    print(f"  y la misma carpeta como .zip:  {zpath}")
    print(f"  {n_proc} procedimientos, {os.path.getsize(skpath) / 1024:,.0f} KB")
    print(f"  disposicion y exclusiones identicas a package_skill.py")
    print(f"  cuerpo de SKILL.md: {os.path.getsize(os.path.join(pkg, 'SKILL.md')):,} bytes")

    # 6. paquete minimo de diagnostico: solo SKILL.md y los procedimientos.
    #    Si el completo no sube y este si, el problema esta en la libreria
    #    Python o en las referencias, no en la skill.
    zmin = os.path.join(DESTINO, f"{NOMBRE}-minimo.skill")
    with zipfile.ZipFile(zmin, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(f"{NOMBRE}/SKILL.md",
                   open(os.path.join(pkg, "SKILL.md"), encoding="utf-8").read())
        for f in sorted(glob.glob(os.path.join(pkg, "procedimientos", "*.md"))):
            z.write(f, os.path.join(NOMBRE, "procedimientos", os.path.basename(f)))
    print(f"Paquete minimo de diagnostico: {zmin}")
    print(f"  sin libreria ni referencias, {os.path.getsize(zmin) / 1024:,.0f} KB")

    construye_claude_code()
    return 0


# --- Claude Code: paquete para el directorio de skills -----------------------

EXCLUIDOS = ("dist", "__pycache__", os.path.join("tests", "fixtures"),
             os.path.join("tests", "salida"), ".git", ".claude", "encargos",
             "clientes", "salidas", "datos")


def construye_claude_code() -> None:
    """Zip del plugin tal cual, para descomprimir en `~/.claude/skills/`.

    Claude Code carga solo lo que hay ahi, sin marketplace, sin git y sin red.
    Es la via que no depende de que la sincronizacion del marketplace funcione.
    """
    zpath = os.path.join(DESTINO, f"{NOMBRE}-claude-code.zip")
    n = 0
    EXCLUIDOS_DIR = ("dist", "__pycache__", ".git", ".claude")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for base, dirs, ficheros in os.walk(RAIZ):
            rel_dir = os.path.relpath(base, RAIZ)
            if any(rel_dir == e or rel_dir.startswith(e + os.sep) for e in EXCLUIDOS):
                dirs[:] = []
                continue
            dirs[:] = [d for d in dirs if d not in EXCLUIDOS_DIR]
            for f in ficheros:
                if f.endswith(".pyc"):
                    continue
                completo = os.path.join(base, f)
                rel = os.path.relpath(completo, RAIZ)
                info = zipfile.ZipInfo(os.path.join(NOMBRE, rel).replace(os.sep, "/"))
                info.compress_type = zipfile.ZIP_DEFLATED
                # el lanzador `bin/audita` necesita conservar el bit de ejecucion
                modo = 0o755 if rel == os.path.join("bin", "audita") else 0o644
                info.external_attr = modo << 16
                z.writestr(info, open(completo, "rb").read())
                n += 1
    print(f"Paquete para Claude Code: {zpath}")
    print(f"  {n} ficheros, {os.path.getsize(zpath) / 1024:,.0f} KB")
    print(f"  se descomprime en ~/.claude/skills/ y carga sin marketplace")


if __name__ == "__main__":
    sys.exit(main())
