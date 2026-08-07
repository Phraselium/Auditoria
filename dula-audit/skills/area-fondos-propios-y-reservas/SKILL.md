---
name: area-fondos-propios-y-reservas
description: Audita los movimientos del patrimonio neto y su coherencia con las actas y la propuesta de aplicación del resultado, y verifica específicamente las reservas indisponibles y restringidas: reserva legal, reserva de capitalización, reserva de nivelación, reserva por fondo de comercio y otras reservas afectas, con su dotación, mantenimiento, plazos y desglose. Se comprueba en planificación por sus implicaciones y se cierra en trabajo de campo.
---

# Área G — Fondos propios y reservas

**Cuentas del área:** 10x capital · 11x reservas · 12x resultados · 13x subvenciones y ajustes · 557 dividendo a cuenta

La mecánica (carga del programa escalado, ejecución, generación del papel de
trabajo, conclusión y registro) la aporta `area-runner`. Aquí está el **criterio
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
export PYTHONPATH=<plugin>/shared/scripts
python3 -c "
import sys; sys.path.insert(0,'<plugin>/shared/scripts')
from dula import ingesta, plan_contable
sys_df,_ = ingesta.normaliza_sumas_y_saldos('00-fuentes/sumas_y_saldos.xlsx')
for _, r in sys_df[sys_df['cuenta'].str.startswith(('11','10','12','13'))].iterrows():
    info = plan_contable.reserva_restringida(r['cuenta'])
    if info: print(r['cuenta'], r['saldo'], info['nombre'], '| disponible:', info['disponible'], '|', info.get('regla',''))
"
```

## Checklist de autoverificación

Además de la checklist común de `area-runner`:

- [ ] El movimiento del patrimonio neto cuadra con el ECPN y con el balance.
- [ ] La propuesta de aplicación del resultado coincide con el acta.
- [ ] Todas las reservas indisponibles están identificadas con su régimen y su plazo.
- [ ] Se ha verificado que ninguna reserva indisponible se ha dispuesto dentro del plazo.
- [ ] El desglose de reservas restringidas figura en la memoria.
- [ ] Se ha comprobado la causa de disolución del art. 363.1.e) LSC.
