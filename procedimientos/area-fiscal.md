# area-fiscal

> Área J — Conciliación resultado contable ↔ base imponible, impuestos diferidos y cuadres fiscales.

> **Cuándo:** NO cubre el apartado del informe sobre transparencia fiscal país por país: eso es redaccion-informe. Términos: audita, fiscal, conciliación, contable, imponible, diferencias, permanentes, temporarias, activos, pasivos, impuesto, diferido, recuperabilidad, deducciones.

> **Necesita:** `[carpeta-del-encargo]`

---
**Cuentas del área:** 473 retenciones · 474 activos por impuesto diferido · 479 pasivos por impuesto diferido · 6300/6301 impuesto · 633/638 ajustes · 475x HP acreedora

La mecánica (carga del programa escalado, ejecución, generación del papel de
trabajo, conclusión y registro) la aporta la guía `areas-de-campo`. Aquí está el **criterio
específico del área** y su programa de trabajo.

## Riesgos típicos

| Riesgo | Afirmaciones |
|---|---|
| Activos por impuesto diferido no recuperables reconocidos en balance | valoración |
| Contingencias fiscales no provisionadas ni desglosadas | integridad |
| Diferencias temporarias no identificadas | exactitud |
| Deducciones aplicadas sin cumplir los requisitos | exactitud |

## Criterio específico del área

> **Aviso.** La nueva sección del informe relativa al «impuesto sobre sociedades»
> introducida por la RICAC de 22/01/2026 **no pertenece a esta área**. Responde a
> la DA 11ª de la LAC (transparencia fiscal país por país, umbral de 750 M€) y se
> trata en `redaccion-informe`. El trabajo de esta área es el de siempre.

**Recuperabilidad de los activos por impuesto diferido.** Es el juicio más
relevante del área y el que más se despacha con una frase. Un activo por impuesto
diferido solo se reconoce si es probable que la entidad disponga de ganancias
fiscales futuras. Exige:

- Proyecciones de la dirección, con sus hipótesis.
- Contraste de las proyecciones de ejercicios anteriores **contra lo realmente
  ocurrido** — el mejor indicador de la fiabilidad de la dirección al estimar.
- Plazo de reversión de las diferencias temporarias imponibles.

Si la entidad viene de pérdidas recurrentes, el reconocimiento es difícilmente
sostenible. Aplica NIA-ES 540 (Revisada).

**Conciliación resultado contable ↔ base imponible.** Recálculo completo con
identificación de cada diferencia permanente y temporaria. La conciliación que no
cierra es la señal de que falta una diferencia por identificar.

**Cuadres fiscales que se hacen siempre:**

| Cuadre | Contra |
|---|---|
| Ventas del ejercicio × tipo | IVA repercutido de los modelos 303 y del 390 |
| Compras y gastos × tipo | IVA soportado deducido |
| Gastos de personal y profesionales | Retenciones de los modelos 111 y del 190 |
| Arrendamientos | Retenciones del modelo 115 |
| Impuesto devengado | Modelo 200 presentado |

**Reservas con efecto fiscal.** Conéctalo con `area-fondos-propios-y-reservas`: la
reserva de capitalización y la de nivelación tienen plazos de mantenimiento cuyo
incumplimiento obliga a regularizar el incentivo aplicado.

## Programa de trabajo

El programa escalado por perfil está en
`referencias/programas/fiscal.md`. Se carga bajo demanda: no lo copies aquí.

## Ejecución

```bash
audita analiticos 00-fuentes/cifras_fiscales.json \
    00-fuentes/cifras_fiscales_anterior.json --materialidad <MP> \
    --papel "01-papeles/J-1 Fiscal.xlsx"
```

## Checklist de autoverificación

Además de la checklist común de `areas-de-campo`:

- [ ] La conciliación resultado contable ↔ base imponible cierra sin residuo sin explicar.
- [ ] Cada diferencia permanente y temporaria está identificada y documentada.
- [ ] La recuperabilidad de los activos por impuesto diferido está evaluada con evidencia, no con una manifestación.
- [ ] Los cuadres de IVA y de retenciones se han ejecutado contra los modelos presentados.
- [ ] Los ejercicios abiertos a inspección y las contingencias están identificados y desglosados.
- [ ] NO se ha confundido esta área con el apartado del informe sobre transparencia fiscal país por país.
