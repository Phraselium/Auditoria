# area-existencias

> Área B — Recuento físico, valoración, corte de operaciones y obsolescencia.

> **Cuándo:** Úsala cuando haya saldos en el grupo 3, cuando el cliente convoque el recuento, o cuando haya que evaluar el deterioro de existencias. Si la entidad no tiene existencias, no la actives. Términos: audita, existencias, asistencia, verificación, recuento, físico, valoración, operaciones, obsolescencia, márgenes.

> **Necesita:** `[inventario-valorado.xlsx]`

---
**Cuentas del área:** 30x-36x existencias · 39x deterioro · 61x variación · 71x variación de productos terminados

La mecánica (carga del programa escalado, ejecución, generación del papel de
trabajo, conclusión y registro) la aporta la guía `areas-de-campo`. Aquí está el **criterio
específico del área** y su programa de trabajo.

## Riesgos típicos

| Riesgo | Afirmaciones |
|---|---|
| Sobrevaloración por inclusión de costes indebidos o de existencias obsoletas | valoración |
| Corte de operaciones incorrecto en compras y ventas de fin de ejercicio | corte |
| Existencias en poder de terceros o de terceros en poder de la entidad | existencia, integridad |
| Valor neto realizable inferior al coste | valoración |

## Criterio específico del área

**La asistencia al recuento no es negociable si las existencias son
significativas.** Si no se asistió, los procedimientos alternativos rara vez son
suficientes y normalmente hay **limitación al alcance** con efecto en la opinión.
Dilo antes de aceptar el encargo, no después.

**Valoración.** Verifica el método declarado (coste medio ponderado o FIFO — el
LIFO no está admitido en el PGC) y **recalcúlalo** sobre una muestra de
referencias con el fichero de movimientos. Comprueba que el coste no incluye
gastos de comercialización ni financieros no capitalizables.

**Obsolescencia.** El indicador más útil es la **rotación por referencia**:
existencias / consumo del ejercicio. Las referencias con rotación superior a un
año son candidatas a deterioro con independencia de lo que diga la dirección.

**Corte.** Contrasta los últimos albaranes de entrada y salida del ejercicio y los
primeros del siguiente contra su registro contable y contra el recuento. Es donde
aparecen las incidencias reales.

## Programa de trabajo

El programa escalado por perfil está en
`shared/references/programas/existencias.md`. Se carga bajo demanda: no lo copies aquí.

## Ejecución

```bash
dula muestreo 00-fuentes/existencias.xlsx valor --metodo mus \
    --materialidad <MP> --excel "01-papeles/B-1 Muestra existencias.xlsx"
```

## Checklist de autoverificación

Además de la checklist común de `areas-de-campo`:

- [ ] El inventario valorado cuadra con el saldo contable.
- [ ] Consta si se asistió o no al recuento y, si no se asistió, el efecto en el alcance.
- [ ] El método de valoración se ha recalculado, no solo verificado documentalmente.
- [ ] El corte de operaciones se ha probado en ambos sentidos.
- [ ] Las referencias de baja rotación están evaluadas para deterioro.
