# evaluacion-de-incorrecciones

> Sumario de ajustes corregidos y no corregidos, con su evaluación cualitativa y efecto en la opinión.

> **Cuándo:** Úsala en la fase de cierre, antes de redactar el informe, y cada vez que un área proponga un ajuste. Términos: elabora, sumario, ajustes, reclasificaciones, corregidas, calcula, efecto, acumulado, epígrafe, evalúa, cuantitativa, cualitativamente, incorpora, ejercicio.

> **Necesita:** `[carpeta-del-encargo]`

---
## Qué entra en el sumario

Toda diferencia detectada que supere el **umbral de incorrecciones claramente
insignificantes** (5 % de la materialidad global). Por debajo no se acumula,
**salvo que por su naturaleza sea cualitativamente significativa**.

| Tipo | Definición |
|---|---|
| **Factual** | Incorrección sobre la que no hay duda |
| **De juicio** | Diferencia derivada del juicio de la dirección sobre una estimación que el auditor considera irrazonable |
| **Proyectada** | La mejor estimación del auditor sobre el error en una población, extrapolada desde la muestra |

Las tres se acumulan. Omitir las proyectadas es un error frecuente que hace que el
sumario infravalore el efecto real.

## Registro

```python
enc.añade_incorreccion(
    area="C", descripcion="Ventas de diciembre correspondientes al ejercicio siguiente",
    efecto_resultado=-18_400.00, efecto_patrimonio=-18_400.00,
    epigrafe="1", tipo="factual", corregida=False,
    cualitativa="Afecta al cumplimiento del covenant de EBITDA mínimo y al "
                "cálculo de la retribución variable de la dirección.")
```

## La evaluación cualitativa no es opcional

Una incorrección puede ser **cuantitativamente inmaterial y cualitativamente
significativa**. `CAL-041` exige que toda no corregida tenga su evaluación
cualitativa. Los factores a considerar:

- ¿Afecta al cumplimiento de **covenants** o de requisitos legales?
- ¿Afecta a la **clasificación** entre partidas (corriente/no corriente,
  patrimonio/pasivo)?
- ¿Afecta a las **retribuciones de la dirección** o a la retribución variable?
- ¿Convierte una pérdida en beneficio, o al revés?
- ¿Afecta a un desglose cuya exigencia legal no depende del importe (partes
  vinculadas, retribuciones al órgano de administración)?
- ¿**Revela un sesgo de la dirección**? Varias incorrecciones pequeñas en la misma
  dirección no son ruido: son un patrón, y es el hallazgo más importante que puede
  producir esta skill.
- ¿Enmascara un cambio de tendencia?

## Incorrecciones no corregidas del ejercicio anterior

Se arrastran y se acumulan (`ejercicio_anterior=True`). Su efecto sobre el
**resultado** del ejercicio actual puede ser el contrario al que tuvieron en el
anterior (efecto de reversión), mientras que su efecto sobre el **balance**
persiste. Hay que evaluar ambos enfoques y quedarse con el más restrictivo.

## Conclusión y efecto en la opinión

| Situación | Efecto |
|---|---|
| Efecto agregado **inferior** a la materialidad global y sin significatividad cualitativa | Opinión favorable |
| Efecto agregado **superior** a la materialidad global | Opinión **con salvedades** o **desfavorable**, según la generalización |
| Efecto inferior pero **cualitativamente significativo** | Evaluar caso a caso; puede exigir salvedad |
| Efecto **próximo** a la materialidad | Reconsiderar si la materialidad sigue siendo apropiada y si hay riesgo de incorrecciones no detectadas |

`CAL-040` lo verifica automáticamente y `CAL-060` detecta la incoherencia de
proponer opinión favorable con incorrecciones que superan la materialidad.

## Comunicación a la dirección

Todas las incorrecciones acumuladas se comunican, con solicitud de corrección. Si
la dirección se niega, hay que **entender por qué**: la negativa a corregir un
ajuste claro es en sí misma información sobre la actitud de la dirección y
alimenta la evaluación del riesgo de fraude.

## Outputs

- `01-papeles/8.1 Sumario de incorrecciones.xlsx` — corregidas y no corregidas,
  efecto por epígrafe y acumulado, evaluación cualitativa, arrastre del ejercicio
  anterior y conclusión sobre la materialidad.

## Checklist de autoverificación

- [ ] Todas las áreas han registrado sus ajustes propuestos.
- [ ] Las incorrecciones proyectadas del muestreo están incluidas.
- [ ] Cada no corregida tiene **evaluación cualitativa** redactada.
- [ ] Las no corregidas del ejercicio anterior están arrastradas.
- [ ] El efecto acumulado se contrasta contra la materialidad **global vigente**.
- [ ] Se ha evaluado si el conjunto revela un sesgo de la dirección.
- [ ] La conclusión sobre el tipo de opinión se ha trasladado a `redaccion-informe`.
- [ ] Las incorrecciones se han comunicado a la dirección y consta su respuesta.
