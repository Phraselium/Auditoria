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

    python3 tools/construir_paquetes.py
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

# El paquete de claude.ai no tiene ${CLAUDE_PLUGIN_ROOT} ni el lanzador `audita`
# en el PATH: las rutas se reescriben al montar el paquete.
SUSTITUCIONES = [
    ("${CLAUDE_PLUGIN_ROOT}/procedimientos", "$D/procedimientos"),
    ("${CLAUDE_PLUGIN_ROOT}/referencias", "$D/referencias"),
    ("${CLAUDE_PLUGIN_ROOT}/plantillas", "$D/plantillas"),
    ("${CLAUDE_PLUGIN_ROOT}/scripts", "$D/scripts"),
    ("${CLAUDE_PLUGIN_ROOT}", "$D"),
    ("procedimientos/", "$D/procedimientos/"),
    ("referencias/", "$D/referencias/"),
    ("plantillas/", "$D/plantillas/"),
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
          f"Instalela con:  {sys.executable} -m pip install pandas openpyxl\n"
          f"Son las dos unicas que necesita el plugin.", file=sys.stderr)
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
    return re.sub(r"(?m)^(\s*)audita ", r"\1python3 $D/audita.py ", texto)


def construye_indice(metadatos: dict[str, dict]) -> str:
    # el frontmatter se serializa, no se concatena: las descripciones llevan dos
    # puntos y romperian el YAML si se escribieran a mano
    # SOLO name y description. `license` y `compatibility` admiten unicamente
    # valores normalizados (SPDX / mapa de versiones); con texto libre el
    # validador de claude.ai rechaza la subida ("no se ha podido sincronizar").
    # Todo lo demas va al cuerpo, donde no lo valida nadie.
    import io
    buf = io.StringIO()
    for k, v in (("name", NOMBRE), ("description", DESCRIPCION)):
        yaml.safe_dump({k: v}, buf, allow_unicode=True, width=10**6,
                       default_flow_style=False, sort_keys=False)
    L = [
        "---",
        buf.getvalue().rstrip("\n"),
        "---",
        "",
        "# Auditoría de cuentas — NIA-ES",
        "",
        "Equipo de auditoría senior para encargos españoles bajo NIA-ES. **Esta página es",
        "el índice**: abre solo el procedimiento que necesites, cuando lo necesites.",
        "",
        "Versión 1.6.0 · Marco: NIA-ES; PGC y PGC PYMES; RICAC de",
        "22/01/2026 · Requiere Python 3.10+ con `pandas` y `openpyxl`.",
        "",
        "## Cómo trabajar con esta skill",
        "",
        "1. **Localiza la carpeta de la skill** una sola vez por conversación:",
        "   ```bash",
        "   find / -name 'SKILL.md' -path '*auditoria-nia-es*' 2>/dev/null | head -1",
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
        "   python3 $D/audita.py doctor          # comprueba el entorno",
        "   python3 $D/audita.py <subcomando> --help",
        "   ```",
        "",
        "4. **Antes de nada, carga las convenciones del despacho**:",
        "   `cat $D/procedimientos/convenciones-despacho.md` — lleva los umbrales, el índice de",
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
            marca = "**▸**" if n in GUIAS else ""
            L.append(f"| {marca} `{n}` | {metadatos[n]['description']} |".replace("|  `", "| `"))
        L.append("")
    L += [
        "**▸** marca las **guías de fase**: ábrelas primero, te dicen qué",
        "procedimiento de su fase corresponde y en qué orden.",
        "",
    ]
    L += [
        "## Qué más hay en el paquete",
        "",
        "| Carpeta | Contenido |",
        "|---|---|",
        "| `scripts/audita/` | La librería de cálculo: ingesta, cuadres, materialidad, muestreo, leasings, financiación, amortizaciones, comparador, test de asientos y revisión de calidad |",
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
        "Ejecuta `python3 $D/audita.py doctor`. Te dirá qué falta por configurar: los",
        "campos entre `«»` de `procedimientos/convenciones-despacho.md` (números de ROAC,",
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
    if cuerpo > 20_000:
        errores.append(f"cuerpo de SKILL.md de {cuerpo} caracteres: pasa de ~5k tokens")
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
                if "pip install" in texto and "Instalela con" not in texto \
                        and "pip install pandas openpyxl" not in texto:
                    errores.append(f"{rel} ejecuta pip install")
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

    # 2. indice
    with open(os.path.join(pkg, "SKILL.md"), "w", encoding="utf-8") as fh:
        fh.write(construye_indice(metadatos))

    # 3. librería, referencias y plantillas
    shutil.copytree(os.path.join(RAIZ, "scripts"), os.path.join(pkg, "scripts"))
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
