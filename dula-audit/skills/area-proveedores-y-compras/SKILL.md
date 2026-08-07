---
name: area-proveedores-y-compras
description: 'Audita proveedores y compras: conciliaciones de saldos, búsqueda de pasivos no registrados, corte de operaciones y confirmaciones. Úsala siempre que haya compras o gastos de explotación significativos. La búsqueda de pasivos no registrados es su procedimiento central y no se omite en ningún perfil.'
---

# Área H — Proveedores y compras

**Cuentas del área:** 40x proveedores · 41x acreedores · 60x compras · 62x servicios exteriores · 472 IVA soportado

La mecánica (carga del programa escalado, ejecución, generación del papel de
trabajo, conclusión y registro) la aporta `area-runner`. Aquí está el **criterio
específico del área** y su programa de trabajo.

## Riesgos típicos

| Riesgo | Afirmaciones |
|---|---|
| Pasivos no registrados al cierre | integridad |
| Corte de operaciones incorrecto en compras | corte |
| Gastos del ejercicio siguiente imputados al auditado o al revés | corte, exactitud |
| Saldos deudores en cuentas de proveedores sin justificación | clasificación |

## Criterio específico del área

**La búsqueda de pasivos no registrados es el procedimiento central del área, y
se ejecuta en todos los perfiles.** La integridad del pasivo no se prueba
circularizando: se prueba buscando lo que falta. Las cuatro fuentes que mejor
funcionan:

1. **Pagos posteriores al cierre**: revisa los movimientos bancarios del primer
   trimestre siguiente por encima de un umbral y verifica a qué ejercicio
   corresponde el gasto.
2. **Facturas recibidas tras el cierre** con fecha de devengo anterior.
3. **Cuentas de proveedores con saldo cero** que tuvieron movimiento durante el
   ejercicio: son las que más fácilmente ocultan una factura no registrada.
4. **Contratos y servicios recurrentes** (alquileres, suministros, asesorías) sin
   gasto registrado en el último mes o trimestre.

**Saldos deudores en proveedores.** Anticipos legítimos o errores. Si son
significativos, se reclasifican al activo: presentar un anticipo minorando el
pasivo es una incorrección de clasificación.

**Corte.** Contrasta los últimos albaranes de recepción del ejercicio contra su
factura y su registro contable.

## Programa de trabajo

El programa escalado por perfil está en
`shared/references/programas/proveedores-y-compras.md`. Se carga bajo demanda: no lo copies aquí.

## Ejecución

```bash
dula muestreo 00-fuentes/pagos_posteriores.xlsx importe \
    --metodo dirigido --materialidad <MP> --excel "01-papeles/H-2 Pasivos no registrados.xlsx"
```

## Checklist de autoverificación

Además de la checklist común de `area-runner`:

- [ ] La búsqueda de pasivos no registrados se ha ejecutado sobre las cuatro fuentes, no solo sobre los pagos posteriores.
- [ ] Las cuentas de proveedores con saldo cero y movimiento están revisadas.
- [ ] El corte se ha probado contra evidencia de recepción.
- [ ] Los saldos deudores están identificados y reclasificados si son significativos.
- [ ] Las diferencias de conciliación con extractos de proveedores están explicadas.
