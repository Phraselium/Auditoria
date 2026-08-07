---
name: entendimiento-entidad
description: Construye el entendimiento de la entidad y su entorno: perfil de negocio, sector, marco de información financiera aplicable, ciclos de transacciones, sistemas de TI y grado de automatización, partes vinculadas y hechos relevantes del ejercicio, aprovechando el Registro Mercantil, las cuentas depositadas, la web de la entidad y la prensa cuando estén disponibles. Úsala al inicio de la planificación, antes del mapa de riesgos.
---

# Entendimiento de la entidad (NIA-ES 315 Revisada)

No es un documento de relleno: es lo que permite que el mapa de riesgos identifique
riesgos **reales** en vez de una lista genérica de manual.

## Qué hay que entender, y para qué

| Aspecto | Para qué sirve después |
|---|---|
| Actividad, productos, clientes y mercados | Construir expectativas en los analíticos |
| Sector y su situación | Valorar el riesgo inherente y la empresa en funcionamiento |
| Estructura societaria y de propiedad | Identificar partes vinculadas |
| Marco de información financiera aplicable | Determinar el modelo de cuentas y los desgloses exigibles |
| Ciclos de transacciones | Diseñar las pruebas de recorrido y de controles |
| Sistemas de TI y automatización | Decidir si es viable confiar en controles |
| Financiación y covenants | Anticipar riesgos de clasificación y de empresa en funcionamiento |
| Hechos relevantes del ejercicio | Anticipar áreas de trabajo no recurrentes |

## Fuentes que no cuestan tiempo y se aprovechan poco

1. **Cuentas anuales depositadas** de los tres últimos ejercicios: evolución,
   informes de auditoría anteriores y sus salvedades.
2. **Nota simple del Registro Mercantil**: órgano de administración, capital,
   apoderamientos, cargas.
3. **Web de la entidad**: líneas de negocio, ubicaciones, clientes de referencia.
4. **Prensa sectorial**: situación del sector, concursos de acreedores de clientes
   o proveedores relevantes.
5. **El informe del auditor predecesor** y sus salvedades.
6. **La campaña anterior**, si es recurrente: las incidencias que se repiten son
   las que hay que anticipar.

## Determinación del marco aplicable

| Marco | Condición |
|---|---|
| PGC PYMES | Cumple los límites del art. 2 del RD 1515/2007 y no incurre en los supuestos de exclusión |
| PGC — modelo abreviado | Límites del art. 257 LSC para balance y memoria abreviados |
| PGC — modelo normal | Supera los límites |
| Consolidado | Existe grupo y no concurre dispensa |

**Compruébalo, no lo presumas.** Un cliente que ha superado los límites durante
dos ejercicios consecutivos cambia de modelo, y con él cambian los desgloses
exigibles en la memoria — que es donde `comparador-documental` detectará las
ausencias.

**Señal de alerta:** presencia de cuentas de los grupos 8 y 9 en el balance. Esas
cuentas no existen en el PGC PYMES simplificado: si están, hay que verificar qué
marco se está aplicando realmente.

## Pruebas de recorrido

Una por cada ciclo significativo (ventas, compras, tesorería, personal). Sirven
para **entender el flujo**, no para concluir sobre una afirmación: una prueba de
recorrido no es evidencia sustantiva suficiente por sí sola.

## Outputs

- `01-papeles/1.1 Entendimiento de la entidad.xlsx` — perfil, ciclos, sistemas,
  partes vinculadas identificadas, marco aplicable y su justificación.
- Alimenta directamente `mapa-de-riesgos` y `plan-y-solicitud-informacion`.

## Checklist de autoverificación

- [ ] El marco de información financiera está **determinado y justificado** contra
      los límites legales, no presumido del ejercicio anterior.
- [ ] Los ciclos significativos están identificados y descritos.
- [ ] El entorno de TI está evaluado, con su grado de automatización.
- [ ] Se han consultado las cuentas depositadas y el informe del auditor anterior.
- [ ] Las partes vinculadas identificadas se han trasladado a `area-partes-vinculadas`.
- [ ] Los hechos relevantes del ejercicio están recogidos y trasladados al mapa de
      riesgos.
