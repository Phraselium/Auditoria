# dula-audit

Equipo de auditoría senior virtual para **Dula Auditores**. Cubre el ciclo
completo del encargo —aceptación, planificación, trabajo de campo, cierre e
informe— bajo NIA-ES, con cálculo determinista por script, trazabilidad total y
reporte por excepción.

**Estado:** v1.1.0 · 34 skills · 7 comandos · 3 agentes · 21 módulos Python ·
**208/208 comprobaciones superadas · 100 % de cobertura de la librería**.

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

```bash
# 1. Copiar el plugin donde Claude Code lo encuentre
cp -r dula-audit ~/.claude/plugins/

# 2. Dependencias (solo dos, nada exótico)
pip install pandas openpyxl

# 3. Verificar la instalación
cd ~/.claude/plugins/dula-audit
python3 tests/run_all.py     # 208/208 y cobertura 100 %
```

Después, **completa `CLAUDE.md`**: los campos entre `«»` son los datos reales del
despacho. Sin ellos, el plugin funciona pero deja `[PENDIENTE-CLIENTE]` donde
haría falta un dato tuyo (tarifas, nº de ROAC, ruta base).

---

## Flujo de un encargo

```
/dula-audit:nuevo-encargo "ACME SL" 2025 PGC-PYMES
        │
        ├─ estimacion-encargo ──► perfil, horas, honorarios, go/no-go
        └─ aceptacion-e-independencia ──► declaración firmable + carta de encargo
        │
/dula-audit:planificar
        │
        ├─ ingesta-y-cuadres        ◄── PUERTA: si no cuadra, se detiene
        ├─ entendimiento-entidad
        ├─ materialidad
        ├─ mapa-de-riesgos
        ├─ escalado-del-encargo     ◄── configura qué se activa y con qué profundidad
        ├─ diseno-de-pruebas        ◄── cero riesgos huérfanos, cero pruebas huérfanas
        └─ plan-y-solicitud-informacion (PBC)
        │
/dula-audit:campo <area>            ─► 12 áreas + area-runner + test de asientos
/dula-audit:comparar                ─► CCAA ↔ balance ↔ memoria ↔ borradores
/dula-audit:estado                  ─► dónde estamos y cuál es el siguiente paso
        │
/dula-audit:cerrar
        │
        ├─ evaluacion-de-incorrecciones
        ├─ hechos-posteriores-y-empresa-en-funcionamiento
        ├─ comunicaciones-y-manifestaciones
        ├─ redaccion-informe        ◄── incluida la sección del Impuesto sobre Sociedades
        ├─ revision-de-calidad      ◄── panel del socio + listado por severidad
        └─ archivo-y-cierre
```

`revision-de-calidad --pre-vuelo` se ejecuta **durante toda la campaña**, no solo
al final. Es el cambio de mayor impacto real: si el socio solo ve las excepciones
el último día, el problema no se ha resuelto, se ha concentrado.

---

## Estructura

```
dula-audit/
├── .claude-plugin/plugin.json
├── CLAUDE.md                    # perfil del despacho, convenciones y umbrales
├── GUIA-ARRANQUE.md             # una página para empezar
├── commands/                    # 7 comandos de entrada rápida
├── agents/                      # extractor-documental · reconciliador · revisor-critico
├── skills/                      # 34 skills
└── shared/
    ├── scripts/dula/            # 16 módulos: ingesta, cuadres, muestreo, leasing…
    ├── references/              # mapeo PGC, desgloses de memoria, catálogo de
    │                            # riesgos, 11 packs de programa por área
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

```bash
export PYTHONPATH=<plugin>/shared/scripts
python3 -m dula.cli --help
```

| Subcomando | Qué hace |
|---|---|
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

**`tests/test_libreria.py`** — 156 comprobaciones unitarias con **resultados
numéricos conocidos**, no solo «que no reviente»: TIR de un préstamo francés
contra su tipo de partida, proyección de errores por *tainting*, umbral doble de
los analíticos, clasificación de arrendamientos indicador a indicador, período
medio de cobro, conciliación bancaria en los dos sentidos.

```bash
python3 tests/run_all.py             # 208/208 + cobertura, es el que hay que ejecutar
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
