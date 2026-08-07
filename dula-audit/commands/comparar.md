---
description: Ejecuta el comparador documental sobre cuentas anuales, memoria, borradores o el informe
argument-hint: [qué comparar]
---

Compara: $ARGUMENTS

Invoca `comparador-documental` y ejecuta **todas** las comparaciones para las que
haya datos:

- Cuentas anuales formuladas ↔ balance de sumas y saldos
- Memoria ↔ cifras de los estados financieros
- Memoria ↔ checklist de desgloses obligatorios del modelo aplicable
- Memoria ↔ memoria del ejercicio anterior (notas heredadas sin actualizar)
- Ejercicio ↔ ejercicio anterior ↔ cuentas depositadas en el Registro Mercantil
- Borradores sucesivos (diff con impacto por epígrafe)
- Informe de gestión ↔ cuentas anuales
- Documentación soporte ↔ registro contable

Las comparaciones que **no** puedas ejecutar por falta de datos, repórtalas como
excepción con el motivo. Nunca las des por cuadradas.

Si el encargo está en fase de firma, ejecuta además la verificación `9.1` del
informe contra las cuentas anuales definitivas. **Cualquier bloqueante ahí impide
firmar.**
