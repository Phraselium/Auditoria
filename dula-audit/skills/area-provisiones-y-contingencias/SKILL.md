---
name: area-provisiones-y-contingencias
description: 'Audita provisiones y pasivos contingentes: circularización de abogados, evaluación de litigios en curso, verificación del cálculo de las provisiones y del desglose de los pasivos contingentes. Úsala cuando haya litigios, reclamaciones, saldos en el grupo 14 o 499, o cuando la circularización bancaria revele avales.'
---

# Área K — Provisiones y contingencias

**Cuentas del área:** 14x provisiones a largo · 499/529 provisiones a corto · 695/795 dotación y exceso

La mecánica (carga del programa escalado, ejecución, generación del papel de
trabajo, conclusión y registro) la aporta `area-runner`. Aquí está el **criterio
específico del área** y su programa de trabajo.

## Riesgos típicos

| Riesgo | Afirmaciones |
|---|---|
| Litigios o reclamaciones no comunicados por la dirección | integridad |
| Provisión infravalorada o pasivo contingente sin desglosar | valoración, desglose |
| Provisiones dotadas sin obligación presente (alisamiento del resultado) | existencia |

## Criterio específico del área

**La circularización de abogados es el procedimiento central**, y su valor está en
enviarla a **todos** los abogados que hayan facturado durante el ejercicio, no
solo a los que la dirección declare. Cruza las cuentas 623 (servicios de
profesionales independientes) para identificarlos: el abogado que ha facturado y
del que la dirección no habla es exactamente el que hay que circularizar.

**El árbol de decisión de la NRV 15ª:**

| Probabilidad de salida de recursos | Tratamiento |
|---|---|
| Probable y estimable con fiabilidad | **Provisión** en balance |
| Probable pero no estimable con fiabilidad | Pasivo contingente: **desglose** en memoria |
| Posible | Pasivo contingente: **desglose** en memoria |
| Remota | No se reconoce ni se desglosa |

**Provisiones dotadas sin obligación presente.** Es el reverso del riesgo
habitual: una provisión genérica «para riesgos» sin obligación identificada es una
incorrección y una posible herramienta de alisamiento del resultado. Conecta con
el riesgo de sesgo de la dirección del `mapa-de-riesgos`.

**Avales y garantías.** Los revelados por las confirmaciones bancarias
(`CIR-020`) son pasivos contingentes y deben desglosarse. Es una de las
conexiones entre áreas que más se pierde.

## Programa de trabajo

El programa escalado por perfil está en
`shared/references/programas/provisiones-y-contingencias.md`. Se carga bajo demanda: no lo copies aquí.

## Ejecución

```bash
dula muestreo 00-fuentes/mayor_623.xlsx importe --metodo dirigido \
    --materialidad <MP> --excel "01-papeles/K-1 Abogados a circularizar.xlsx"
```

## Checklist de autoverificación

Además de la checklist común de `area-runner`:

- [ ] Se ha circularizado a TODOS los abogados que han facturado, no solo a los declarados por la dirección.
- [ ] Cada litigio está evaluado individualmente contra el árbol de decisión de la NRV 15ª.
- [ ] Los avales revelados por las confirmaciones bancarias están desglosados.
- [ ] Las provisiones sin obligación presente identificada están cuestionadas.
- [ ] Los pasivos contingentes están desglosados en memoria con su naturaleza y efecto estimado.
