---
name: area-clientes-e-ingresos
description: 'Audita clientes e ingresos: circularización y procedimientos alternativos, corte de operaciones, antigüedad y deterioro, reconocimiento de ingresos incluida la respuesta a la presunción de fraude de la NIA-ES 240, y conciliación de ingresos con el IVA repercutido. Úsala siempre que haya cifra de negocios: es un área obligatoria en todo encargo.'
---

# Área C — Clientes e ingresos

**Cuentas del área:** 43x clientes · 490/493 deterioro · 70x ventas · 477 IVA repercutido

La mecánica (carga del programa escalado, ejecución, generación del papel de
trabajo, conclusión y registro) la aporta `area-runner`. Aquí está el **criterio
específico del área** y su programa de trabajo.

## Riesgos típicos

| Riesgo | Afirmaciones |
|---|---|
| Reconocimiento de ingresos antes del devengo (presunción de fraude, NIA-ES 240.25) | ocurrencia, corte |
| Saldos de clientes antiguos sin deterioro reconocido | valoración |
| Ingresos no registrados | integridad |
| Notas de abono posteriores al cierre que anulan ventas del ejercicio | ocurrencia |

## Criterio específico del área

**La presunción de fraude en el reconocimiento de ingresos siempre está** (NIA-ES
240.25). Solo puede rebatirse documentando el razonamiento. Las respuestas que
mejor funcionan en la cartera de Dula:

- **Análisis mensual de la facturación** (`analiticos.evolucion_mensual`). La
  concentración en diciembre es la señal más barata y más productiva.
- **Corte de operaciones** sobre las últimas facturas del ejercicio y las
  primeras del siguiente, contra el albarán de entrega o el parte de servicio.
- **Notas de abono posteriores al cierre**: revisa las emitidas en el primer
  trimestre siguiente y verifica a qué ejercicio corresponde el ingreso anulado.

**Conciliación ingresos ↔ IVA repercutido.** Barata y muy eficaz para la
afirmación de integridad: ventas del ejercicio × tipo aplicable, contrastado con
el IVA repercutido declarado en los modelos 303 y en el 390. Las diferencias
tienen explicación (operaciones exentas, intracomunitarias, distintos tipos) pero
deben cuadrar una vez explicadas.

**Deterioro.** El listado de antigüedad de saldos es el punto de partida, pero no
la conclusión: comprueba los **cobros posteriores al cierre**, que es la mejor
evidencia sobre la recuperabilidad.

## Programa de trabajo

El programa escalado por perfil está en
`shared/references/programas/clientes-e-ingresos.md`. Se carga bajo demanda: no lo copies aquí.

## Ejecución

```bash
export PYTHONPATH=${CLAUDE_PLUGIN_ROOT}/shared/scripts
python3 -m dula.cli muestreo 00-fuentes/mayor_clientes.xlsx debe --metodo mus \
    --materialidad <MP> --semilla <n> --excel "01-papeles/C-1 Muestra clientes.xlsx"
```

## Checklist de autoverificación

Además de la checklist común de `area-runner`:

- [ ] La presunción de fraude en el reconocimiento de ingresos tiene respuesta ejecutada o consta rebatida por escrito.
- [ ] El corte de operaciones se ha probado contra evidencia de entrega, no solo contra la factura.
- [ ] La conciliación con el IVA repercutido cuadra o sus diferencias están explicadas.
- [ ] Los saldos vencidos significativos tienen verificación de cobro posterior.
- [ ] Las no respondidas de la circularización tienen procedimiento alternativo documentado y su suficiencia evaluada.
