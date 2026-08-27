# auditoria-nia-es

Plugin de Claude Code para la auditoría de cuentas anuales en España, bajo
NIA-ES. Cubre el ciclo completo del encargo —captación, aceptación,
planificación, trabajo de campo, cierre e informe— con cálculo determinista por
script, traza de cada cifra a fichero, hoja y celda, y reporte por excepción.
Pensado para encargos de dos días a dos meses, con el socio firmante revisando
un panel de una página en vez de todo el archivo.

## Instalación

**Claude Code** — todo: 10 skills, 1 comando, 3 agentes, 29 procedimientos y la
librería de cálculo.

```
/plugin marketplace add Phraselium/Auditoria
/plugin install auditoria-nia-es@auditoria-nia-es
```

**claude.ai** — el conocimiento y los scripts, sin menú `/` ni subagentes.
Descarga `dist/auditoria-nia-es.skill` y súbelo en **Ajustes → Capacidades →
Skills**, con «Ejecución de código y creación de archivos» activada. O
constrúyelo con `python3 scripts/empaquetar_skill.py`.

Guía completa, con la tabla de qué funciona en cada sitio y qué hacer si falla
la sincronización, en [INSTALACION.md](INSTALACION.md).

Después:

```bash
pip install -r requirements.txt                    # pandas y openpyxl
python3 scripts/comprobar_privacidad.py --instalar-hook  # bloquea commits con datos de cliente
python3 tests/run_all.py                           # 298 comprobaciones
audita doctor                                      # qué falta por configurar
```

Y completa `config/configuracion.md` a partir de `config/configuracion.ejemplo.md`
con los datos del despacho — pero no lo subas relleno: está en `.gitignore` y el
verificador de privacidad falla si aparece.

## Contexto de uso

Despacho de auditoría con cartera mayoritariamente de PYME y algún cliente
grande. Trabajo intensivo en Excel, con Data Sniper para OCR. Sumas y saldos de
8 a 10 dígitos por cuenta y 6 a 8 grupos. Los dos cuellos de botella reales son
los **arrendamientos financieros** —hay encargos con más de cien contratos, cada
entidad con su formato— y la **financiación bancaria**, con cuadros heterogéneos
y confirmaciones que llegan tarde.

Y la restricción que lo condiciona todo: **hay poco tiempo para revisiones, y el
socio firmante no revisa en detalle todo lo que firma.** Por eso cada salida
llega ya verificada, cuadrada y trazada, y las excepciones aparecen durante la
campaña, no el último día.

## Qué hace y qué no

| Hace | No hace |
|---|---|
| Normaliza la contabilidad de cualquier ERP y la cuadra | Accede a la contabilidad del cliente |
| Recalcula cien contratos de leasing y los clasifica | Decide la clasificación: la propone |
| Fija la materialidad y dimensiona las muestras | Firma el informe |
| Cuadra memoria, balance, borradores e informe | Sustituye la revisión del socio |
| Detecta lo que falta en el archivo antes de firmar | Concluye cuando la evidencia no basta |
| Redacta el informe según los modelos vigentes | Reduce el alcance para ahorrar tiempo |

**Asiste, no decide ni firma.** Toda conclusión es una propuesta fundamentada
sujeta a la validación del auditor firmante. La dirección, supervisión y
revisión del encargo es responsabilidad **indelegable** del socio (NIA-ES 220
Revisada).

## Tres reglas de diseño

**El script calcula, el modelo interpreta.** Todo cuadre, recálculo,
amortización, extrapolación de muestra o comparación numérica se ejecuta en
Python. Ningún importe sale de una estimación mental, y por eso cualquier
resultado es reejecutable por un revisor.

**Cero invención.** Ninguna cifra, fecha, cláusula o referencia normativa sin
origen verificable. Si falta un dato: `[PENDIENTE-CLIENTE]`. Si hace falta
criterio profesional: `[JUICIO-AUDITOR]`. Nunca se rellena en silencio, y si la
evidencia no basta para concluir, se dice en vez de concluir igualmente.

**Reporte por excepción.** La hoja de detalle lo contiene todo; la pantalla,
solo las excepciones, con un máximo de 15 líneas. Un volcado de 400 filas no es
información: es trabajo trasladado al revisor.

## Skills

Diez. Cinco son **guías de fase**: un índice que dice qué procedimiento toca y
en qué orden, y abre solo ese. Las otras cinco llevan su contenido dentro porque
se usan solas. Los 29 procedimientos no cuestan contexto hasta que se abren.

| Skill | Cubre |
|---|---|
| `convenciones-despacho` | Umbrales, índice de papeles, marco normativo y las once reglas. Se carga la primera |
| `estimacion-y-aceptacion` | Perfil de complejidad, horas y honorarios, independencia, alcance |
| `ingesta-y-cuadres` | Normaliza cualquier ERP y ejecuta los cuadres. **Puerta de entrada obligatoria** |
| `planificacion` | Entendimiento, materialidad, mapa de riesgos, diseño de pruebas, PBC |
| `areas-de-campo` | Las doce áreas más saldos de apertura |
| `tecnicas-de-prueba` | Muestreo, analíticos y test de asientos del diario |
| `comparador-documental` | Cuentas anuales, memoria, borradores e informe |
| `cierre-del-encargo` | Incorrecciones, hechos posteriores, manifestaciones, archivo |
| `redaccion-informe` | Tipo de opinión y redacción según los modelos vigentes de 2026 |
| `revision-de-calidad` | Estado del encargo y panel del socio, con 22 comprobaciones |

No hace falta invocarlas: preguntando en lenguaje normal se carga solo lo que
haga falta. `/` las muestra todas.

## Agentes

`extractor-documental` — convierte contratos, escrituras, cuadros de entidades
financieras y facturas en datos procesables, con traza a página y cláusula y
confianza declarada por campo.

`reconciliador` — cuadres y conciliaciones masivas entre ficheros. No aplica
criterio profesional: solo calcula.

`revisor-critico` — busca activamente lo que falta en el archivo, sin
complacencia. Úsalo antes de firmar en perfiles COMPLEJO, o cuando un archivo
parezca demasiado limpio.

## Scripts

```bash
# Puerta de entrada: normaliza la contabilidad y ejecuta los diez cuadres
audita ingesta sumas_y_saldos.xlsx --diario diario.xlsx --encargo .

# Materialidad, con la magnitud elegida y justificada
audita materialidad '{"cifra_negocios": 1850000, "total_activo": 920000}' \
    --perfil ESTANDAR --encargo .

# Cien contratos de leasing en tres formatos distintos, recalculados y clasificados
audita leasing contratos/ 2025-12-31 --encargo . --papel "01-papeles/F-1.xlsx"

# Cartera de financiación, confirmaciones bancarias y covenants
audita financiacion cartera.xlsx 2025-12-31 --encargo .

# Muestra con la semilla registrada: sin ella no es reejecutable por un revisor
audita muestreo poblacion.xlsx importe --metodo mus --materialidad 46000 --semilla 12345

# Test de asientos inusuales — obligatorio en todo encargo (NIA-ES 240.31)
audita asientos diario.xlsx 2025-12-31 --materialidad 46000 --perfil ESTANDAR

# Dónde está el encargo y cuál es el siguiente paso
audita estado <encargo>

# Panel del socio: qué exige su juicio y si se puede firmar
audita calidad <encargo> --pre-vuelo
```

Subcomandos completos con `audita --help`. Si `bin/` no está en el PATH:
`python3 "${CLAUDE_PLUGIN_ROOT:-.}"/scripts/audita/cli.py`.

## Trazabilidad y uso de IA

Cada papel de trabajo lleva cuatro hojas: **Conclusión**, **Detalle** (con
fórmulas `=SUM()` vivas), **Traza** (el `fichero!hoja!celda` de cada cifra) y
**Excepciones**, ordenadas por severidad y con su acción concreta.

`uso-ia.log` registra cada ejecución asistida, y `CAL-091` cierra el bucle:
falla si el resultado de una ejecución sin validar está dentro de un papel
concluido. La validación no es un trámite — acredita que un auditor ha revisado
el resultado, no solo que la herramienta se ejecutó. Sin eso, ante una
inspección no hay forma de distinguir un cálculo revisado de uno aceptado a
ciegas (NIGC1-ES).

```bash
audita validar <encargo> --listar
audita validar <encargo> --entrada IA-0003 --quien "MJ Pérez"
```

## Privacidad

El plugin es código publicable; los papeles de trabajo y los datos de los
clientes no lo son, y están sujetos al **deber de secreto del art. 31 LAC**, a
la normativa de prevención del blanqueo y al RGPD. Tres capas:

`.gitignore` excluye toda hoja de cálculo, `encargos/`, `clientes/`,
`salidas/`, certificados, `encargo.json`, `uso-ia.log`, la configuración del
despacho y `datos/nombres_privados.txt`.

`scripts/comprobar_privacidad.py` revisa lo que va a subirse y falla si
encuentra NIF, NIE o CIF con dígito de control válido —un identificador
inventado casi nunca valida; uno real, siempre—, IBAN correctos, correos,
teléfonos, ficheros prohibidos, o nombres de tu lista privada.

Hook de pre-commit con `--instalar-hook`: ningún commit se crea sin pasar la
comprobación.

```bash
python3 scripts/comprobar_privacidad.py             # lo versionado
python3 scripts/comprobar_privacidad.py --staged    # lo que va al commit
python3 scripts/comprobar_privacidad.py --historial # busca en todo el historial
```

Para vigilar las razones sociales de tu cartera, copia
`datos/nombres_privados.ejemplo.txt` a `datos/nombres_privados.txt` (ignorado
por git) y pon un nombre por línea. Sin él, la comprobación cubre
identificadores y ficheros, pero no denominaciones.

Los fixtures de prueba usan una sociedad inequívocamente ficticia y **calculan
su CIF en tiempo de ejecución**, así que en el repositorio no hay escrito ningún
identificador con dígito de control válido.

Si algo privado llega a subirse, no basta con corregirlo en un commit nuevo: hay
que reescribir el historial y forzar el push. Y aun así GitHub conserva los
commits huérfanos accesibles por su SHA hasta su recolección de basura, y
cualquier fork o caché previo mantiene la copia. Ante una fuga real de datos de
cliente, reescribe, fuerza el push y abre un ticket a GitHub Support.

## Pruebas

```bash
python3 tests/run_all.py     # 298 comprobaciones, cobertura de la librería
```

Cubren lo que puede romperse en silencio y llegar a un informe firmado: los diez
cuadres de integridad, el recálculo de amortizaciones elemento a elemento, el
tipo de interés implícito por bisección y la clasificación de arrendamientos, la
proyección de errores de la muestra con *tainting*, los cuadres entre memoria y
balance, el árbol de decisión de la opinión, y las 22 comprobaciones de calidad
del archivo.

Seis criterios de aceptación de extremo a extremo: un encargo pequeño completo,
cien contratos de leasing en formatos dispares, un comparador que tiene que
detectar una diferencia deliberada de 4.850,00 €, la reproducibilidad de los
cálculos, una revisión de calidad que tiene que detectar un papel sin concluir y
un riesgo sin respuesta, y el informe con la sección del Impuesto sobre
Sociedades.

Incluyen regresiones de defectos reales aparecidos durante el desarrollo: un
cuadre que fallaba sobre balances ya regularizados, un emparejamiento de
columnas que confundía el identificador del contrato con el nombre del banco, y
un covenant sin datos que se daba por cumplido porque un valor ausente se leía
como cero.

## Verificación de la normativa

El conocimiento del modelo tiene fecha de corte y la normativa cambia. Los
párrafos del modelo de informe que no se han podido contrastar contra el PDF
oficial del ICAC van marcados `[VERIFICAR-LITERAL-ICAC]`, y `audita doctor` los
cuenta. Contrástalos una vez antes del primer uso real y borra la marca.

Marco aplicado: NIA-ES; NIGC1-ES y NIGC2-ES; **RICAC de 22/01/2026**
(BOE-A-2026-2234), que modifica las NIA-ES 510, 570R, 600R, 700R, 705R, 706R,
710 y 720R; LAC 22/2015 y RD 2/2021; PGC y PGC PYMES.

## Estructura

```
.claude-plugin/    plugin.json y marketplace.json
skills/            10 skills: 5 guías de fase y 5 con contenido propio
procedimientos/    29 procedimientos que las guías abren bajo demanda
commands/          nuevo-encargo: crea la carpeta y arranca la aceptación
agents/            extractor-documental, reconciliador y revisor-critico
scripts/           librería de cálculo, empaquetador y verificador de privacidad
  audita/          23 módulos: ingesta, cuadres, muestreo, leasing, calidad…
referencias/       mapeo del PGC, desgloses de memoria, catálogo de riesgos
  programas/       los doce programas de trabajo escalados por perfil
plantillas/        informe, cartas de encargo y manifestaciones, comunicaciones
config/            configuración del despacho (la rellena y no se versiona)
datos/             lista de nombres privados para el verificador
dist/              paquetes para claude.ai y para el directorio de skills
bin/audita         lanzador; Claude Code lo añade al PATH del Bash
tests/             suite completa y generador de fixtures sintéticos
```

**Estado del encargo:** `encargo.json` por cliente y ejercicio, con materialidad
versionada, riesgos, papeles, excepciones, incorrecciones, pendientes del
cliente, horas y huellas SHA-256 de los ficheros fuente.

## Aviso

Esta herramienta es un apoyo al trabajo de auditores de cuentas. No sustituye el
criterio del auditor ni la consulta de la normativa vigente. Nada de lo que
produce constituye una opinión de auditoría, y todo requiere revisión y
validación humana antes de incorporarse a un archivo o a un informe firmado.
