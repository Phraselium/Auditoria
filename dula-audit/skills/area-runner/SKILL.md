---
name: area-runner
description: Motor común de ejecución de las áreas de trabajo de campo. Carga el programa de trabajo del área escalado por perfil, ejecuta los procedimientos, genera el papel de trabajo en formato estándar, concluye y registra el resultado en el estado del encargo. Las skills area-* delegan aquí toda la mecánica y solo aportan el criterio específico de su área. Úsala cuando ejecutes cualquier área de trabajo de campo o cuando necesites entender cómo se estructura un papel de trabajo del despacho.
---

# Motor de áreas

Las doce áreas de trabajo de campo comparten el 80 % de su mecánica. Ese 80 %
vive aquí; lo específico de cada área vive en su `SKILL.md` (el criterio) y en su
pack de programa (los procedimientos). Así no hay doce copias del mismo texto
desincronizándose entre sí.

## Secuencia que ejecuta toda área

**1. Comprobar la puerta de entrada.** Si el papel `2.1` no está `concluido`, se
detiene. No se trabaja sobre una contabilidad que no cuadra.

**2. Cargar el programa escalado.** Lee `shared/references/programas/<area>.md` y
selecciona los procedimientos del perfil vigente (`LIGERO` / `ESTÁNDAR` /
`COMPLEJO`), tomado de `encargo.json`.

**3. Recuperar el contexto.** Del estado del encargo: materialidad de ejecución
vigente, riesgos asignados al área, procedimientos elegidos en
`diseno-de-pruebas` y su alcance.

**4. Ejecutar.** Todo cálculo por script. Las funciones disponibles por área están
en la tabla de abajo.

**5. Generar el papel de trabajo.** Formato único de cuatro hojas:

```python
from dula.excel_out import PapelDeTrabajo
p = PapelDeTrabajo("<REF>", "<Título>", "<CLIENTE>", <EJERCICIO>)
p.alcance("...").fundamento("...").riesgos(["R001", "R002"])
p.detalle(df, "Detalle", totales=["importe"])
p.trazas(registro).excepciones(res.excepciones)
p.concluye("...", "LIMPIO" | "CON EXCEPCIONES" | "BLOQUEADO")
p.guardar("01-papeles/<REF> <Título>.xlsx")
```

**6. Concluir.** La conclusión responde a tres preguntas, siempre: **qué se ha
probado**, **con qué alcance**, y **a qué resultado se llega respecto de las
afirmaciones cubiertas**. Una conclusión de una línea no es una conclusión
(`CAL-011`).

**7. Registrar.**

```python
enc.registra_papel("<REF>", "<Título>", ruta, conclusion, ["R001"], "concluido")
enc.registra_excepciones(res.excepciones, "<REF>")
enc.guardar()
```

**8. Proponer ajustes.** Toda diferencia que suponga una incorrección se registra
con `enc.añade_incorreccion(...)`, marcando si está corregida y con su evaluación
cualitativa. Lo que no se registre aquí, no llegará a
`evaluacion-de-incorrecciones` ni al informe.

## Funciones de cálculo por área

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

## Reglas comunes a todas las áreas

1. **El script calcula, el modelo concluye.** Ningún importe se obtiene de una
   estimación mental.
2. **Reporte por excepción.** La hoja de detalle contiene todo; el resumen en
   pantalla, solo las excepciones. Máximo 15 líneas.
3. **Traza obligatoria.** Cada cifra relevante del papel tiene su
   `fichero!hoja!celda` en la hoja de traza.
4. **Nada se rellena en silencio.** Falta un dato → `[PENDIENTE-CLIENTE]`. Hace
   falta criterio → `[JUICIO-AUDITOR]`.
5. **Vinculación al riesgo.** Un papel sin riesgo asignado es un procedimiento
   huérfano y `revision-de-calidad` lo reporta.
6. **Escalado en dos direcciones.** El perfil simplifica, pero si aparece un
   hallazgo que invalida la simplificación, `escalado-del-encargo` eleva el
   perfil y avisa de qué trabajo se ha quedado corto.

## Checklist de autoverificación (aplica a toda área)

- [ ] El papel `2.1` estaba concluido antes de empezar.
- [ ] Se ha usado el programa del perfil vigente, no otro.
- [ ] Todos los procedimientos del programa se han ejecutado o consta por qué no.
- [ ] Todo cálculo procede de un script, no de una estimación.
- [ ] La conclusión responde a qué, con qué alcance y con qué resultado.
- [ ] Los riesgos del área están vinculados al papel.
- [ ] Las diferencias se han registrado como incorrecciones propuestas.
- [ ] El papel se ha registrado en `encargo.json` con estado `concluido`.
- [ ] La hoja de traza está poblada.
