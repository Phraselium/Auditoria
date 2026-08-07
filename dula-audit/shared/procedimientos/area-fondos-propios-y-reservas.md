# area-fondos-propios-y-reservas

> Área G — Patrimonio neto y reservas indisponibles: legal, capitalización, nivelación.

> **Cuándo:** Se comprueba en planificación por sus implicaciones y se cierra en trabajo de campo. Términos: audita, movimientos, patrimonio, coherencia, propuesta, aplicación, verifica, específicamente, reservas, indisponibles, restringidas, reserva, capitalización, nivelación.

> **Necesita:** `[sumas-y-saldos.xlsx]`

---
**Cuentas del área:** 10x capital · 11x reservas · 12x resultados · 13x subvenciones y ajustes · 557 dividendo a cuenta

La mecánica (carga del programa escalado, ejecución, generación del papel de
trabajo, conclusión y registro) la aporta la guía `areas-de-campo`. Aquí está el **criterio
específico del área** y su programa de trabajo.

## Riesgos típicos

| Riesgo | Afirmaciones |
|---|---|
| Reservas indisponibles mal dotadas, insuficientes o dispuestas indebidamente | presentación, desglose |
| Distribución de dividendos que incumple los límites legales | cumplimiento |
| Movimientos de patrimonio neto incoherentes con las actas | exactitud |
| Patrimonio neto por debajo de los límites de disolución o reducción obligatoria | empresa en funcionamiento |

## Criterio específico del área

**Se verifica dos veces: en planificación y en cierre.** En planificación porque
sus implicaciones condicionan el resto del trabajo (causa de disolución, límites a
la distribución, efecto fiscal). En cierre porque la propuesta de aplicación del
resultado es del ejercicio auditado.

### Reservas indisponibles y restringidas

`plan_contable.reserva_restringida(cuenta)` identifica la reserva y su régimen:

| Cuenta | Reserva | Régimen |
|---|---|---|
| 112 | Reserva legal | 10 % del beneficio hasta el 20 % del capital (art. 274 LSC) |
| 1142 | Reserva por fondo de comercio | Indisponible mientras haya fondo de comercio en el activo (art. 273.4 LSC) |
| 1144 | **Reserva de capitalización** | Indisponible durante el plazo legal de mantenimiento del incremento de fondos propios (art. 25 LIS) |
| 1145 | **Reserva de nivelación** | Indisponible hasta su aplicación o el transcurso de 5 años (art. 105 LIS) |
| 1141 | Reserva por capital amortizado | Indisponible (art. 335 c) LSC) |
| 115 | Reservas especiales | Según la normativa específica aplicable |

**Lo que hay que comprobar en cada una, no solo su existencia:**

1. **Dotación correcta** en el ejercicio en que nació la obligación.
2. **Mantenimiento**: que no se haya dispuesto durante el plazo legal.
3. **Plazo**: cuándo deja de ser indisponible. La reserva de capitalización y la
   de nivelación tienen plazos que hay que seguir año a año.
4. **Desglose en memoria**: la nota de fondos propios debe identificarlas y
   explicar su restricción. Es un desglose que se omite con frecuencia.

**Efecto fiscal.** Disponer de la reserva de capitalización antes de plazo obliga
a regularizar el incentivo fiscal aplicado. Conéctalo con `area-fiscal`.

### Causa de disolución

Patrimonio neto inferior a la mitad del capital social (art. 363.1.e LSC) es
causa de disolución. Conéctalo con `hechos-posteriores-y-empresa-en-funcionamiento`.

## Programa de trabajo

El programa escalado por perfil está en
`shared/references/programas/fondos-propios-y-reservas.md`. Se carga bajo demanda: no lo copies aquí.

## Ejecución

```bash
dula reservas 00-fuentes/sumas_y_saldos.xlsx \
    --cliente "<CLIENTE>" --ejercicio <AAAA> --encargo . \
    --papel "01-papeles/G-2 Reservas indisponibles.xlsx"
```

Identifica cada reserva restringida con su régimen y su norma, verifica de forma
determinista la dotación mínima de la reserva legal (10 % del beneficio hasta el
20 % del capital, art. 274 LSC) y deja constancia de que **cada una debe figurar
identificada en la nota de fondos propios de la memoria** — es un desglose que se
omite con frecuencia.

## Checklist de autoverificación

Además de la checklist común de `areas-de-campo`:

- [ ] El movimiento del patrimonio neto cuadra con el ECPN y con el balance.
- [ ] La propuesta de aplicación del resultado coincide con el acta.
- [ ] Todas las reservas indisponibles están identificadas con su régimen y su plazo.
- [ ] Se ha verificado que ninguna reserva indisponible se ha dispuesto dentro del plazo.
- [ ] El desglose de reservas restringidas figura en la memoria.
- [ ] Se ha comprobado la causa de disolución del art. 363.1.e) LSC.
