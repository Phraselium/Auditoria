# test-asientos-diario

> Selecciona los asientos inusuales del diario. Obligatorio en todo encargo.

> **Cuándo:** Es obligatorio en todo encargo: úsala siempre que dispongas del libro diario. Términos: selecciona, asientos, inusuales, diario, respuesta, riesgo, elusión, controles, dirección, contrapartidas, atípicas, raramente, utilizadas, manuales.

> **Necesita:** `[diario.xlsx] [fecha-cierre]`

---
**Obligatorio en todo encargo, sin excepción.** El riesgo de elusión de los
controles por la dirección se presume presente en toda entidad, sea cual sea su
tamaño, y esta presunción **no es rebatible**.

## Ejecución

```bash
dula asientos 00-fuentes/diario.xlsx 2025-12-31 \
    --materialidad <MP> --perfil ESTANDAR \
    --cliente "<CLIENTE>" --ejercicio 2025 \
    --papel "01-papeles/2.8 Test de asientos.xlsx"
```

## Los nueve filtros y su peso

| Filtro | Peso | Por qué |
|---|---|---|
| Ingreso sin contrapartida en clientes ni tesorería | 5 | Respuesta directa a la presunción de fraude en ingresos |
| Contrapartida no habitual | 4 | Combinación de cuentas que no se repite en el ejercicio |
| Asiento de los últimos 5 días del ejercicio | 3 | Los ajustes de cierre son donde se concentra el juicio |
| Sin descripción ni concepto | 3 | Un asiento sin explicación es un asiento que nadie quiso explicar |
| Cuentas de utilización excepcional | 3 | Cuentas usadas 1-2 veces en todo el ejercicio |
| Usuario de baja frecuencia | 3 | Quien contabiliza poco y contabiliza esto |
| Fin de semana | 2 | Fuera del horario normal de trabajo |
| Festivo nacional | 2 | Ídem |
| Importe redondo (múltiplo de 1.000) | 2 | Los importes reales rara vez son redondos |
| Importe superior a la materialidad de ejecución | 2 | Relevancia |

En perfil `LIGERO` se aplican solo los **cuatro de mayor rendimiento** (últimos
días, importe redondo, sin descripción, ingreso sin contrapartida normal). La
reducción es de eficiencia: en poblaciones pequeñas, el perfilado de usuarios y
las cuentas raras generan ruido sin aportar. **La prueba no se elimina nunca.**

## Priorización

Los asientos se puntúan y se ordenan. Se reportan los **40 de mayor puntuación**,
y si hay más por encima del umbral se dice expresamente cuántos quedan fuera —
nunca se trunca en silencio. El objetivo no es listar 400 asientos raros: es
señalar los 15 que hay que mirar.

## Cómo interpretarlo

Un asiento seleccionado **no es un asiento irregular**. El filtro dirige la
inspección; no presume nada. Para cada uno de los reportados:

1. Obtén el soporte documental.
2. Verifica su razonabilidad y su correcta imputación.
3. Documenta la conclusión, aunque sea «asiento correcto, corresponde a X».

Un papel que lista los asientos seleccionados y no documenta qué se hizo con cada
uno **no responde al riesgo**.

## Conexiones

- Los **huecos de numeración** detectados en `ingesta-y-cuadres` (`CUA-021`), si
  son eliminaciones tras contabilización, refuerzan este riesgo.
- Las contrapartidas con cuentas 55x alimentan `area-partes-vinculadas`.
- Los asientos de ingresos de los últimos días alimentan `area-clientes-e-ingresos`.

## Requisito de datos

El diario debe incluir **fecha y usuario**. Sin usuario, tres de los nueve filtros
no se pueden aplicar y así se hace constar. Pídelo en la PBC como prioridad 1: es
una reextracción trivial para el cliente y para el auditor es la diferencia entre
ejecutar la prueba y simularla.

## Checklist de autoverificación

- [ ] La prueba se ha ejecutado, con independencia del perfil.
- [ ] El diario incluye fecha y usuario, o consta que no y qué filtros no se han
      podido aplicar.
- [ ] Los filtros aplicados corresponden al perfil vigente.
- [ ] Cada asiento reportado tiene su soporte obtenido y su conclusión documentada.
- [ ] Si se han truncado los reportados, consta cuántos quedan fuera.
- [ ] Los hallazgos se han trasladado a las áreas que correspondan.
