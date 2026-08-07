# dula-audit

Equipo de auditoría senior virtual para **Dula Auditores**. Cubre el ciclo
completo del encargo —aceptación, planificación, trabajo de campo, cierre e
informe— bajo NIA-ES, con cálculo determinista por script, trazabilidad total y
reporte por excepción.

**Estado:** v1.5.0 · 10 skills · 29 procedimientos · 1 comando · 3 agentes ·
23 módulos Python · **273/273 comprobaciones superadas · 100 % de cobertura de
la librería**.

---

## Qué resuelve

El despacho trabaja con Excel, Data Sniper y revisión visual. El cuello de botella
no es el criterio profesional: es el tiempo que se va en comparar, cuadrar y
recalcular a mano, y la imposibilidad de que el socio revise en detalle todo lo
que firma.

Este plugin ataca las dos cosas:

| Antes | Con el plugin |
|---|---|
| ~100 contratos de leasing recalculados a mano: **3 días** | Recálculo del 100 % + cuadro de vencimientos + conciliación: **unas horas**, con las excepciones aisladas |
| Cuadrar memoria contra balance leyendo cuadros | Comparación sistemática que reporta **solo las diferencias**, con importe, origen y causa probable |
| El socio revisa lo que le da tiempo | **Panel del socio** de una página con las 10-20 cuestiones que exigen su juicio; todo lo demás cuadrado y evidenciado |
| Las excepciones aparecen el último día | **Modo pre-vuelo** ejecutable durante toda la campaña |
| El precio se fija a ojo | Perfil de complejidad puntuado, horas por área y categoría, punto muerto y **qué pedir al cliente para abaratar** |

---

## Principios de diseño

1. **Determinismo.** Todo cuadre, recálculo, amortización, extrapolación o
   comparación numérica se ejecuta por script Python. El modelo interpreta, decide
   y redacta; **el script calcula**.
2. **Cero invención.** Ninguna cifra sin traza a `fichero!hoja!celda` o a
   `documento!página!cláusula`. Lo que falta es `[PENDIENTE-CLIENTE]`; lo que
   requiere criterio es `[JUICIO-AUDITOR]`. Nunca se rellena en silencio.
3. **Reporte por excepción.** Conclusión + excepciones + evidencia. Máximo 15
   líneas en pantalla.
4. **Proporcionalidad graduada.** Tres perfiles calculados, no una plantilla única.
5. **Justificabilidad.** Cada decisión metodológica queda documentada para que un
   revisor externo la reconstruya sin preguntar nada.
6. **Autocontrol.** Ninguna skill cierra sin pasar su checklist de
   autoverificación.
7. **Trazabilidad del uso de IA.** Toda ejecución asistida queda registrada en
   `uso-ia.log` con sus entradas (y su huella SHA-256), sus salidas y **quién
   validó el resultado**. `revision-de-calidad` reporta como excepción toda
   ejecución sin validar cuyo resultado se haya incorporado a un papel
   concluido (NIGC1-ES; ISO/IEC 42001).

> **El plugin asiste, no decide ni firma.** La dirección, supervisión y revisión
> del encargo es responsabilidad **indelegable** del socio firmante (NIA-ES 220
> Revisada). Lo que hace el plugin es hacerla viable en minutos.

---

## Instalación

Hay **dos productos distintos**, porque Claude Code y claude.ai no admiten lo
mismo. El de claude.ai se genera desde el mismo código, así que no divergen.

| | Claude Code | claude.ai (web y escritorio) |
|---|---|---|
| Formato | Plugin (`/plugin install`) | Skill suelta en `.zip`, subida desde Ajustes |
| Componentes | 10 skills + 1 comando + 3 agentes | 1 skill con 39 procedimientos que se abren bajo demanda |
| Menú `/` | Sí, con descripción y argumentos | No: Claude la activa sola por el contexto |
| Requisito | — | Plan Pro, Max, Team o Enterprise **con ejecución de código activada** |
| Ámbito | Personal o de proyecto | Personal: cada persona la sube por su cuenta |

---

## A) Claude Code

### Opción A — descomprimir en el directorio de skills (recomendada)

**No usa marketplace, ni git, ni red.** Claude Code carga lo que encuentre en
`~/.claude/skills/`, así que no hay sincronización que pueda fallar.

1. Descargue **`build/dula-audit-claude-code.zip`** (299 KB) del repositorio.
2. Descomprímalo dentro de `~/.claude/skills/`:

```bash
mkdir -p ~/.claude/skills
unzip -o ~/Descargas/dula-audit-claude-code.zip -d ~/.claude/skills/
```

En Windows: descomprima en `C:\Users\<usuario>\.claude\skills\`, de modo que
quede `…\.claude\skills\dula-audit\.claude-plugin\plugin.json`.

3. Reinicie Claude Code y compruébelo:

```bash
claude plugin list      # debe decir dula-audit@skills-dir · 1.5.0 · loaded
```

**Para actualizar:** borre la carpeta y vuelva a descomprimir. No hay caché
intermedia que limpiar.

> Si ya tenía el plugin instalado por marketplace, desinstálelo primero
> (`/plugin uninstall dula-audit@dula`): la copia instalada tiene precedencia y
> la del directorio de skills no llegaría a cargarse.

### Opción B — desde el marketplace

```
/plugin marketplace add Phraselium/Auditoria
/plugin install dula-audit@dula
```

Si el resumen de instalación dice `Run /reload-plugins to activate`, ejecútalo.

**Si falla con un error de sincronización**, pruebe con la URL completa en lugar
de la forma abreviada `owner/repo`, que tiene que resolver el branch por defecto:

```
/plugin marketplace remove dula
/plugin marketplace add https://github.com/Phraselium/Auditoria.git
/plugin install dula-audit@dula
```

Y si tampoco, use la **opción A**: no depende del marketplace en absoluto.

### Opción C — desde una copia local

```bash
git clone https://github.com/Phraselium/Auditoria.git
```

```
/plugin marketplace add /ruta/donde/lo/hayas/clonado/Auditoria
/plugin install dula-audit@dula
```

### Opción D — probarlo sin instalar

```bash
claude --plugin-dir /ruta/a/Auditoria/dula-audit
```

La copia local tiene prioridad sobre la instalada, así que sirve para probar
cambios sin desinstalar nada.

### Para actualizar a una versión nueva (opciones B, C y D)

**Sincronizar el marketplace no actualiza el plugin ya instalado.** Hay que
reinstalarlo, y en este orden:

```
/plugin marketplace update dula
/plugin uninstall dula-audit@dula
/plugin install dula-audit@dula
```

Compruebe con `claude plugin list` que la versión es la que esperaba. Si
`marketplace update` falla, borre la caché y vuelva a añadirlo:

```
/plugin marketplace remove dula
/plugin marketplace add https://github.com/Phraselium/Auditoria.git
```

### Después de instalar, en cualquiera de los cuatro casos

```bash
pip install pandas openpyxl            # las dos únicas dependencias
```

```bash
dula doctor                            # comprueba instalación y configuración
```

`dula doctor` distingue lo que **impide** trabajar (falta Python o una
dependencia, falta un fichero de referencia) de lo que solo **degrada** el
resultado (sin tarifas, estimador sin calibrar, párrafos del informe pendientes
de contraste). Empiece siempre por ahí.

**Coste en contexto:** el plugin añade unos **3.100 tokens a cada sesión** — las
descripciones de sus 14 componentes. Eran 6.700 con las 35 skills anteriores.
Fuera de campaña puede desactivarlo con `/plugin disable dula-audit` y
reactivarlo con `/plugin enable dula-audit`.

Verificación completa de la librería de cálculo:

```bash
claude plugin validate <ruta>/dula-audit    # debe decir "Validation passed"
cd <ruta>/dula-audit && python3 tests/run_all.py   # 273/273 y cobertura 100 %
```

Después, **completa `skills/convenciones-dula/SKILL.md`**: los campos entre `«»` son los datos reales del
despacho. Sin ellos, el plugin funciona pero deja `[PENDIENTE-CLIENTE]` donde
haría falta un dato tuyo (tarifas, nº de ROAC, ruta base).

---

## B) claude.ai (web y escritorio)

claude.ai **no admite plugins**: admite skills sueltas en `.zip`. Y su
frontmatter solo acepta los seis campos de la especificación Agent Skills, así
que el plugin no se puede subir tal cual — `argument-hint`, `when_to_use` y
`user-invocable` darían `Unexpected key(s) in SKILL.md frontmatter`.

El paquete ya está construido en **`build/dula-audit-claude-ai.zip`** (240 KB).

**Pasos:**

1. Descargue `build/dula-audit-claude-ai.zip` del repositorio.
2. En claude.ai: **Ajustes → Capacidades** → active **«Ejecución de código y
   creación de archivos»**. Sin eso las skills no funcionan.
3. **Ajustes → Capacidades → Skills → Subir skill** y elija el `.zip`.
4. En una conversación nueva, escriba: *«comprueba la instalación de dula-audit
   con dula doctor»*.

**Qué cambia respecto a Claude Code:**

- No hay menú `/`: Claude activa la skill sola cuando el contexto lo pide
  («cuadra este balance», «recalcula estos leasings»). Puede invocarla
  explícitamente nombrándola.
- Los 39 procedimientos viajan en `procedimientos/`, y Claude abre **solo** el
  que necesita. Coste en contexto hasta entonces: cero.
- El `SKILL.md` es un índice con las once reglas innegociables y la tabla de
  procedimientos.

**Para regenerarlo** tras cualquier cambio en el plugin:

```bash
python3 tools/construir_claude_ai.py
```

El script valida el paquete contra la especificación —campos permitidos,
longitud de `name` y `description`, tamaño del cuerpo— y falla si algo no cumple.
La suite lo comprueba en cada ejecución.

### Qué NO se puede hacer desde los ajustes de la app

**Los ajustes de Claude no admiten plugins de Claude Code ni marketplaces.**
Plugins, marketplaces y `/plugin` son exclusivos de Claude Code. En los ajustes
de la app solo hay dos sitios, y solo uno sirve aquí:

| Sección de ajustes | Qué admite | ¿Sirve para dula-audit? |
|---|---|---|
| **Skills** (Personalizar en la app de escritorio, o los ajustes de skills en claude.ai) | Un `.zip` con una skill del estándar Agent Skills | **Sí** — es el `.zip` de esta sección |
| **Conectores** | Servidores MCP, por URL y OAuth | No. dula-audit no es un servidor MCP: no hay nada a lo que conectarse |

No hay ninguna opción de «añadir repositorio» ni de «marketplace» en la app.
Para eso hace falta Claude Code.

### Si la subida falla con «no se ha podido sincronizar»

Ese error es del validador de la plataforma, no del contenido de la skill. Las
cuatro causas conocidas están ya descartadas por construcción, y la suite lo
verifica en cada ejecución:

| Causa | Cómo se evita |
|---|---|
| Campos de frontmatter con texto libre | El paquete lleva **solo** `name` y `description`. `license` y `compatibility` exigen valores normalizados (SPDX, mapa de versiones) y con prosa se rechazan |
| Ficheros con bit de ejecución o scripts de shell | El punto de entrada es `dula.py`, Python plano en modo `0644`. No viaja ningún `.sh`, `.exe` ni binario |
| Extensiones desconocidas | Solo `.md`, `.py` y `.json` |
| Más de 200 ficheros | El paquete tiene 87 |

Si aun así falla, hay dos variantes para aislar la causa con dos pruebas:

| Variante | En qué se diferencia | Qué demuestra si esa sí sube |
|---|---|---|
| `dula-audit-claude-ai-plano.zip` (238 KB) | `SKILL.md` en la **raíz** del zip, sin carpeta contenedora | El validador esperaba la disposición plana |
| `dula-audit-claude-ai-minimo.zip` (98 KB) | Solo índice y procedimientos, **sin librería ni referencias** | El problema está en la librería o en las referencias, no en la skill |

Las dos son de diagnóstico, no el producto: **sin la librería Python no hay
cálculo determinista**, que es el fundamento del plugin.

Si ninguna sube, **el camino sin riesgo es Claude Code con la opción A**: se
descomprime en `~/.claude/skills/` y no interviene ningún validador.

> **Las skills no se sincronizan entre superficies.** Si actualiza el plugin,
> tiene que volver a subir el `.zip` a claude.ai.

---

## El menú `/`

Al escribir `/` aparecen las 42 entradas del plugin con su descripción en
castellano y el argumento que esperan. Están ordenadas en dos grupos:

| | |
|---|---|
| **`Flujo 1` … `Flujo 6`** | Los seis pasos del encargo, en orden. Empiece por aquí |
| **`Área A` … `Área M`** | Las doce áreas de trabajo de campo, con su letra del índice |
| El resto | Procedimientos concretos: materialidad, muestreo, informe, calidad… |

Cada entrada separa lo que usted lee de lo que necesita el modelo:

- **`description`** — una frase corta. Es lo que ve al pasar el ratón.
- **`when_to_use`** — el detalle de cuándo disparar la skill. No ensucia el menú.
- **`argument-hint`** — qué escribir después del comando.

Al pulsar cualquiera, lo primero que aparece en pantalla es **qué necesita, qué
va a recibir y el comando exacto** que se va a ejecutar. Si falta algún dato, se
lo pide en lugar de inventarlo.

**Diez entradas, no treinta y cinco.** Cinco de ellas son **guías de fase**:
`estimacion-y-aceptacion`, `planificacion`, `areas-de-campo`,
`tecnicas-de-prueba` y `cierre-del-encargo`. Cada una es un índice que dice qué
procedimiento de su fase toca y en qué orden, y abre solo ese, desde
`shared/procedimientos/`. Las otras cinco —`convenciones-dula`,
`ingesta-y-cuadres`, `comparador-documental`, `redaccion-informe` y
`revision-de-calidad`— llevan su contenido dentro porque se usan solas.

Los 29 procedimientos no ocupan contexto hasta que se abren: el menú es corto y
el conocimiento sigue completo.

---

## Flujo de un encargo

```
/dula-audit:nuevo-encargo "ACME SL" 2025 PGC-PYMES
        │
/estimacion-y-aceptacion            ─► estimacion-encargo · aceptacion-e-independencia
        │                              escalado-del-encargo
        │
/ingesta-y-cuadres                  ◄── PUERTA: si no cuadra, se detiene
        │
/planificacion                      ─► entendimiento-entidad · materialidad
        │                              mapa-de-riesgos · diseno-de-pruebas
        │                              plan-y-solicitud-informacion (PBC)
        │
/areas-de-campo <área>              ─► las 12 áreas + saldos de apertura
/tecnicas-de-prueba                 ─► muestreo · analiticos · test-asientos-diario
/comparador-documental              ─► CCAA ↔ balance ↔ memoria ↔ borradores
/revision-de-calidad                ─► dónde estamos, qué falta, y el panel del socio
        │
/cierre-del-encargo                 ─► hechos-posteriores-y-empresa-en-funcionamiento
        │                              evaluacion-de-incorrecciones
        │                              comunicaciones-y-manifestaciones
        │                              archivo-y-cierre
        │
/redaccion-informe                  ◄── incluida la sección del Impuesto sobre Sociedades
```

`revision-de-calidad --pre-vuelo` se ejecuta **durante toda la campaña**, no solo
al final. Es el cambio de mayor impacto real: si el socio solo ve las excepciones
el último día, el problema no se ha resuelto, se ha concentrado.

---

## Estructura

```
dula-audit/
├── .claude-plugin/plugin.json
├── skills/convenciones-dula/SKILL.md                    # perfil del despacho, convenciones y umbrales
├── GUIA-ARRANQUE.md             # una página para empezar
├── bin/dula                     # lanzador; se añade al PATH del Bash
├── commands/nuevo-encargo.md    # el único comando: crea la carpeta y arranca
├── agents/                      # extractor-documental · reconciliador · revisor-critico
├── skills/                      # 10 skills: 5 guías de fase + 5 con contenido propio
└── shared/
    ├── procedimientos/          # 29 procedimientos que las guías abren bajo demanda
    ├── scripts/dula/            # 23 módulos: ingesta, cuadres, muestreo, leasing…
    ├── references/              # mapeo PGC, desgloses de memoria, catálogo de
    │                            # riesgos, 12 packs de programa por área
    └── templates/               # informe, cartas, comunicaciones, índice
```

**Estado del encargo:** `encargo.json` por cliente y ejercicio, con materialidad
versionada, riesgos, papeles, excepciones, incorrecciones, pendientes y huellas
SHA-256 de los ficheros fuente.

---

## Marco normativo aplicado

| Bloque | Versión |
|---|---|
| Bloque de informe (510, 570R, 600R, 700R, 705R, 706R, 710, 720R, 260) | **RICAC de 22/01/2026** (BOE-A-2026-2234) |
| Riesgo | NIA-ES 315 (Revisada) |
| Estimaciones | NIA-ES 540 (Revisada) — RICAC 11/04/2024 |
| Grupos | NIA-ES 600 (Revisada) — ejercicios desde 01/01/2024 |
| Calidad | NIGC1-ES, NIGC2-ES y NIA-ES 220 (Revisada) — en vigor desde 01/01/2023 |
| Contable | PGC (RD 1514/2007), PGC PYMES y Resoluciones del ICAC |
| Regulación | Ley 22/2015 y RD 2/2021 · Reglamento (UE) 537/2014 para EIP |

**NIA para EMC (ISA for LCE):** efectiva internacionalmente desde el 15/12/2025
pero **no adoptada por el ICAC**. Se usa solo para calibrar la proporcionalidad de
los programas. El marco aplicado y declarado sigue siendo **NIA-ES**.

### La sección del Impuesto sobre Sociedades — lo que hay que saber

**No trata de la contabilización del impuesto.** Responde a la **DA 11ª de la
LAC** (Ley 28/2022, transposición del art. 48 *ter* de la Directiva 2013/34/UE):
el informe público de **transparencia fiscal país por país**, exigible a matrices
últimas con **cifra de negocios consolidada > 750 M€** en los dos últimos
ejercicios consecutivos.

Para la cartera de Dula será, en la práctica totalidad de los casos, la redacción
de **entidad NO obligada**. El trabajo del área fiscal no cambia.

**Dos puertas de aplicación distintas:**

| Elemento | Se aplica a |
|---|---|
| Apartado del impuesto sobre sociedades | Ejercicios iniciados **desde 22/06/2025**, aunque el encargo se contratara antes |
| Resto del bloque de informe | Encargos **contratados o iniciados desde 01/01/2026** |

⚠️ **Pendiente de contraste literal.** El entorno donde se generó el plugin no
tiene acceso a `boe.es` ni a `icac.gob.es`. La estructura y el contenido de la
sección están verificados; el **texto literal** de los párrafos marcados
`[VERIFICAR-LITERAL-ICAC]` en `shared/templates/informe-auditoria.md` debe
contrastarse **una vez** contra el PDF oficial de la NIA-ES 700R antes del primer
uso real.

---

## Uso de la librería desde la línea de comandos

El plugin expone el lanzador **`dula`** en el `PATH` del Bash mientras está
activo — no hay que exportar `PYTHONPATH` ni saber dónde se instaló:

```bash
dula doctor          # empiece siempre por aquí
dula --help
```

| Subcomando | Qué hace |
|---|---|
| `doctor` | Comprueba instalación, dependencias y configuración |
| `nuevo` | Crea carpeta y estado del encargo |
| `estimar` | Perfil de complejidad, horas y honorarios |
| `ingesta` | Normaliza y ejecuta los cuadres de integridad |
| `materialidad` | Determina la materialidad, con recálculo y alerta de alcance |
| `leasing` | Procesa el lote de contratos de arrendamiento |
| `financiacion` | Recalcula la cartera, confirmaciones y covenants |
| `amortizaciones` | Recálculo integral del inmovilizado |
| `asientos` | Test de asientos del diario |
| `muestreo` | MUS, atributos o dirigido, con semilla registrada |
| `analiticos` | Variaciones, ratios y expectativas |
| `comparar` | Comparador documental (8 comparaciones) |
| `calidad` | Revisión del archivo + panel del socio |
| `estado` | Dónde está el encargo y cuál es el siguiente paso |
| `horas` | Imputa y consulta horas por papel de trabajo |
| `pbc` | Pendientes del cliente, ordenados por ruta crítica |
| `reservas` | Reservas indisponibles y restringidas, con la regla del art. 274 LSC |
| `validar` | Valida una ejecución de la bitácora de uso de IA |

---

## Banco de pruebas

`tests/test_aceptacion.py` demuestra los seis criterios de aceptación
**ejecutándolos** sobre fixtures sintéticos (nada de datos de clientes):

**`tests/test_aceptacion.py`** — los seis criterios, sobre fixtures sintéticos
(nada de datos de clientes):

| # | Criterio | Comprobaciones |
|---|---|---|
| 1 | Un encargo pequeño se recorre entero sin salir del plugin | 7/7 |
| 2 | 100 contratos heterogéneos → cuadro completo con excepciones aisladas | 11/11 |
| 3 | El comparador detecta la diferencia deliberada memoria/balance | 5/5 |
| 4 | Cálculos reproducibles por script y trazables al fichero de origen | 8/8 |
| 5 | La revisión detecta un papel sin conclusión y un riesgo sin respuesta | 7/7 |
| 6 | El modelo de informe corresponde a la versión normativa vigente | 14/14 |

**`tests/test_libreria.py`** — 205 comprobaciones unitarias con **resultados
numéricos conocidos**, no solo «que no reviente»: TIR de un préstamo francés
contra su tipo de partida, proyección de errores por *tainting*, umbral doble de
los analíticos, clasificación de arrendamientos indicador a indicador, período
medio de cobro, conciliación bancaria en los dos sentidos.

```bash
python3 tests/run_all.py             # 273/273 + cobertura, es el que hay que ejecutar
python3 tests/generar_fixtures.py    # regenera los datos sintéticos
```

`run_all.py` **falla si la cobertura baja del 95 %**. Un plugin que produce
papeles de trabajo firmados no puede llevar código que nunca se ha ejecutado.

---

## Limitaciones declaradas

Conviene tenerlas presentes antes del primer uso real:

- **La extracción de contratos escaneados sigue siendo humana.** El plugin declara
  confianza por campo y manda a revisión todo lo que baje de 0,85. Prometer el
  100 % automático sería vender un riesgo, no una herramienta.
- **El estimador no está calibrado** con datos de Dula. Las horas base son
  genéricas hasta que se registren 3-5 encargos reales en
  `shared/references/historico-encargos.json`.
- **No hay skill de consolidación en v1.** El motor la detecta, eleva el perfil y
  marca `[JUICIO-AUDITOR]` con referencia a la NIA-ES 600 (Revisada). Hacerlo mal
  sería peor que no hacerlo.
- **El texto literal del apartado del Impuesto sobre Sociedades** está pendiente de
  contraste con el PDF oficial del ICAC (ver arriba).
- **La compatibilidad con Data Sniper no está verificada contra un fichero real.**
  La ingesta es genérica y la detección de cabeceras y columnas absorbe las
  variantes habituales, pero es una hipótesis razonada, no un hecho comprobado.
