---
name: area-tesoreria-y-financiacion
description: Audita tesorería y financiación: conciliaciones bancarias, gestión y seguimiento de las confirmaciones bancarias incluidos avales, garantías, pignoraciones y saldos indirectos, normalización de cuadros de amortización heterogéneos, recálculo de deuda viva, reparto corriente/no corriente, intereses devengados, coste amortizado y verificación de covenants. Escala desde tres créditos hasta carteras de pólizas, confirming y factoring.
---

# Área D y E — Tesorería y financiación

**Cuentas del área:** 57x tesorería · 52x deudas a corto · 17x deudas a largo · 16x deudas con grupo · 66x gastos financieros

La mecánica (carga del programa escalado, ejecución, generación del papel de
trabajo, conclusión y registro) la aporta `area-runner`. Aquí está el **criterio
específico del área** y su programa de trabajo.

## Riesgos típicos

| Riesgo | Afirmaciones |
|---|---|
| Deuda financiera no registrada | integridad |
| Avales, garantías y pignoraciones no desglosados | integridad, desglose |
| Reparto corriente/no corriente no actualizado al cierre | clasificación |
| Intereses devengados no periodificados | corte, exactitud |
| Gastos de formalización llevados a resultados en lugar de a coste amortizado | valoración |
| Incumplimiento de covenants no detectado | clasificación, empresa en funcionamiento |

## Criterio específico del área

**La confirmación bancaria de TODAS las entidades es obligatoria en todos los
perfiles.** No solo de aquellas con saldo: también de aquellas con las que la
entidad ha operado durante el ejercicio aunque cierren a cero. Es la única forma
de probar la **integridad** del pasivo financiero y de detectar los **riesgos
indirectos** (avales, garantías, pignoraciones, líneas no dispuestas) que la
dirección no siempre comunica.

**Cuadros heterogéneos.** Ningún banco entrega el mismo formato. El emparejador
de columnas trabaja por palabras y absorbe la mayoría de las variantes. Lo que no
absorbe se reporta como excepción, no se adivina.

**Productos revolving.** Pólizas, confirming y factoring no tienen cuadro de
amortización: la deuda viva es el dispuesto y el reparto corriente/no corriente
depende del **vencimiento del límite**. Sin fecha de vencimiento, todo va a
corriente y se reporta la limitación (`FIN-001`).

**Excedidos en póliza** (`FIN-002`): dispuesto superior al límite concedido.
Puede indicar excedido no regularizado o reducción del límite por la entidad. Su
efecto sobre los covenants suele ser el problema real.

**Covenants.** Un incumplimiento a la fecha de cierre puede convertir deuda no
corriente en corriente y, en casos graves, activar dudas sobre empresa en
funcionamiento. **Sin waiver de fecha anterior al cierre, se reclasifica.** Es una
de las comprobaciones que más se olvidan y de las que más efecto tienen.

## Programa de trabajo

El programa escalado por perfil está en
`shared/references/programas/tesoreria-y-financiacion.md`. Se carga bajo demanda: no lo copies aquí.

## Ejecución

```bash
export PYTHONPATH=<plugin>/shared/scripts
python3 -m dula.cli financiacion 00-fuentes/cartera.xlsx 2025-12-31 \
    --confirmaciones 00-fuentes/confirmaciones.xlsx --covenants 00-fuentes/covenants.xlsx \
    --cliente "<CLIENTE>" --ejercicio 2025 --papel "01-papeles/E-1 Financiacion.xlsx"
```

## Checklist de autoverificación

Además de la checklist común de `area-runner`:

- [ ] Se ha circularizado a TODAS las entidades, no solo a las que tienen saldo.
- [ ] Las confirmaciones sin respuesta tienen procedimiento alternativo y su suficiencia evaluada.
- [ ] Los avales, garantías y pignoraciones revelados por las confirmaciones están desglosados en memoria.
- [ ] Corriente + no corriente = deuda viva, instrumento a instrumento.
- [ ] Los covenants están verificados y, si hay incumplimiento, consta el waiver o la reclasificación.
- [ ] Las conciliaciones bancarias no tienen partidas pendientes sin explicar.
