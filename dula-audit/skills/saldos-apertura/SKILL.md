---
name: saldos-apertura
description: Ejecuta los procedimientos sobre los saldos iniciales y la información comparativa en primeros encargos, y evalúa el efecto en la opinión si no se obtiene evidencia suficiente y adecuada. Úsala cuando el encargo sea el primero con este cliente, cuando el ejercicio anterior no estuviera auditado, o cuando el auditor predecesor emitiera una opinión modificada.
---

# Saldos de apertura (NIA-ES 510 y 710)

## Los tres escenarios y lo que cambia en cada uno

| Escenario | Procedimientos | Efecto potencial |
|---|---|---|
| Ejercicio anterior **auditado por otro auditor con opinión favorable** | Revisión de sus papeles de trabajo previa autorización; verificación de que la apertura coincide con su cierre | Normalmente ninguno |
| Ejercicio anterior **auditado con opinión modificada** | Evaluar si la causa persiste al cierre del ejercicio actual | Si persiste, afecta también a este informe |
| Ejercicio anterior **no auditado** | Procedimientos sustantivos completos sobre los saldos de apertura significativos | Si no se obtiene evidencia, **limitación al alcance** |

## Procedimientos sobre saldos no auditados

No se auditan «los saldos de apertura» en abstracto: se audita **cada uno de los
significativos** con el procedimiento que le corresponde.

| Saldo | Procedimiento sobre la apertura |
|---|---|
| Clientes y proveedores | Cobros y pagos posteriores; circularización con corte a la fecha de apertura |
| Tesorería | Conciliación bancaria a la fecha de apertura |
| Inmovilizado | Reconstrucción del inventario y recálculo de la amortización acumulada desde el origen |
| Existencias | El más difícil: si no se asistió al recuento de apertura, rara vez hay procedimiento alternativo suficiente |
| Deuda financiera | Confirmación bancaria con saldo a la fecha de apertura; cuadros de amortización |
| Fondos propios | Escrituras, actas y cuentas depositadas |
| Provisiones y contingencias | Circularización de abogados con alcance retroactivo |

## Efecto en el informe

| Situación | Opinión |
|---|---|
| No se obtiene evidencia suficiente sobre los saldos de apertura | **Con salvedades o denegada**, según la generalización del efecto |
| Los saldos de apertura contienen una incorrección que afecta al ejercicio actual | **Con salvedades o desfavorable** |
| Los saldos de apertura contienen una incorrección que **no** afecta al ejercicio actual pero sí a la comparativa | Salvedad **referida a la comparativa** |
| El ejercicio anterior no fue auditado | **Párrafo de otras cuestiones** indicándolo (NIA-ES 710.14) |

**Existencias de apertura no verificadas**: afecta al resultado del ejercicio
actual a través del consumo. Es el caso que con más frecuencia produce salvedad
en primeros encargos y conviene advertirlo al cliente **antes** de aceptar.

## Conexión con la aceptación

Este trabajo tiene coste y se estima en `estimacion-encargo` (driver
`primer_encargo`, +8 puntos y multiplicador 1,15 sobre las horas). Si el cliente
no autoriza la comunicación con el auditor predecesor, el coste sube y el riesgo
también: valóralo en la decisión de aceptación, no después.

## Checklist de autoverificación

- [ ] Está determinado cuál de los tres escenarios aplica.
- [ ] En caso de auditor predecesor, consta la solicitud de acceso a sus papeles y
      su resultado.
- [ ] Cada saldo de apertura significativo tiene su procedimiento ejecutado.
- [ ] La apertura cuadra con el cierre anterior (`CUA-042`) o las diferencias
      están explicadas.
- [ ] Si el ejercicio anterior no fue auditado, el informe incluye el párrafo de
      otras cuestiones.
- [ ] El efecto en la opinión está evaluado y trasladado a `redaccion-informe`.
