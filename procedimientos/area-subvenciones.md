# area-subvenciones

> Área L — Clasificación, condiciones, imputación a resultados y riesgo de reintegro.

> **Cuándo:** Úsala cuando haya saldos en las cuentas 130, 131, 132, 740 o 746. Si la entidad no recibe subvenciones, no la actives. Términos: audita, subvenciones, donaciones, legados, clasificación, capital, explotación, cumplimiento, condiciones, asociadas, imputación, resultados, riesgo, reintegro.

> **Necesita:** `[carpeta-del-encargo]`

---
**Cuentas del área:** 130/131/132 subvenciones de capital · 740 subvenciones de explotación · 746 imputación a resultados · 172/522 deudas por reintegro

La mecánica (carga del programa escalado, ejecución, generación del papel de
trabajo, conclusión y registro) la aporta la guía `areas-de-campo`. Aquí está el **criterio
específico del área** y su programa de trabajo.

## Riesgos típicos

| Riesgo | Afirmaciones |
|---|---|
| Subvención de capital imputada a resultados antes de tiempo | corte, exactitud |
| Condiciones de la subvención incumplidas sin reconocer el riesgo de reintegro | valoración, integridad |
| Clasificación incorrecta entre reintegrable y no reintegrable | clasificación |

## Criterio específico del área

**La clasificación depende del cumplimiento de las condiciones, no del acuerdo de
concesión.** Una subvención solo se reconoce como no reintegrable —y por tanto
directamente en patrimonio neto— cuando existe un **acuerdo individualizado de
concesión, se han cumplido las condiciones establecidas y no existen dudas
razonables sobre su recepción** (NRV 18ª). Mientras alguna condición esté
pendiente, es un pasivo.

**Lo que hay que leer, y hay que leerlo de verdad:** la resolución de concesión.
Ahí están las condiciones (mantenimiento del empleo, del activo, plazos de
justificación, obligación de permanencia) cuyo incumplimiento activa el reintegro.
Es documentación que el cliente rara vez aporta sin que se le pida expresamente.

**Imputación a resultados.** Las de capital se imputan **en proporción a la
amortización** del activo financiado, o a su baja. Recalcúlalo: es un cálculo
sencillo que se hace mal con frecuencia, sobre todo cuando el activo se amortiza
por un plazo distinto al previsto.

**Efecto fiscal.** La imputación contable y la fiscal pueden diferir. Conéctalo con
`area-fiscal`.

## Programa de trabajo

El programa escalado por perfil está en
`referencias/programas/subvenciones.md`. Se carga bajo demanda: no lo copies aquí.

## Ejecución

```bash
audita analiticos 00-fuentes/subvenciones_actual.json \
    00-fuentes/subvenciones_anterior.json --materialidad <MP> \
    --papel "01-papeles/L-1 Subvenciones.xlsx"
```

## Checklist de autoverificación

Además de la checklist común de `areas-de-campo`:

- [ ] Se han obtenido y leído las resoluciones de concesión, no solo el listado del cliente.
- [ ] Cada condición está verificada individualmente con evidencia.
- [ ] La imputación a resultados se ha recalculado en proporción a la amortización.
- [ ] El riesgo de reintegro está evaluado y, si existe, reconocido o desglosado.
- [ ] El movimiento cuadra con el ECPN.
