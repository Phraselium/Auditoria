---
name: ingesta-y-cuadres
description: Normaliza el balance de sumas y saldos, el libro diario, los mayores y las cuentas anuales de cualquier ERP, y ejecuta la batería completa de cuadres de integridad (debe=haber, diario↔sumas y saldos, apertura↔cierre anterior, resultado, correlativos y huecos de numeración, asientos fuera de ejercicio, mapeo a epígrafes). Es la PUERTA DE ENTRADA obligatoria al trabajo de campo. Úsala en cuanto llegue la contabilidad del cliente, antes de cualquier prueba de área. NO la uses para comparar cuentas anuales con memoria (eso es comparador-documental).
---

# Ingesta y cuadres de integridad

**Puerta de entrada.** Si algo no cuadra, el proceso se detiene y lo reporta.
Ninguna prueba de área se ejecuta sobre una base que no cuadra: sería trabajo
tirado y evidencia inservible.

## Cuándo se dispara

- Llega la contabilidad del cliente (balance, diario, mayores).
- El cliente envía una **nueva versión** de un fichero ya trabajado — la huella
  SHA-256 lo detecta y obliga a repetir los cuadres.
- Antes de cualquier skill de área. Sin `2.1` concluido, no se abre ninguna.

## Inputs

| Input | Obligatorio |
|---|---|
| Balance de sumas y saldos al máximo detalle (8-10 dígitos, 6-8 grupos) | **Sí** |
| Libro diario del ejercicio con fecha, cuenta, concepto, usuario | Muy recomendable |
| Balance de sumas y saldos del ejercicio anterior | Recomendable |
| Cuentas anuales formuladas | No (se usan en `comparador-documental`) |

Se aceptan `.xlsx`, `.xls`, `.csv`, `.txt` y `.tsv`, con la cabecera en cualquier
fila, las columnas en cualquier orden y los importes en formato español
(`1.234,56`, `(1.234,56)`). **No pidas al cliente que cambie el formato.**

## Procedimiento

```bash
export PYTHONPATH=${CLAUDE_PLUGIN_ROOT}/shared/scripts
python3 -m dula.cli ingesta 00-fuentes/sumas_y_saldos.xlsx \
    --diario 00-fuentes/diario.xlsx \
    --anterior 00-fuentes/sumas_y_saldos_anterior.xlsx \
    --ejercicio 2025 --cliente "<CLIENTE>" \
    --papel "01-papeles/2.1 Cuadres.xlsx" --encargo .
```

### Cuadres que se ejecutan

| Código | Cuadre | Severidad si falla |
|---|---|---|
| CUA-001 | Total debe = total haber | BLOQUEANTE |
| CUA-002 | Suma de saldos = 0 | BLOQUEANTE |
| CUA-003 | Saldo = debe − haber, cuenta a cuenta | RESOLVER |
| CUA-010 | Diario ↔ sumas y saldos, cuenta a cuenta | BLOQUEANTE |
| CUA-020 | Cada asiento cuadra individualmente | BLOQUEANTE |
| CUA-021 | Correlativos y huecos de numeración | RESOLVER |
| CUA-030/031 | Asientos fuera del ejercicio auditado | RESOLVER |
| CUA-040/042 | Apertura ↔ cierre del ejercicio anterior | RESOLVER |
| CUA-050/051 | Resultado grupos 6/7 ↔ cuenta 129 | BLOQUEANTE |
| CUA-060 | Cuentas con saldo sin epígrafe asignado | RESOLVER |

### Balances pre y post regularización

El script detecta en qué estado llega el balance y **adapta la comprobación**:

- **Pre-regularización** (lo habitual al pedir el balance a 31/12): los grupos 6
  y 7 conservan saldo y la 129 está a cero. El resultado es −(suma de saldos 6/7).
- **Post-regularización**: los grupos 6 y 7 tienen movimiento pero saldo cero. El
  resultado **no puede deducirse del balance**: hace falta el diario para excluir
  el asiento de regularización. Sin diario, la comprobación **no se ejecuta y así
  se hace constar** — no se da por bueno un cuadre que no se ha hecho.

### Huecos de numeración

Un hueco no es un error por sí mismo (asientos anulados, numeración por diarios
separados). Pero si son **eliminaciones tras contabilización**, es un indicio de
elusión de controles por la dirección. Obtén explicación del cliente y, si
procede, alimenta el riesgo correspondiente en `mapa-de-riesgos` (NIA-ES 240).

### Cuentas sin mapeo

Las cuentas de creación libre fuera del cuadro PGC se reportan **una a una con su
saldo**. Asigna el epígrafe manualmente y añade la regla a
`shared/references/mapeo-pgc.json` para que el cliente no vuelva a generarla la
próxima campaña.

## Outputs

- `01-papeles/2.1 Cuadres.xlsx` — conclusión, sumas y saldos normalizados,
  epígrafes agregados, traza y excepciones.
- Ficheros fuente registrados en `encargo.json` con su **SHA-256**.
- Resumen en pantalla y **código de salida 2** si algún cuadre bloqueante falla.

## Si un cuadre bloqueante falla

1. **No continúes.** No abras ninguna skill de área.
2. Identifica la causa con la sugerencia que da la excepción.
3. La causa más frecuente en la práctica: extracción parcial del fichero, filas
   de subtotal leídas como datos, o diario de un rango de fechas distinto.
4. Solicita nueva extracción y **repite la ingesta completa**, no solo el cuadre
   que falló.

## Checklist de autoverificación

- [ ] Todos los cuadres se han ejecutado, no solo los que tenían datos.
- [ ] Los cuadres que **no se han podido ejecutar** figuran como excepción
      explicando por qué, no como "sin incidencias".
- [ ] Cada fichero fuente está registrado con su SHA-256 en `encargo.json`.
- [ ] Las cuentas sin mapeo están todas reportadas con su saldo.
- [ ] El papel `2.1` tiene conclusión redactada y hoja de traza poblada.
- [ ] Si hay bloqueantes, el estado del papel es `en curso`, **no** `concluido`.
- [ ] El resumen en pantalla no pasa de 15 líneas.
