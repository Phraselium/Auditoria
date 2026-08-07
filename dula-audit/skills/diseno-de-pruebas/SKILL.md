---
name: diseno-de-pruebas
description: Elige para cada riesgo el procedimiento más barato que sigue siendo suficiente, con su fundamento.
when_to_use: 'Úsala tras el mapa de riesgos, cuando haya que decidir cómo probar un área, o cuando el auditor pregunte si puede reducir el alcance de una prueba. Términos: criterio, riesgo, propone, procedimiento, eficiente, siendo, suficiente, apropiado, eligiendo, analíticos, sustantivos, muestreo, estadístico, atributos.'
argument-hint: '[área o riesgo]'
---

# Diseño de pruebas — motor de criterio

> **Al invocarla, empieza por aquí.** Presenta en pantalla, en tres
> líneas y antes de hacer nada:
>
> 1. **Qué necesito:** el mapa de riesgos, el perfil del encargo y la materialidad de ejecución.
> 2. **Qué vas a recibir:** papel 1.5 con el procedimiento elegido, las alternativas descartadas y cuándo el atajo deja de ser defendible.
> 3. **El comando exacto** que voy a ejecutar, con las rutas reales.
>
> Si falta algo de lo anterior, pídelo y **no lo inventes**.

Elige **la alternativa justificable más barata**, y dice expresamente **cuándo esa
alternativa deja de ser defendible**. Ahorrar horas con un atajo que no se
sostiene ante inspección no es ahorrar: es acumular un problema.

## Inputs

Mapa de riesgos por área y afirmación, perfil del encargo, materialidad de
ejecución vigente, y el balance ya cuadrado (para conocer el tamaño y la
composición de cada población).

## Tabla de decisión

Se recorre **de arriba abajo**. Se toma la primera opción cuyas condiciones se
cumplan íntegramente.

| # | Procedimiento | Condiciones que deben cumplirse | Coste relativo |
|---|---|---|---|
| 1 | **Examen del 100 %** | Población pequeña (≤ 25-40 partidas) o muy concentrada en pocas partidas grandes | Muy bajo si la población es pequeña |
| 2 | **Analítico sustantivo con expectativa** | La relación es **predecible**; la expectativa se construye con **datos independientes** del registro auditado; el umbral de precisión se fija a priori; riesgo no significativo | El más bajo por euro cubierto |
| 3 | **Muestreo dirigido no estadístico** | Pocas partidas concentran el importe; el resto se cubre con analítico; **no se extrapola** | Bajo |
| 4 | **Muestreo estadístico MUS** | Población numerosa y homogénea; riesgo de **sobrevaloración**; se necesita extrapolar | Medio |
| 5 | **Pruebas de controles + sustantivas reducidas** | El control es **relevante, formalizado y operativo todo el ejercicio**; existe evidencia documental de su ejecución; es eficiente frente a probar todo sustantivamente | Medio-alto de entrada, rentable si cubre varios riesgos |
| 6 | **Confirmaciones externas** | Existe tercero identificable con incentivo a responder; el saldo es significativo; hay tiempo para reiterar | Alto (tiempo de calendario, no de trabajo) |
| 7 | **Prueba de recorrido** | Se necesita **entender** el flujo, no cuantificarlo | Bajo, pero **no es evidencia sustantiva suficiente por sí sola** |

## Cuándo cada atajo deja de ser defendible

Esto es lo que hay que decir en voz alta, y lo que la skill debe advertir:

| Atajo | Deja de ser defendible cuando... |
|---|---|
| Analítico sustantivo en solitario | El riesgo es **significativo** (NIA-ES 330.21 exige pruebas de detalle), o la expectativa se construye con datos del propio registro auditado, o el umbral se fija después de ver la desviación |
| Muestreo dirigido | Se pretende **concluir sobre la población entera**. No es estadístico: la conclusión se limita a lo examinado más el analítico sobre el resto |
| Confiar en controles | No hay evidencia documental de su ejecución, o se detecta **una sola desviación** en la muestra de atributos |
| Reducir la circularización | El analítico sobre clientes no concluye, o hay indicios de reconocimiento de ingresos irregular |
| No asistir al recuento | Las existencias son significativas. Los procedimientos alternativos rara vez son suficientes: si no se asistió, normalmente hay limitación al alcance |
| Prueba de recorrido como evidencia | Se usa para concluir sobre una afirmación en lugar de para entender el proceso |

## Respuestas obligatorias, no negociables

Con independencia de lo que diga la tabla de eficiencia:

1. **Test de asientos del diario** (NIA-ES 240.32.a). El riesgo de elusión de
   controles por la dirección se presume presente **siempre**. → `test-asientos-diario`
2. **Presunción de fraude en el reconocimiento de ingresos** (NIA-ES 240.25).
   Solo puede rebatirse documentando por qué no aplica; no se omite en silencio.
3. **Riesgos significativos**: exigen pruebas de detalle específicas y una
   comprensión de los controles relevantes. Un analítico no basta.
4. **Confirmación bancaria de todas las entidades**, en todos los perfiles,
   incluidos los riesgos indirectos (avales, garantías, pignoraciones).

## Procedimiento

1. Para cada riesgo del mapa, recorre la tabla de decisión.
2. Comprueba las condiciones **una a una**. Si alguna no se cumple, baja a la
   siguiente opción y **documenta por qué se descartó la anterior** — eso es lo
   que un inspector querrá leer.
3. Dimensiona el alcance con `muestreo`:
   ```bash
   dula muestreo poblacion.xlsx importe --metodo mus \
       --materialidad <MP> --riesgo 0.05 --semilla <n>
   ```
4. Estima las horas de cada prueba y súmalas. Contrasta con el presupuesto de
   `estimacion-encargo`. Si el diseño se pasa, **no recortes evidencia**: avisa de
   la desviación al socio, que es quien decide.
5. Registra en `encargo.json` la vinculación **riesgo → procedimiento → papel**.

## La regla de los huérfanos

- **Todo riesgo debe tener al menos un procedimiento que lo responda.**
- **Todo procedimiento debe responder a un riesgo identificado.**

`revision-de-calidad` falla en bloqueante si detecta huérfanos en cualquiera de
los dos sentidos. Un procedimiento sin riesgo asociado suele ser trabajo heredado
de campañas anteriores que ya no aporta: es una fuente de ahorro real.

## Outputs

- `01-papeles/1.5 Diseno de pruebas.xlsx`: por cada riesgo, procedimiento
  elegido, fundamento, condiciones verificadas, alternativas descartadas y por
  qué, alcance, semilla si aplica, y horas estimadas.
- Programas de trabajo por área, escalados por perfil, en
  `shared/references/programas/`.

## Checklist de autoverificación

- [ ] Cada riesgo tiene al menos un procedimiento asignado.
- [ ] Cada procedimiento apunta a un riesgo. **Cero huérfanos.**
- [ ] Cada elección documenta las condiciones verificadas y las alternativas
      descartadas con su motivo.
- [ ] Los riesgos significativos tienen pruebas de detalle, no solo analíticos.
- [ ] El test de asientos del diario está programado.
- [ ] La presunción de fraude en ingresos tiene respuesta, o consta rebatida y
      documentada.
- [ ] Todas las entidades financieras están incluidas en la circularización.
- [ ] Las horas suman y se han contrastado con el presupuesto.
- [ ] Donde se ha elegido la opción barata, consta expresamente qué la haría
      dejar de ser defendible.
