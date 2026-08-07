---
name: estimacion-encargo
description: Calcula el perfil de complejidad de un encargo de auditoría a partir del balance de sumas y saldos y estima horas y honorarios por área y categoría profesional, con rango optimista/esperado/pesimista y punto muerto. Úsala cuando el socio esté valorando si aceptar un cliente, fijando precio, presupuestando o planificando la carga de trabajo, o cuando pregunte "cuánto nos va a costar esto" o "qué encarece este encargo". NO la uses para planificar el trabajo de un encargo ya aceptado (eso es diseno-de-pruebas) ni para evaluar la independencia (eso es aceptacion-e-independencia).
---

# Estimación del encargo

Convierte un balance de sumas y saldos en una decisión de precio defendible.
Puntúa los drivers que de verdad mueven las horas en Dula, no los que figuran en
los manuales.

## Cuándo se dispara

- El socio ha captado un cliente y necesita fijar precio.
- El encargo llega ya cerrado y hay que dimensionar el equipo y el calendario.
- Se revisa el presupuesto a mitad de campaña porque el encargo se ha torcido.

## Inputs

| Input | Obligatorio | Notas |
|---|---|---|
| Balance de sumas y saldos al máximo detalle | **Sí** | 8-10 dígitos, 6-8 grupos, cualquier formato de ERP |
| Libro diario | No | Si está, el nº de asientos se cuenta en lugar de estimarse |
| Cuentas anuales del ejercicio anterior | No | Mejora la detección de subvenciones, vinculadas y moneda extranjera |
| Respuestas del cliente sobre los drivers cualitativos | **Sí** | Automatización de facturación, nº de leasings, historial de respuesta |
| `shared/references/tarifas.json` | No | Sin él, los honorarios salen `[PENDIENTE-CLIENTE]` |

## Procedimiento

**1. Ingesta y lectura de drivers cuantitativos.** Del balance se extraen
directamente: nº de cuentas activas, grupos presentes (6 vs. 8), existencia de
saldos en existencias (grupo 3), subvenciones (130/131/132/746), moneda
extranjera (668/768), instrumentos de financiación (17x/52x/16x/51x), leasings
(174/524) y partes vinculadas (16x/24x/44x con desglose de grupo).

```bash
export PYTHONPATH=${CLAUDE_PLUGIN_ROOT}/shared/scripts
python3 -m dula.cli ingesta <sumas_y_saldos.xlsx> --diario <diario.xlsx> --ejercicio <AAAA>
```

**2. Completar los drivers cualitativos.** Pregunta al socio **solo** lo que no
se deduce del balance, y en una sola tanda:

- ¿La facturación está automatizada, es semiautomática o se hace a mano?
- ¿Cuántos contratos de arrendamiento financiero hay, aproximadamente?
- ¿Cuántos créditos, pólizas, avales, confirming y factoring?
- ¿Cómo responde este cliente: ágil, normal, o lento/desordenado?
- ¿Es primer encargo? ¿Hay consolidación? ¿Es EIP?

**3. Puntuación y perfil.**

```bash
python3 -m dula.cli estimar drivers.json --tarifas shared/references/tarifas.json \
    --excel "02-documentos/Estimacion.xlsx" --encargo <carpeta-encargo>
```

Formato de `drivers.json`:

```json
{
  "n_asientos": 4200, "n_cuentas": 180,
  "automatizacion_facturacion": "media",
  "n_instrumentos_financiacion": 6, "n_leasings": 12,
  "existencias": "si", "subvenciones": "no",
  "operaciones_vinculadas": "si", "moneda_extranjera": "no",
  "consolidacion": "no", "primer_encargo": "no",
  "respuesta_cliente": "normal", "eip": false
}
```

**4. Interpretar y decidir.** El script entrega perfil, horas por área y
categoría, rango, honorarios, punto muerto, los 5 factores que más encarecen el
encargo con su **palanca de abaratamiento**, y la configuración del perfil.

**5. Informe de decisión para el socio.** Redáctalo en máximo una página:

- **Recomendación go / no-go**, con el motivo en una frase.
- Perfil, horas esperadas y honorario mínimo (punto muerto).
- Los 3 factores que más encarecen, con **qué pedirle al cliente para
  abaratarlo**. Esto es lo que convierte la estimación en negociación.
- Riesgos de aceptación detectados en el balance (patrimonio neto negativo,
  fondo de maniobra negativo, saldos anómalos con vinculadas).
- Qué queda `[PENDIENTE-CLIENTE]`.

## Escala de puntuación

| Driver | Máx. | Driver | Máx. |
|---|---|---|---|
| Volumen de asientos | 15 | Existencias | 10 |
| Nº de cuentas activas | 8 | Subvenciones | 8 |
| Automatización de facturación | 8 | Operaciones vinculadas | 10 |
| Créditos, pólizas, avales, confirming | 15 | Moneda extranjera | 5 |
| Leasings | 15 | Consolidación | 12 |
| Historial de respuesta del cliente | 8 | Primer encargo | 8 |

`LIGERO` ≤ 20 · `ESTÁNDAR` 21-50 · `COMPLEJO` > 50.
**Overrides duros:** EIP → COMPLEJO. Consolidación sobre LIGERO → ESTÁNDAR.

## Outputs

- `02-documentos/Estimacion <cliente> <ejercicio>.xlsx` — drivers, horas por
  área, factores y configuración del perfil.
- Perfil registrado en `encargo.json`, del que se alimenta `escalado-del-encargo`.
- Informe de decisión go/no-go en pantalla.

## Advertencias de uso

- **La estimación no calibrada es orientativa.** Si `historico-encargos.json`
  está vacío, dilo expresamente al socio: el rango sale de horas base genéricas,
  no de la experiencia del despacho.
- El ahorro por uso del plugin que aplica el modelo es **conservador** y solo se
  aplica donde el cálculo es determinista. No prometas más.
- Un perfil LIGERO **no autoriza** a recortar por debajo de lo defendible. Si el
  encargo se tuerce, `escalado-del-encargo` eleva el perfil y avisa de qué
  trabajo ya ejecutado se ha quedado corto.

## Checklist de autoverificación

- [ ] El balance se ha ingerido y **los cuadres de integridad pasan**. Sin eso,
      el recuento de cuentas y de saldos no es fiable y la estimación tampoco.
- [ ] Todos los drivers cuantitativos proceden del balance, no de una suposición.
- [ ] Los drivers cualitativos no informados figuran como `[PENDIENTE-CLIENTE]` y
      **no puntúan** (no se les asigna un valor medio por defecto).
- [ ] El perfil resultante es coherente con los overrides (EIP, consolidación).
- [ ] Si no hay tarifas, los honorarios salen `[PENDIENTE-CLIENTE]`, no un número.
- [ ] Los factores encarecedores llevan su palanca de abaratamiento.
- [ ] El informe de decisión cabe en una página.
- [ ] El perfil ha quedado registrado en `encargo.json`.
