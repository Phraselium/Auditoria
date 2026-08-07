---
name: area-arrendamientos
description: Procesa en lote contratos de arrendamiento en formatos dispares (contratos, cuadros de la entidad financiera, facturas de cuota), extrae sus términos, recalcula el tipo implícito, clasifica financiero/operativo con motivación, construye el cuadro de cuotas por año, periodifica la carga financiera, reparte corriente/no corriente y concilia con las cuentas 174 y 524. Diseñada para cientos de contratos. Úsala cuando el cliente tenga leasings o rentings, cuando aparezcan saldos en 174/524, o cuando haya que verificar el desglose de arrendamientos de la memoria.
---

# Área F — Arrendamientos

**Prueba crítica de eficiencia.** El caso real de referencia: un transportista con
~100 camiones en arrendamiento financiero. A mano son tres días. Con esta skill,
unas horas.

## Qué gana y qué no gana esta skill

**Gana, y por goleada:** cálculo del tipo implícito, cuadro de cuotas,
periodificación de la carga financiera, reparto corriente/no corriente,
conciliación con la contabilidad y cuadro de vencimientos para la memoria. Todo
determinista, sobre el **100 % de la población**. No hace falta muestrear para la
verificación aritmética.

**No gana:** la lectura de contratos en PDF escaneado de calidad irregular. Esa
sigue siendo humana. El diseño lo asume: la extracción declara **confianza por
campo**, y todo lo que baje de 0,85 va a revisión documental obligatoria. El
muestreo se reserva **solo** para verificar los términos extraídos contra el
contrato original.

## Inputs

Cualquier combinación de:
- Cuadros de amortización de las entidades financieras (un fichero por entidad,
  cada uno con su nomenclatura de columnas).
- Relación interna de contratos de la entidad.
- Extracciones de Data Sniper / OCR sobre los contratos en PDF.
- Saldos contables de las cuentas 174 y 524.

**No hace falta homogeneizar los ficheros.** El emparejador de columnas trabaja
por palabras y reconoce las variantes habituales (`Nº Contrato` / `Referencia` /
`id`, `Importe financiado` / `Principal` / `Nominal`, `Cuota mensual` / `Importe
cuota` / `Mensualidad`...).

## Procedimiento

**1. Consolidar los ficheros de las distintas entidades.**

```python
import pandas as pd
from dula import ingesta, leasing

dfs = [ingesta.lee_tabla(f)[0] for f in FICHEROS]
contratos = pd.concat([leasing.normaliza_lote(d) for d in dfs], ignore_index=True)
contratos["_fila_origen"] = range(2, len(contratos) + 2)
```

`normaliza_lote` es idempotente: consolidar ficheros ya normalizados no pierde
campos.

**2. Procesar el lote.**

```bash
export PYTHONPATH=<plugin>/shared/scripts
python3 -m dula.cli leasing 00-fuentes/contratos_consolidados.xlsx 2025-12-31 \
    --saldo-174 <saldo> --saldo-524 <saldo> \
    --cliente "<CLIENTE>" --ejercicio 2025 \
    --papel "01-papeles/F-1 Arrendamientos.xlsx" \
    --excel "01-papeles/F-1 Anexo cuadros.xlsx"
```

**3. Revisar las excepciones.** Solo eso. Los contratos que cuadran no requieren
tu atención.

| Código | Excepción |
|---|---|
| `ARR-001` | Faltan datos esenciales — no se ha calculado |
| `ARR-002` | Extracción con confianza < 0,85 — verificación documental obligatoria |
| `ARR-003` | La suma de pagos mínimos no supera el importe financiado: **financieramente imposible** |
| `ARR-010` | Clasificación financiero/operativo **no concluida** |
| `ARR-020` | Tipo implícito recalculado ≠ tipo declarado por la entidad (> 0,25 p.p.) |
| `ARR-030` | Deuda viva recalculada ≠ saldo contable del contrato |
| `ARR-040` | El total del área no cuadra con las cuentas 174 / 524 |

## La clasificación financiero / operativo

Se motiva **indicador a indicador** conforme a la NRV 8ª del PGC. Basta que
concurra **uno** para presumir arrendamiento financiero:

1. Transferencia de la propiedad al finalizar el plazo.
2. Opción de compra cuyo precio hace que no existan dudas razonables de que se
   ejercitará (umbral operativo: opción ≤ 1,5 cuotas).
3. El plazo cubre la mayor parte de la vida económica del activo (umbral: ≥ 75 %).
4. El valor actual de los pagos mínimos ≈ el valor razonable del activo
   (umbral: ≥ 90 %).
5. Activo de naturaleza tan especializada que solo el arrendatario puede usarlo.

**Regla que no se negocia:** cuando no concurre ninguno **pero falta información**
para descartarlos (típicamente el valor razonable o la vida útil), la
clasificación es `DUDOSO` y se eleva a `[JUICIO-AUDITOR]`. **Nunca se clasifica
como operativo por defecto solo porque falten datos** — ese es precisamente el
error que la entidad tiene incentivo a cometer, porque saca la deuda del balance.

## Interpretación de ARR-020

Una diferencia sistemática de 0,5-1 p.p. entre el tipo recalculado y el declarado
suele tener una de estas dos causas, y conviene distinguirlas antes de proponer
nada:

- **Comisiones de apertura y gastos de formalización** no incluidos en el cálculo
  de la entidad → deben incorporarse al coste amortizado.
- **La opción de compra no está en los flujos** con los que la entidad calculó la
  cuota, o base 360/365 distinta → normalmente no requiere ajuste.

## Outputs

- `01-papeles/F-1 Arrendamientos.xlsx` — conclusión, resumen por contrato con su
  motivación de clasificación, cuadro por ejercicio, cuadro detallado, traza y
  excepciones.
- **Cuadro de vencimientos por ejercicio** (cuotas, carga financiera, capital)
  listo para el desglose de la memoria.
- Reparto corriente/no corriente para la reclasificación de cierre.

## Checklist de autoverificación

- [ ] Se han ingerido **todos** los ficheros de contratos, de todas las entidades.
- [ ] El nº de contratos procesados + los reportados como no calculables = el
      total ingerido. **No se ha perdido ninguno por el camino.**
- [ ] En cada contrato, la suma del capital amortizado del cuadro = el importe
      financiado (verificación aritmética independiente).
- [ ] Corriente + no corriente = deuda viva, contrato a contrato.
- [ ] Todo contrato `FINANCIERO` u `OPERATIVO` tiene motivación redactada.
- [ ] Ningún contrato se ha clasificado como operativo por falta de datos.
- [ ] Los de confianza < 0,85 están marcados para verificación documental.
- [ ] La conciliación con 174 y 524 está ejecutada y cuadra, o su diferencia está
      explicada y propuesta como ajuste.
- [ ] El cuadro de vencimientos cubre todos los ejercicios hasta el último
      vencimiento.
- [ ] Se ha verificado el desglose de la memoria contra el cuadro generado.
