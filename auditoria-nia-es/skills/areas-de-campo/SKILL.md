---
name: areas-de-campo
description: Ejecuta cualquier área de trabajo de campo con su programa escalado por perfil.
when_to_use: 'Úsala para auditar un área concreta: inmovilizado, existencias, clientes e ingresos, proveedores y compras, tesorería, financiación, arrendamientos y leasings, fondos propios y reservas indisponibles, personal, fiscal, provisiones y contingencias, subvenciones, partes vinculadas, o saldos de apertura en primeros encargos. También cuando aparezcan saldos en un grupo del PGC y haya que decidir qué hacer con ellos. Términos: auditar, área, inmovilizado, amortizaciones, existencias, recuento, clientes, circularización, corte de operaciones, deterioro, proveedores, pasivos no registrados, tesorería, conciliación bancaria, financiación, covenants, leasing, arrendamiento financiero, reservas, capitalización, nóminas, impuesto sobre sociedades, impuestos diferidos, litigios, abogados, subvenciones, reintegro, partes vinculadas, saldos de apertura.'
argument-hint: <área — p.ej. arrendamientos, inmovilizado, fiscal>
---

# Áreas de trabajo de campo

Las doce áreas comparten el 80 % de su mecánica. Ese 80 % está aquí; el criterio
específico de cada una vive en su procedimiento, que se abre **solo cuando se
usa**.

> **Al invocarla, empieza por aquí.** Antes de hacer nada, di en tres líneas:
> qué área vas a ejecutar, qué necesitas del cliente y el comando exacto con las
> rutas reales. Si falta algo, pídelo y **no lo inventes**.

## 1. Elige el área y abre su procedimiento

```bash
cat ${CLAUDE_PLUGIN_ROOT}/shared/procedimientos/area-<nombre>.md
```

| Área | Ref. | Procedimiento | Cuentas |
|---|---|---|---|
| Inmovilizado | `A` | `area-inmovilizado` | 20x, 21x, 22x, 28x, 68x |
| Existencias | `B` | `area-existencias` | 3xx, 39x, 61x, 71x |
| Clientes e ingresos | `C` | `area-clientes-e-ingresos` | 43x, 490, 70x, 477 |
| Tesorería y financiación | `D` `E` | `area-tesoreria-y-financiacion` | 57x, 52x, 17x, 16x, 66x |
| Arrendamientos | `F` | `area-arrendamientos` | 174, 524, 21x, 662, 621 |
| Fondos propios y reservas | `G` | `area-fondos-propios-y-reservas` | 10x, 11x, 12x, 13x |
| Proveedores y compras | `H` | `area-proveedores-y-compras` | 40x, 41x, 60x, 62x, 472 |
| Personal | `I` | `area-personal` | 64x, 465, 476, 4751 |
| Fiscal | `J` | `area-fiscal` | 473, 474, 479, 630x, 475x |
| Provisiones y contingencias | `K` | `area-provisiones-y-contingencias` | 14x, 499, 529, 695 |
| Subvenciones | `L` | `area-subvenciones` | 130-132, 740, 746 |
| Partes vinculadas | `M` | `area-partes-vinculadas` | 16x, 24x, 44x, 55x |
| Saldos de apertura | `N-3` | `saldos-apertura` | (primeros encargos) |

Y el programa de trabajo escalado por perfil:

```bash
cat ${CLAUDE_PLUGIN_ROOT}/shared/references/programas/<área>.md
```

## 2. La secuencia, idéntica en todas las áreas

**a. Comprueba la puerta de entrada.** Si el papel `2.1` no está `concluido`, se
detiene. No se trabaja sobre una contabilidad que no cuadra.

**b. Carga el programa del perfil vigente** (`LIGERO` / `ESTÁNDAR` / `COMPLEJO`),
tomado de `encargo.json`. Los procedimientos se acumulan: ESTÁNDAR incluye los de
LIGERO, y COMPLEJO los de ambos.

**c. Recupera el contexto**: materialidad de ejecución vigente, riesgos asignados
al área y su alcance.

**d. Ejecuta.** Todo cálculo por script:

```bash
audita amortizaciones <inventario> <inicio> <fin>   # área A
audita leasing <contratos> <fecha-cierre>           # área F
audita financiacion <cartera> <fecha-cierre>        # áreas D y E
audita reservas <sumas-y-saldos>                    # área G
audita muestreo <población> <columna> --metodo mus  # cualquier área
```

| Área | Ref. | Módulo y función |
|---|---|---|
| Inmovilizado | `A` | `amortizaciones.recalcula()`, `amortizaciones.indicios_deterioro()` |
| Existencias | `B` | `analiticos.expectativa()`, `muestreo.mus()` |
| Clientes e ingresos | `C` | `analiticos.evolucion_mensual()`, `muestreo.mus()`, `comparador.soporte_vs_contabilidad()` |
| Tesorería | `D` | `financiacion.concilia_banco()`, `financiacion.seguimiento_confirmaciones()` |
| Financiación | `E` | `financiacion.procesa_cartera()`, `financiacion.verifica_covenants()` |
| Arrendamientos | `F` | `leasing.procesa_lote()`, `leasing.conciliacion_contable()` |
| Fondos propios | `G` | `plan_contable.reserva_restringida()` |
| Proveedores y compras | `H` | `comparador.soporte_vs_contabilidad()`, `muestreo.mus()` |
| Personal | `I` | `analiticos.expectativa()` |
| Fiscal | `J` | `analiticos.expectativa()` |
| Provisiones | `K` | `muestreo.dirigido()` |
| Subvenciones | `L` | `analiticos.variaciones()` |
| Partes vinculadas | `M` | `comparador.soporte_vs_contabilidad()` |

Añade siempre `--encargo . --papel "01-papeles/<REF>.xlsx" --horas <n> --riesgos R00x`:
con eso el papel, las fuentes y la bitácora se registran solos. Las horas **se
acumulan** entre sesiones: un área se trabaja en varias tandas y la desviación se
calcula sobre el total.

Desde Python, si se genera el papel a mano:

```python
from audita.excel_out import PapelDeTrabajo
p = PapelDeTrabajo("<REF>", "<Título>", "<CLIENTE>", <EJERCICIO>)
p.alcance("...").fundamento("...").riesgos(["R001", "R002"])
p.detalle(df, "Detalle", totales=["importe"])
p.trazas(registro).excepciones(res.excepciones)
p.concluye("...", "LIMPIO" | "CON EXCEPCIONES" | "BLOQUEADO")
p.guardar("01-papeles/<REF> <Título>.xlsx")

enc.registra_papel("<REF>", "<Título>", ruta, conclusion, ["R001"], "concluido",
                   horas=6.0, preparado_por="LG")
enc.registra_excepciones(res.excepciones, "<REF>")
enc.guardar()
```

**e. Concluye.** La conclusión responde a tres preguntas, **siempre**: qué se ha
probado, con qué alcance, y a qué resultado se llega respecto de las afirmaciones
cubiertas. Una conclusión de una línea no es una conclusión (`CAL-011`).

**f. Propón los ajustes.** Toda diferencia que suponga una incorrección se
registra con su evaluación cualitativa. Lo que no se registre aquí no llegará al
sumario ni al informe.

## 3. Reglas comunes, sin excepción

1. **El script calcula, tú concluyes.** Ningún importe sale de una estimación
   mental.
2. **Reporte por excepción.** La hoja de detalle lo contiene todo; la pantalla,
   solo las excepciones. Máximo 15 líneas.
3. **Traza obligatoria.** Cada cifra relevante lleva su `fichero!hoja!celda`.
4. **Nada se rellena en silencio.** Falta un dato → `[PENDIENTE-CLIENTE]`. Hace
   falta criterio → `[JUICIO-AUDITOR]`.
5. **Vinculación al riesgo.** Un papel sin riesgo asignado es un procedimiento
   huérfano, y `revision-de-calidad` lo reporta.
6. **Escalado en dos direcciones.** El perfil simplifica, pero si aparece un
   hallazgo que invalida la simplificación —indicio de fraude, incorrección
   material, deficiencia significativa de control, duda sobre empresa en
   funcionamiento, limitación al alcance, covenant incumplido, operación
   vinculada no declarada— **eleva el perfil antes de cerrar el área** y avisa de
   qué trabajo ya ejecutado se ha quedado corto.

## 4. Formato del papel de trabajo

Cuatro hojas, siempre: **Conclusión** (referencia, alcance, fundamento, riesgos
cubiertos, indicadores, firma), **Detalle** (con fórmulas `=SUM()` vivas en los
totales), **Traza** (origen de cada dato) y **Excepciones** (ordenadas por
severidad, con importe, causa sugerida y acción).

## Checklist de autoverificación

- [ ] El papel `2.1` estaba concluido antes de empezar.
- [ ] Se ha usado el programa del **perfil vigente**, no otro.
- [ ] Todos los procedimientos del programa se han ejecutado, o consta por qué no.
- [ ] Todo cálculo procede de un script, no de una estimación.
- [ ] La conclusión responde a qué, con qué alcance y con qué resultado.
- [ ] Los riesgos del área están vinculados al papel.
- [ ] Las diferencias se han registrado como incorrecciones propuestas.
- [ ] Si ha aparecido un hallazgo que invalida el perfil, se ha elevado.
- [ ] El papel está registrado en `encargo.json` con estado `concluido`.
