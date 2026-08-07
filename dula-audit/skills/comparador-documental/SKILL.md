---
name: comparador-documental
description: Compara sistemáticamente cuentas anuales, balance de sumas y saldos, mayores, memoria, cuentas depositadas en el Registro Mercantil, borradores sucesivos, informe de gestión, documentación soporte e informe de auditoría, y reporta SOLO las diferencias con importe, cuenta, origen y causa sugerida. Incluye la checklist de desgloses obligatorios de memoria por modelo. Úsala cuando lleguen cuentas anuales o borradores, cuando haya que cuadrar la memoria, cuando el cliente envíe una nueva versión, y SIEMPRE antes de firmar el informe. NO la uses para los cuadres internos de la contabilidad (eso es ingesta-y-cuadres).
---

# Comparador documental

El núcleo de la automatización. Es lo que sustituye a la revisión visual de
cuadros comparados a mano, que es donde el despacho pierde más horas y donde más
se escapan las cosas.

## Cuándo se dispara

| Situación | Comparación |
|---|---|
| Llegan las cuentas anuales formuladas | CCAA ↔ sumas y saldos |
| Hay que revisar la memoria | Memoria ↔ estados financieros + checklist de desgloses |
| Hay ejercicio anterior o cuentas depositadas | Comparativa ↔ anterior ↔ Registro Mercantil |
| El cliente envía una versión nueva del borrador | Diff con impacto por epígrafe |
| Existe informe de gestión | Informe de gestión ↔ CCAA (NIA-ES 720R) |
| Hay contratos, facturas, extractos o escrituras | Soporte ↔ registro contable |
| **Antes de firmar** | Informe de auditoría ↔ CCAA definitivas |

## Inputs

Cada comparación necesita sus dos lados. Lo que no esté, **no se compara y se
hace constar** — nunca se da por cuadrado lo que no se ha comparado.

## Procedimiento

```bash
export PYTHONPATH=<plugin>/shared/scripts

# 1. Cuentas anuales <-> balance de sumas y saldos
python3 -m dula.cli comparar --ccaa 00-fuentes/ccaa.json \
    --sumas-y-saldos 00-fuentes/sumas_y_saldos.xlsx

# 2. Memoria <-> estados financieros + checklist de desgloses
python3 -m dula.cli comparar \
    --memoria-desgloses 00-fuentes/memoria_desgloses.json \
    --estados 00-fuentes/estados.json \
    --memoria-texto 00-fuentes/memoria.txt \
    --memoria-anterior 00-fuentes/memoria_anterior.txt \
    --modelo PYME --contexto '{"arrendamientos": true, "subvenciones": true}'

# 3. Ejercicio <-> anterior <-> cuentas depositadas en el Registro Mercantil
python3 -m dula.cli comparar --ccaa ccaa.json --anterior-ccaa ccaa_anterior.json \
    --depositadas ccaa_depositadas.json

# 4. Informe de gestion <-> cuentas anuales (NIA-ES 720R)
python3 -m dula.cli comparar --ccaa ccaa.json --informe-gestion informe_gestion.json

# 5. Documentacion soporte <-> registro contable
python3 -m dula.cli comparar --soporte facturas.xlsx --contabilidad mayor_400.xlsx \
    --clave "n factura" --columna-importe importe

# 6. Diff entre borradores
python3 -m dula.cli comparar --borrador-anterior v1.json --borrador-nuevo v2.json

# 7. ULTIMA VERIFICACION antes de la firma
python3 -m dula.cli comparar --informe informe.json --ccaa-definitivas ccaa_def.json \
    --papel "01-papeles/9.1 Verificacion previa a la firma.xlsx"
```

### Los dos motores

**Motor numérico (determinista).** Compara importes con tolerancia de 1,00 € (las
cuentas anuales se formulan redondeadas). Reporta el importe de cada diferencia,
si el concepto falta en un lado, y la causa más probable.

**Motor de desgloses (criterio + referencia).** Contrasta la memoria contra
`shared/references/desgloses-memoria.json`, que recoge las 25 notas por modelo
(PYME / ABREVIADA / NORMAL) con su contenido mínimo y su base normativa. Las
notas condicionales solo se exigen si el supuesto concurre: pásalo en `--contexto`.

Detecta tres cosas distintas:

| Código | Hallazgo |
|---|---|
| `MEM-001` | Desglose obligatorio ausente |
| `MEM-002` | **Párrafo con cifras idéntico al del ejercicio anterior** — nota heredada sin actualizar |
| `CMP-020` | El desglose no cuadra con el estado financiero del que procede |

`MEM-002` merece atención: un párrafo descriptivo puede repetirse legítimamente,
pero uno **que contiene cifras** y se repite literalmente es casi siempre una nota
que nadie ha tocado.

### La verificación previa a la firma (9.1)

Es la última red de seguridad y sus fallos son **BLOQUEANTES**. Contrasta
denominación social, NIF, ejercicio, fecha de cierre, marco aplicado, modelo,
fecha de formulación, total activo, patrimonio neto, resultado y cifra de
negocios. Los errores que se cuelan aquí —un ejercicio mal escrito, una cifra de
un borrador anterior— son los que producen las incidencias más embarazosas en
inspección.

**Si esta comparación arroja un bloqueante, no se firma.** Sin excepción.

## Outputs

- `01-papeles/2.10 Comparador documental.xlsx`
- `01-papeles/9.1 Verificacion previa a la firma.xlsx`
- Resumen por excepción en pantalla, máximo 15 líneas.

## Advertencias de uso

- El motor de desgloses busca **términos** en el texto de la memoria. Que una
  nota figure como presente **no significa que esté completa**: el contraste
  numérico lo hace el motor numérico, y la suficiencia del contenido es
  `[JUICIO-AUDITOR]`.
- Si el balance está post-regularización, pásale el diario con `--diario` para
  que la cuenta de resultados pueda reconstruirse. Sin diario, la PyG saldrá a
  cero y el comparador reportará diferencias contra las cuentas anuales — que es
  exactamente lo que debe hacer, pero no es la incidencia real.

## Checklist de autoverificación

- [ ] Se han ejecutado **todas** las comparaciones para las que había datos.
- [ ] Las comparaciones no ejecutadas figuran como excepción con el motivo.
- [ ] Cada diferencia lleva importe, origen y causa sugerida.
- [ ] La checklist de memoria se ha corrido con el modelo correcto y el contexto
      del encargo (`arrendamientos`, `subvenciones`, `existencias`...).
- [ ] Se ha buscado la herencia de notas del ejercicio anterior.
- [ ] Si hay cuentas depositadas en el Registro Mercantil, se han comparado
      (`--depositadas`): una diferencia ahí es una reformulación o una corrección
      de error que debe estar desglosada.
- [ ] Si existe informe de gestión, se ha contrastado contra las cuentas
      (`--informe-gestion`, NIA-ES 720R).
- [ ] Si el encargo está en fase de firma, la verificación `9.1` está ejecutada y
      **sin bloqueantes**.
- [ ] No se ha volcado la comparación completa: solo las diferencias.
