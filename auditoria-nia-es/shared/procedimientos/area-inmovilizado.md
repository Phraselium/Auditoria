# area-inmovilizado

> Área A — Altas, bajas, recálculo integral de amortizaciones e indicios de deterioro.

> **Cuándo:** Úsala cuando haya saldos en los grupos 20, 21 o 22, cuando el cliente aporte el inventario de inmovilizado, o cuando haya que verificar la dotación a la amortización. Términos: audita, inmovilizado, material, intangible, inversiones, inmobiliarias, recálculo, integral, amortizaciones, elemento, prorrateo, activación, gastos, indicios.

> **Necesita:** `[inventario.xlsx] [inicio] [fin]`

---
**Cuentas del área:** 20x, 21x, 22x, 23x · 28x amortización acumulada · 29x deterioro · 68x dotación · 77x/67x resultados por enajenación

La mecánica (carga del programa escalado, ejecución, generación del papel de
trabajo, conclusión y registro) la aporta la guía `areas-de-campo`. Aquí está el **criterio
específico del área** y su programa de trabajo.

## Riesgos típicos

| Riesgo | Afirmaciones |
|---|---|
| Gastos activados que no cumplen los requisitos de reconocimiento | exactitud, existencia |
| Amortización mal calculada en altas y bajas del ejercicio | exactitud |
| Elementos totalmente amortizados o fuera de uso que siguen en balance | existencia, valoración |
| Indicios de deterioro no evaluados | valoración |
| Bajas no registradas | existencia |

## Criterio específico del área

**Activación de gastos.** El error más frecuente en PYME no es la amortización:
es activar lo que es gasto (reparaciones presentadas como mejoras) o gastar lo
que es activo. Revisa las altas del ejercicio contra su factura y pregunta si
**amplían la capacidad, la productividad o la vida útil**. Si solo mantienen la
capacidad, son gasto.

**Vida útil contable vs. fiscal.** Un coeficiente igual al máximo de la tabla del
art. 12.1 LIS es un indicio de que la vida útil se ha fijado por criterio fiscal.
No es un error por sí mismo, pero exige comprobar que responde a la vida
económica real. El script lo marca como `AMO-020` (informativa).

**Sobreamortización arrastrada.** Amortización acumulada superior a la base
amortizable (`AMO-012`) es habitual en inventarios antiguos mal mantenidos.
Evalúa si es corrección de error (NRV 22ª) y su efecto en la comparativa.

**Existencia física.** En perfil ESTÁNDAR y COMPLEJO, inspecciona físicamente una
muestra de las altas del ejercicio y de los elementos de mayor valor neto
contable. Una hoja de inventario no acredita la existencia.

## Programa de trabajo

El programa escalado por perfil está en
`shared/references/programas/inmovilizado.md`. Se carga bajo demanda: no lo copies aquí.

## Ejecución

```bash
audita amortizaciones 00-fuentes/inventario.xlsx 2025-01-01 2025-12-31 \
    --cliente "<CLIENTE>" --ejercicio 2025 --papel "01-papeles/A-1 Inmovilizado.xlsx"
```

## Checklist de autoverificación

Además de la checklist común de `areas-de-campo`:

- [ ] El movimiento del ejercicio cuadra con el balance en coste y en amortización acumulada.
- [ ] La dotación recalculada se ha contrastado elemento a elemento, no en global.
- [ ] Las altas y bajas están prorrateadas por días.
- [ ] Ningún elemento tiene amortización acumulada superior a su base amortizable sin explicación.
- [ ] Los elementos totalmente amortizados en uso están identificados y desglosados en memoria.
- [ ] Se ha evaluado la existencia de indicios de deterioro.
