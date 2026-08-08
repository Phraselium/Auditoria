# aceptacion-e-independencia

> Evalúa independencia e incompatibilidades y genera la declaración firmable y la carta de encargo.

> **Cuándo:** Úsala antes de aceptar cualquier encargo y al renovarlo cada ejercicio. Términos: evalúa, documentada, amenazas, independencia, salvaguardas, incompatibilidades, legales, propias, personas, vinculadas, concentración, honorarios, servicios, distintos.

> **Necesita:** `[cliente] [ejercicio]`

---
Se ejecuta **antes** de aceptar y **se repite cada ejercicio** en los recurrentes:
las circunstancias cambian y la independencia es una evaluación continuada, no un
trámite de la primera vez.

## 1. Amenazas y salvaguardas

Las cinco categorías de amenaza del Código de Ética del IESBA, que inspiran la
práctica española:

| Amenaza | Situación típica en un despacho mediano |
|---|---|
| **Interés propio** | Honorarios significativos respecto del total de la firma; honorarios pendientes de cobro de ejercicios anteriores; relación de negocio con el cliente |
| **Autorrevisión** | Haber participado en la elaboración de la contabilidad, de las cuentas anuales o de los cálculos que después se auditan |
| **Abogacía** | Defender la posición del cliente ante la Administración o ante terceros |
| **Familiaridad** | Relación personal o familiar con la dirección; muchos años consecutivos con el mismo cliente y el mismo equipo |
| **Intimidación** | Amenaza de sustitución; presión sobre el contenido del informe o sobre los honorarios |

Por cada amenaza identificada: **nivel** (¿supera un nivel aceptable?),
**salvaguarda aplicada**, y **conclusión** sobre si la independencia queda
comprometida. Si una amenaza no puede reducirse a un nivel aceptable, **no se
acepta el encargo**. Esa conclusión también hay que documentarla.

## 2. Incompatibilidades legales (LAC arts. 14-20)

Se verifican sobre el auditor, sobre la **red** y sobre las **personas
vinculadas**:

- Cargos directivos o de administración en la entidad.
- Interés financiero directo o indirecto significativo.
- Relación laboral, comercial o de negocio.
- Prestación de servicios de contabilidad o de preparación de estados financieros.
- Servicios de valoración con efecto material en las cuentas.
- Servicios de auditoría interna, de diseño de sistemas de TI financieros,
  jurídicos o de defensa fiscal ante los tribunales.
- **Concentración de honorarios**: límites del art. 20 LAC.
- **Rotación**: obligatoria en EIP conforme al Reglamento (UE) 537/2014.

## 3. Prevención del blanqueo de capitales

Los auditores son **sujetos obligados**. Antes de aceptar:

- Identificación formal del cliente y de su **titular real**.
- Identificación del propósito y la naturaleza de la relación de negocio.
- Comprobación de listas de sanciones y de personas con responsabilidad pública.
- Evaluación del riesgo del cliente y de su sector.

## 4. Competencia y recursos

- ¿Tiene el despacho conocimiento del sector?
- ¿Hay **personal disponible en el calendario del encargo**? Es la restricción que
  más se ignora y la que después produce trabajo apresurado y mal documentado.
- ¿Hace falta un experto (valoración, actuarial, TI)?

## 5. Comunicación con el auditor predecesor

Obligatoria en primeros encargos. Solicita autorización del cliente por escrito;
**si la deniega, es un indicio a valorar en la decisión de aceptación**, y así hay
que documentarlo.

## Outputs

- `01-papeles/0.1 Aceptacion y evaluacion de independencia.xlsx`
- `02-documentos/Declaracion de independencia.docx` — firmable por todo el equipo
  (plantilla en `plantillas/declaracion-independencia.md`)
- `02-documentos/Carta de encargo.docx` — adaptada al encargo, no genérica
  (plantilla en `plantillas/carta-encargo.md`)
- Fase `aceptacion` marcada como `completa` en `encargo.json`

## Checklist de autoverificación

- [ ] Las cinco categorías de amenaza están evaluadas, aunque la conclusión sea
      que no concurren.
- [ ] Cada amenaza identificada tiene salvaguarda y conclusión.
- [ ] Las incompatibilidades se han verificado sobre la red y sobre personas
      vinculadas, no solo sobre el auditor firmante.
- [ ] La concentración de honorarios está calculada.
- [ ] Constan las comprobaciones de prevención del blanqueo y la identificación
      del titular real.
- [ ] La disponibilidad real del equipo en el calendario está confirmada.
- [ ] En primeros encargos, consta la comunicación con el predecesor o el motivo
      por el que no se ha producido.
- [ ] La declaración de independencia está firmada por **todo** el equipo.
- [ ] La carta de encargo está adaptada, no es la plantilla en bruto.
