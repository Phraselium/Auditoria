---
name: analiticos
description: Ejecuta procedimientos analíticos preliminares, sustantivos y de revisión final: variaciones interanuales, ratios, márgenes, análisis mensual de ingresos y gastos, y expectativas construidas con datos independientes, con umbral de investigación definido a priori. Investiga y documenta solo las desviaciones que superan el umbral. Úsala en planificación, como prueba sustantiva en las áreas donde la relación es predecible, y en la revisión final antes de la firma.
---

# Procedimientos analíticos (NIA-ES 520)

## La regla que hace que valgan como evidencia

**El umbral de investigación se fija ANTES de mirar las cifras.** Si se fija
después, el procedimiento no es un analítico sustantivo: es una racionalización
de lo que ha salido, y no vale como evidencia ante un revisor.

```bash
export PYTHONPATH=<plugin>/shared/scripts
python3 -m dula.cli analiticos 00-fuentes/cifras_actual.json 00-fuentes/cifras_anterior.json \
    --materialidad <MP> --factor 0.5 --papel "01-papeles/1.6 Analiticos.xlsx"
```

**Umbral doble.** Se investiga lo que supera **a la vez** el 50 % de la
materialidad de ejecución **y** el 10 % de variación relativa. Solo el absoluto
dispara por cambios porcentuales enormes en partidas irrelevantes; solo el
relativo deja pasar variaciones grandes en partidas estables. La conjunción es lo
que funciona.

## Los tres momentos

**1. Preliminares (planificación).** Sirven para **identificar riesgos**, no para
concluir. Variaciones interanuales por epígrafe y batería de ratios. Lo que salga
alimenta el `mapa-de-riesgos`.

**2. Sustantivos (trabajo de campo).** Aquí sí son evidencia, y solo si:

- La relación es **predecible** (gastos de personal, amortizaciones, suministros,
  arrendamientos, comisiones sobre ventas).
- La expectativa se construye con **datos independientes del registro auditado**.
- El umbral de precisión se fijó a priori.
- El riesgo no es significativo (los significativos exigen pruebas de detalle,
  NIA-ES 330.21).

```python
from dula import analiticos
analiticos.expectativa(
    "Gastos de personal", valor_registrado=462_000,
    valor_esperado=14 * 33_000,
    base_calculo="Nº medio de empleados según TC2 (14) x coste medio del convenio (33.000 EUR)",
    materialidad_ejecucion=15_031)
```

**3. Revisión final (antes de la firma).** Última mirada al conjunto de las
cuentas anuales para comprobar que son coherentes con el conocimiento adquirido
durante toda la auditoría. Es donde aparecen las incoherencias que ninguna prueba
de área detecta porque cada una miraba su trozo.

## Análisis mensual de ingresos

El analítico de mayor rendimiento por hora invertida de todo el plugin.

```python
analiticos.evolucion_mensual(diario, prefijo_cuenta="70")
```

Detecta concentración anómala —típicamente en diciembre—, meses sin actividad y
desviaciones sobre la media. La concentración en diciembre se reporta con
severidad `RESOLVER` y referencia a la NIA-ES 240.25: es la señal más directa de
corte de operaciones incorrecto o de reconocimiento anticipado.

## Lo que no vale como conclusión

Una explicación de la dirección **no corroborada** no es evidencia (NIA-ES 520.7).
Si el cliente explica que la variación se debe a un nuevo contrato, hay que ver el
contrato. Documentar «según nos informa la dirección» y cerrar el papel es
exactamente lo que un inspector señala.

## Checklist de autoverificación

- [ ] El umbral de investigación se fijó **antes** de ver las cifras y consta así.
- [ ] Cada desviación que supera el umbral está investigada y documentada.
- [ ] Las explicaciones de la dirección están **corroboradas con evidencia**.
- [ ] En los analíticos sustantivos, la expectativa se construyó con datos
      independientes del registro auditado.
- [ ] No se ha usado un analítico como única respuesta a un riesgo significativo.
- [ ] Los analíticos de revisión final se han ejecutado sobre las cuentas
      definitivas.
