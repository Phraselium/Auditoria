---
name: convenciones-dula
description: 'Configuración del despacho Dula Auditores: perfil y números de ROAC, marco normativo aplicado y sus fechas de entrada en vigor, índice y nomenclatura de papeles de trabajo, estructura de carpetas del encargo, marcadores reservados, severidades, umbrales de materialidad y tolerancias de cuadre, tarifas por categoría, perfiles de ERP y las once reglas de comportamiento innegociables del plugin. Cárgala al inicio de cualquier trabajo de auditoría y siempre que necesites un umbral, una convención o la versión normativa aplicada.'
---

# Convenciones, umbrales y configuración de Dula Auditores

**Este es el fichero de configuración del plugin.** Todo lo que aparece entre
`«»` hay que completarlo con los datos reales del despacho antes del primer uso
en producción. Lo que no esté completado, el plugin lo tratará como
`[PENDIENTE-CLIENTE]` y no lo inventará.

> **Consúltalo al inicio de cualquier trabajo de auditoría** y siempre que
> necesites un umbral, la referencia de un papel de trabajo, la versión
> normativa aplicada o una regla de comportamiento. Las reglas de la sección 7
> son innegociables: cualquier skill que las incumpla está mal ejecutada.

---

## 1. Perfil del despacho

| | |
|---|---|
| Denominación | «DULA AUDITORES, S.L.» |
| Nº de inscripción en el ROAC de la sociedad | «SXXXX» |
| Socio firmante habitual y nº de ROAC | «Nombre Apellidos — XXXXX» |
| Cartera | Sociedades españolas, mayoritariamente PYME, con algunas entidades grandes |
| EIP | No con carácter general. El plugin contempla el caso y fuerza perfil COMPLEJO |
| Marcos contables habituales | PGC PYMES · PGC · (excepcionalmente consolidado) |
| Herramientas del despacho | Excel intensivo · Data Sniper (extracción/OCR) · revisión visual |
| Duración de los encargos | De 2 días (sociedad pequeña, facturación automatizada) a 2 meses (entidad grande) |

**Restricción operativa declarada, que condiciona todo el diseño:** hay poco
tiempo para revisiones y el socio firmante no revisa en detalle todo lo que
firma. Por eso **todo output del plugin debe llegar ya verificado, cuadrado y
trazado**, con las excepciones aisladas y explicadas.

> **Lo que el plugin no hace.** La dirección, supervisión y revisión del encargo
> es responsabilidad **indelegable** del socio firmante bajo la NIA-ES 220
> (Revisada) y el sistema de gestión de la calidad. El plugin no la sustituye:
> la hace viable en minutos, entregando el panel del socio con las cuestiones que
> exigen juicio y todo lo demás cuadrado y evidenciado.

---

## 2. Marco normativo aplicado

El plugin **cumple** la normativa; no la recita. Las referencias normativas solo
aparecen cuando fundamentan una decisión concreta, en formato breve, y siempre en
la documentación del papel de trabajo.

| Bloque | Versión aplicada |
|---|---|
| Bloque de informe (510, 570R, 600R, 700R, 705R, 706R, 710, 720R y 260) | **Resolución del ICAC de 22/01/2026** (BOE-A-2026-2234) |
| Identificación y valoración del riesgo | NIA-ES 315 (Revisada) — ejercicios iniciados desde 15/12/2022 |
| Estimaciones contables | NIA-ES 540 (Revisada) — RICAC 11/04/2024 |
| Auditoría de grupos | NIA-ES 600 (Revisada) — ejercicios iniciados desde 01/01/2024 |
| Gestión de la calidad | NIGC1-ES, NIGC2-ES y NIA-ES 220 (Revisada) — RICAC 20/04/2022, en vigor desde 01/01/2023 |
| Marco contable | PGC (RD 1514/2007), PGC PYMES y Resoluciones del ICAC |
| Regulación de la actividad | Ley 22/2015 (LAC) y RD 2/2021 (Reglamento) |
| EIP | Reglamento (UE) 537/2014 |

**NIA para EMC (ISA for LCE).** Efectiva internacionalmente para ejercicios
iniciados desde el 15/12/2025, **pero el ICAC no la ha adoptado**. El plugin la
usa **solo como fuente de calibración** de la proporcionalidad y la
simplificación de los programas. Todo papel de trabajo declara expresamente que
el marco aplicado es **NIA-ES**.

### Las dos puertas de aplicación de la RICAC de 22/01/2026

No son una, son dos, y se evalúan por separado:

| Elemento | Se aplica a |
|---|---|
| Apartado sobre el impuesto sobre sociedades | Ejercicios iniciados **desde 22/06/2025**, aunque el encargo se contratara antes |
| Resto de modificaciones del bloque de informe | Encargos **contratados o iniciados desde 01/01/2026** |

Ante solapamiento ambiguo, se elige el **modelo más completo** y se documenta
como `[JUICIO-AUDITOR]`.

### ⚠️ Qué es y qué no es el apartado del Impuesto sobre Sociedades

**No trata de la contabilización del impuesto.** Responde a la **disposición
adicional undécima de la LAC** (introducida por la Ley 28/2022, transposición del
art. 48 *ter* de la Directiva 2013/34/UE): el **informe público de transparencia
fiscal país por país**, exigible a matrices últimas con **cifra de negocios
consolidada superior a 750 M€** en los dos últimos ejercicios consecutivos.

En la práctica totalidad de la cartera de Dula será la **redacción de entidad NO
obligada**. El trabajo del área fiscal (conciliación resultado ↔ base imponible,
impuestos diferidos, contingencias) es independiente y no cambia.

---

## 3. Convenciones

### 3.1 Índice de papeles de trabajo

Aplicado por **todas** las skills, sin excepción.

| Ref. | Área | Ref. | Área |
|---|---|---|---|
| `0.x` | Aceptación, independencia y carta de encargo | `F` | Arrendamientos |
| `1.x` | Planificación | `G` | Fondos propios y reservas |
| `2.x` | Ingesta, cuadres y comparador documental | `H` | Proveedores y compras |
| `A` | Inmovilizado | `I` | Personal |
| `B` | Existencias | `J` | Fiscal |
| `C` | Clientes e ingresos | `K` | Provisiones y contingencias |
| `D` | Tesorería | `L` | Subvenciones |
| `E` | Financiación y deuda | `M` | Partes vinculadas |
| | | `N` | Hechos posteriores y empresa en funcionamiento |
| `8.x` | Cierre: incorrecciones, manifestaciones y comunicaciones | `9.x` | Informe y revisión de calidad |

Nomenclatura de fichero: `«REF» «Título breve».xlsx` — p. ej. `F-1 Arrendamientos.xlsx`.

### 3.2 Estructura de carpetas del encargo

```
«ruta-base»/<CLIENTE>/<EJERCICIO>/
├── encargo.json      # estado único, encadena las fases sin repetir ingestas
├── 00-fuentes/       # ficheros del cliente, inmutables, con hash SHA-256
├── 01-papeles/       # papeles de trabajo .xlsx
├── 02-documentos/    # cartas, memorandos, informe
└── uso-ia.log        # registro de asistencia automatizada
```

**Ruta base del despacho:** «C:\Auditorias» *(pendiente de confirmar)*

### 3.3 Formato del papel de trabajo

Cuatro hojas, siempre, generadas por `shared/scripts/dula/excel_out.py`:

| Hoja | Contenido |
|---|---|
| **Conclusión** | Referencia, cliente, ejercicio, alcance, fundamento del enfoque, riesgos cubiertos, conclusión, indicadores, firma del revisor |
| **Detalle** | Los datos, con **fórmulas vivas** (`=SUM(...)`) en las líneas de total para que el revisor vea el cuadre sin reejecutar nada |
| **Traza** | Origen de cada dato: `fichero!hoja!celda`, confianza de extracción y marca de revisión |
| **Excepciones** | Solo lo que no encaja, ordenado por severidad y con importe, causa sugerida y acción |

### 3.4 Marcadores reservados

| Marcador | Significado |
|---|---|
| `[PENDIENTE-CLIENTE]` | Dato ausente. **Nunca** se rellena con una estimación silenciosa |
| `[JUICIO-AUDITOR]` | Requiere criterio profesional humano |
| `[VERIFICAR-LITERAL-ICAC]` | Texto normativo pendiente de contraste literal con el PDF oficial |

### 3.5 Severidad de las excepciones

| Severidad | Significado |
|---|---|
| `BLOQUEANTE` | Impide continuar o impide firmar |
| `RESOLVER` | A resolver antes de firmar |
| `DOCUMENTAR` | Mejora de documentación |
| `INFORMATIVA` | Se deja constancia, no exige acción |

---

## 4. Umbrales configurables

### 4.1 Materialidad — `shared/scripts/dula/materialidad.py`

| Magnitud de referencia | Rango |
|---|---|
| Resultado antes de impuestos | 5 % – 10 % |
| Importe neto de la cifra de negocios | 0,5 % – 2 % |
| Total activo | 0,5 % – 2 % |
| Patrimonio neto | 1 % – 5 % |
| Total gastos | 0,5 % – 2 % |

**Materialidad de ejecución** (% de la global): `LIGERO` 75 % · `ESTÁNDAR` 65 % ·
`COMPLEJO` 55 %.
**Umbral de incorrecciones claramente insignificantes:** 5 % de la materialidad global.

### 4.2 Tolerancias de cuadre

| Concepto | Valor | Módulo |
|---|---|---|
| Cuadres contables (redondeo de céntimos) | 0,01 € | `cuadres.py` |
| Comparador documental (las CCAA se formulan redondeadas) | 1,00 € | `comparador.py` |
| Contratos de arrendamiento | 1,00 € | `leasing.py` |
| Tipo de interés implícito vs declarado | 0,25 p.p. | `leasing.py` |
| Confianza mínima de extracción documental | 0,85 | `traza.py` |

### 4.3 Muestreo — `shared/scripts/dula/muestreo.py`

Factores de fiabilidad (Poisson) para MUS: riesgo 5 % → 3,00 · 10 % → 2,31 ·
15 % → 1,90 · 20 % → 1,61 · 25 % → 1,39.
Tamaños para pruebas de controles: diaria 25 · semanal 15 · mensual 5 ·
trimestral 2 · anual 1 · varias veces al día 40.

### 4.4 Analíticos — `shared/scripts/dula/analiticos.py`

Umbral de investigación **doble**: se investiga lo que supera **a la vez** el
50 % de la materialidad de ejecución **y** el 10 % de variación relativa. El
umbral se fija **antes** de mirar las cifras (NIA-ES 520.5.c).

### 4.5 Festivos para el test de asientos — `shared/scripts/dula/asientos.py`

Nacionales de aplicación general: 1/1, 6/1, 1/5, 15/8, 12/10, 1/11, 6/12, 8/12,
25/12.
**Añada aquí los autonómicos y locales de la sede de sus clientes:** «...»

---

## 5. Tarifas y calibración *(a completar)*

Sin estos datos, `estimacion-encargo` estima **horas** pero devuelve los
honorarios como `[PENDIENTE-CLIENTE]`. **No inventa un precio.**

```jsonc
{
  "socio":    «120.0»,
  "gerente":  «85.0»,
  "senior":   «60.0»,
  "ayudante": «40.0»,
  "_coste_hora": {                 // coste directo, para el punto muerto
    "socio": «55.0», "gerente": «42.0», "senior": «28.0», "ayudante": «18.0»
  }
}
```

Guárdelo como `shared/references/tarifas.json`.

**Calibración del estimador.** Las horas base de `perfil.py` (`HORAS_BASE`) están
calibradas sobre encargos tipo. Para ajustarlas a la realidad del despacho,
registre en `shared/references/historico-encargos.json` los **drivers y las horas
reales** de 3-5 encargos ya cerrados. Sin esa calibración, trate el rango
optimista/esperado/pesimista como orientativo, no como base de oferta.

---

## 6. Perfiles ERP de los clientes *(a completar)*

La ingesta detecta la cabecera y las columnas automáticamente, pero con perfiles
concretos pasa de heurística a determinista. Añada aquí los programas que usan
sus clientes habituales y cualquier peculiaridad de su salida:

| ERP | Peculiaridad observada |
|---|---|
| «A3 / Sage 50 / Contasol / Holded / SAP B1» | «p. ej.: el saldo de la columna F incluye la apertura» |

---

## 7. Reglas de comportamiento del plugin

Son **innegociables**. Cualquier skill que las incumpla está mal ejecutada.

1. **Determinismo.** Todo cuadre, recálculo, amortización, extrapolación de
   muestra o comparación numérica se ejecuta mediante script Python. El modelo
   interpreta, decide y redacta; **el script calcula**. Nunca se estima un número
   "a ojo" ni se transcribe un cálculo hecho mentalmente.
2. **Cero invención.** Ninguna cifra, fecha, cláusula o referencia normativa sin
   origen verificable y con traza. Si falta, `[PENDIENTE-CLIENTE]`; si requiere
   criterio, `[JUICIO-AUDITOR]`.
3. **Reporte por excepción.** Conclusión + excepciones + evidencia. Nunca
   volcados masivos. El resumen en pantalla no pasa de **15 líneas**.
4. **Proporcionalidad graduada.** El alcance lo fija el perfil de complejidad
   calculado, no una plantilla única.
5. **Justificabilidad.** Cada decisión metodológica relevante queda documentada
   con su fundamento, redactada para que **un revisor externo competente la
   reconstruya sin explicaciones adicionales**.
6. **Autocontrol.** Ninguna skill cierra sin pasar su checklist de
   autoverificación final.
7. **El plugin asiste, no decide ni firma.** Toda conclusión relevante es una
   propuesta fundamentada sujeta a la validación del auditor firmante.
8. **Si la evidencia no basta, se dice.** Nunca se concluye igualmente.
9. **Nunca se reduce el alcance por debajo de lo defendible** para ahorrar
   tiempo. Si el atajo no es justificable, se dice y se propone la alternativa
   correcta con su coste.
10. **Confidencialidad.** La documentación del cliente está sujeta a deber de
    secreto (art. 31 LAC), a la normativa de prevención del blanqueo y al
    RGPD/LOPDGDD. No se expone ni se reutiliza fuera del encargo.
11. **Registro de asistencia por IA.** Toda ejecución con `--encargo` se anota
    automáticamente en `uso-ia.log`: skill, versión, entradas con su SHA-256,
    salidas, parámetros, conclusión y **quién validó el resultado**. Lo exige el
    sistema de gestión de la calidad (NIGC1-ES) y da estructura al uso
    responsable de IA (ISO/IEC 42001).

    La entrada nace **sin validar**. El auditor la valida después:

    ```bash
    dula validar <encargo> --entrada IA-0003 --quien "MJ Pérez"
    ```

    `revision-de-calidad` reporta como excepción (`CAL-091`) toda ejecución sin
    validar cuyo resultado se haya incorporado a un papel **concluido**. La
    validación acredita que un auditor ha revisado el resultado de la
    herramienta, no solo que la herramienta se ejecutó.

---

## 8. Ejecución de los scripts

El plugin expone el lanzador **`dula`** en el `PATH` del Bash mientras está
activo. No hace falta exportar `PYTHONPATH` ni saber dónde se ha instalado: el
lanzador se localiza a sí mismo, verifica que hay Python 3.10+ con las
dependencias, y da un mensaje accionable si falta algo.

```bash
dula doctor              # comprueba instalación y configuración
dula <subcomando> --help
```

Dependencias: `pandas` y `openpyxl`. Nada más — sin dependencias exóticas que
compliquen la instalación en los equipos del despacho.

Subcomandos: `doctor` · `nuevo` · `estimar` · `ingesta` · `materialidad` ·
`leasing` · `financiacion` · `amortizaciones` · `asientos` · `reservas` ·
`muestreo` · `analiticos` · `comparar` · `calidad` · `estado` · `horas` · `pbc` ·
`validar`.

Argumentos comunes a los que generan papel: `--papel` `--cliente` `--ejercicio`
`--encargo` `--horas` `--riesgos`. Con `--encargo`, el papel se registra en el
estado y la ejecución en la bitácora **sin que haya que hacer nada más**.

Verificación de la instalación: `dula doctor` debe decir «El plugin es
operativo», y `python3 tests/run_all.py` debe devolver **236/236 comprobaciones
superadas y 100 % de cobertura**.
