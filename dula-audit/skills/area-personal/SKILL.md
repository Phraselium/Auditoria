---
name: area-personal
description: Audita el área de personal: conciliación de nóminas, seguros sociales y contabilidad, indemnizaciones, provisiones por obligaciones con el personal y retenciones. Úsala cuando haya gastos de personal significativos, que es prácticamente siempre.
---

# Área I — Personal

**Cuentas del área:** 640/641 sueldos · 642 Seguridad Social · 649 otros gastos sociales · 465 remuneraciones pendientes · 476 organismos SS · 4751 retenciones

La mecánica (carga del programa escalado, ejecución, generación del papel de
trabajo, conclusión y registro) la aporta `area-runner`. Aquí está el **criterio
específico del área** y su programa de trabajo.

## Riesgos típicos

| Riesgo | Afirmaciones |
|---|---|
| Gastos de personal no registrados (pagas extra, indemnizaciones, atrasos) | integridad, corte |
| Indemnizaciones por despido sin provisionar | integridad |
| Retribuciones a la dirección no desglosadas en memoria | desglose |
| Retenciones no ingresadas | integridad |

## Criterio específico del área

**El analítico de esta área es especialmente eficaz** porque la expectativa se
construye con datos totalmente independientes del registro contable: número medio
de empleados × coste medio del convenio aplicable. Una desviación relevante
apunta a personal no registrado, a retribuciones extraordinarias o a un error de
imputación.

```python
from dula import analiticos
analiticos.expectativa(
    "Gastos de personal", valor_registrado=..., valor_esperado=n_empleados * coste_medio,
    base_calculo="Nº medio de empleados según TC2 × coste medio del convenio",
    materialidad_ejecucion=...)
```

**Conciliación en tres puntos.** Nóminas ↔ TC1/TC2 de la Seguridad Social ↔
contabilidad. Las tres deben cuadrar; las diferencias tienen explicación
(bonificaciones, incapacidades temporales) pero deben conciliarse.

**Retribuciones a la dirección.** Su desglose en memoria **no admite el criterio
de importancia relativa por importe** (art. 260 LSC): se desglosa siempre. Es uno
de los desgloses más omitidos. Aplica una materialidad específica más baja para
esta partida.

**Indemnizaciones.** Revisa los despidos del ejercicio y los del periodo posterior
hasta la fecha del informe: un despido comunicado antes del cierre genera
obligación aunque se pague después.

## Programa de trabajo

El programa escalado por perfil está en
`shared/references/programas/personal.md`. Se carga bajo demanda: no lo copies aquí.

## Ejecución

```bash
export PYTHONPATH=<plugin>/shared/scripts
python3 -m dula.cli analiticos 00-fuentes/personal_actual.json \
    00-fuentes/personal_anterior.json --materialidad <MP> \
    --papel "01-papeles/I-1 Personal.xlsx"
```

## Checklist de autoverificación

Además de la checklist común de `area-runner`:

- [ ] La conciliación nóminas ↔ seguros sociales ↔ contabilidad cuadra.
- [ ] El analítico se ha construido con datos independientes del registro auditado.
- [ ] Las retribuciones a la dirección están desglosadas en memoria, con independencia de su importe.
- [ ] Los despidos del ejercicio y posteriores están revisados y sus indemnizaciones provisionadas.
- [ ] El devengo de pagas extra y vacaciones está verificado.
