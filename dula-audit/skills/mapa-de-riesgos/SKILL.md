---
name: mapa-de-riesgos
description: Identifica y valora los riesgos de incorrección material por área y por afirmación, situando cada uno en el espectro de riesgo inherente y motivando la valoración con los factores concurrentes. Incluye la presunción de fraude en el reconocimiento de ingresos, el riesgo de elusión de controles por la dirección, los riesgos significativos y la evaluación del entorno de TI y los controles generales. Produce la matriz de riesgos vinculada a los procedimientos que los responden. Úsala en planificación, tras el entendimiento de la entidad, o cuando aparezca un hallazgo que obligue a reevaluar el riesgo.
---

# Mapa de riesgos (NIA-ES 315 Revisada y 240)

## Inputs

Entendimiento de la entidad, balance ya cuadrado, comparativa con el ejercicio
anterior, analíticos preliminares, informe del auditor predecesor si lo hay, y
las incidencias de la campaña anterior.

## 1. Espectro de riesgo inherente

La NIA-ES 315 (Revisada) no pide una etiqueta alto/medio/bajo: pide situar el
riesgo en un **espectro**, motivado por los **factores de riesgo inherente** que
concurren. Los factores a evaluar en cada riesgo:

| Factor | Pregunta |
|---|---|
| Complejidad | ¿El cálculo o el criterio contable es complejo? |
| Subjetividad | ¿Hay estimación, juicio o rango de valores razonables? |
| Cambio | ¿Ha cambiado el negocio, el sistema, la norma o el personal? |
| Incertidumbre | ¿El desenlace depende de hechos futuros? |
| Susceptibilidad a sesgo o fraude | ¿La dirección tiene incentivo o presión sobre esta partida? |

Cuanto más arriba en el espectro y más factores concurran, más probable es que
sea un **riesgo significativo** — el que exige respuesta específica y pruebas de
detalle.

## 2. Riesgos que se presumen siempre

No se identifican: **ya están**. Lo que se documenta es cómo se responden, o —solo
para el primero— por qué se rebate.

1. **Fraude en el reconocimiento de ingresos** (NIA-ES 240.25). Presunción
   rebatible. Si se rebate, hay que documentar el razonamiento; el silencio no
   vale.
2. **Elusión de controles por la dirección** (NIA-ES 240.31). Presunción **no**
   rebatible, en toda entidad, sea cual sea su tamaño. Respuesta obligatoria:
   `test-asientos-diario`, revisión de estimaciones en busca de sesgo, y examen
   de las operaciones significativas fuera del curso normal del negocio.

## 3. Riesgos típicos de la cartera de Dula

Punto de partida, no lista cerrada. El catálogo completo por área está en
`shared/references/catalogo-riesgos.md`.

| Área | Riesgo | Afirmación | Espectro típico |
|---|---|---|---|
| C | Corte de operaciones de diciembre / reconocimiento anticipado | Ocurrencia, corte | Alto |
| C | Deterioro de saldos antiguos no reconocido | Valoración | Medio-alto |
| F | Arrendamiento financiero clasificado como operativo | Clasificación, integridad | Alto |
| E | Deuda no registrada; avales y garantías no desglosados | Integridad | Alto |
| E | Reparto corriente/no corriente no actualizado al cierre | Clasificación | Medio |
| H | Pasivos no registrados al cierre | Integridad | Alto |
| A | Gastos activados que no cumplen los requisitos | Exactitud | Medio |
| A | Amortización mal calculada en altas y bajas | Exactitud | Bajo-medio |
| B | Valoración de existencias y obsolescencia | Valoración | Alto |
| G | Reservas indisponibles mal dotadas o dispuestas | Presentación | Medio |
| J | Recuperabilidad de activos por impuesto diferido | Valoración | Medio-alto |
| M | Operaciones vinculadas no declaradas ni desglosadas | Integridad, desglose | Alto |

## 4. Entorno de TI y controles generales

En una PYME no hay un departamento de sistemas, pero **sí hay riesgo de TI**. Lo
que hay que valorar, proporcionado al tamaño:

- ¿El ERP permite **modificar o eliminar asientos ya contabilizados**? Si sí, los
  huecos de numeración detectados en `ingesta-y-cuadres` cobran otra dimensión.
- ¿Hay **segregación de funciones** o una sola persona hace todo?
- ¿Quién tiene **usuario administrador** y qué puede hacer?
- ¿La facturación está **integrada** con la contabilidad o se repica a mano?
- ¿Hay copias de seguridad y se ha probado su restauración?

La respuesta condiciona directamente si es viable confiar en controles
(procedimiento 5 de `diseno-de-pruebas`) o si todo el enfoque debe ser sustantivo.

## 5. Procedimiento

1. Recorre cada área con saldo o movimiento significativo.
2. Para cada una, identifica los riesgos **por afirmación** (existencia,
   integridad, exactitud, corte, valoración, clasificación, presentación y
   desglose). Un riesgo sin afirmación asignada no es accionable.
3. Sitúa cada riesgo en el espectro y **enumera los factores concurrentes**. La
   valoración sin factores es una etiqueta, no una valoración.
4. Marca los significativos y los de fraude.
5. Registra en `encargo.json`:
   ```python
   enc.añade_riesgo(id="R001", area="C", afirmacion="ocurrencia",
                    descripcion="...", espectro="alto",
                    factores=["susceptibilidad a sesgo", "cambio"],
                    significativo=True, fraude=True)
   ```
6. Pasa el mapa a `diseno-de-pruebas`, que asigna las respuestas.

## 6. Reevaluación durante el trabajo

El mapa **no es un documento de planificación que se archiva**. Cuando aparezca
un hallazgo que contradiga la valoración inicial (una incorrección material en un
área valorada como riesgo bajo, un indicio de fraude, una deficiencia de control),
vuelve aquí, reevalúa, y ejecuta `escalado-del-encargo` para comprobar si el
trabajo ya realizado se ha quedado corto.

## Outputs

- `01-papeles/1.5 Mapa de riesgos.xlsx` — matriz área × afirmación × riesgo, con
  espectro, factores, significatividad y respuestas vinculadas.
- Riesgos registrados en `encargo.json`.

## Checklist de autoverificación

- [ ] Todas las áreas con saldo o movimiento significativo están cubiertas.
- [ ] Cada riesgo tiene **afirmación** asignada.
- [ ] Cada valoración enumera los **factores de riesgo inherente** concurrentes.
- [ ] La presunción de fraude en ingresos está respondida o **rebatida por
      escrito**.
- [ ] El riesgo de elusión de controles por la dirección está incluido, sin
      excepción.
- [ ] El entorno de TI está evaluado, aunque la entidad sea pequeña.
- [ ] Los riesgos significativos están marcados como tales.
- [ ] Ningún riesgo queda sin respuesta asignada al pasar a la fase de campo.
