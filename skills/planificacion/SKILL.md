---
name: planificacion
description: Planificación completa — entendimiento, materialidad, riesgos, diseño de pruebas y PBC.
when_to_use: 'Úsala para planificar un encargo ya aceptado: entender la entidad y su marco contable aplicable, determinar la materialidad global y de ejecución, levantar el mapa de riesgos por área y afirmación, decidir qué prueba responde a cada riesgo, y generar la lista de documentación a pedir al cliente. También al recalcular la materialidad al cierre o al reevaluar un riesgo por un hallazgo. Términos: planificar, entendimiento, entidad, sector, marco, PGC, PYMES, materialidad, magnitud, riesgo, afirmación, fraude, espectro, significativo, control interno, prueba, muestreo, analítico, alcance, PBC, documentación, solicitar.'
argument-hint: '[carpeta-del-encargo]'
---

# Planificación del encargo

Cinco procedimientos encadenados. Cada uno se abre **solo cuando toca**:

```bash
cat ${CLAUDE_PLUGIN_ROOT}/procedimientos/<nombre>.md
```

| Orden | Procedimiento | Qué produce |
|---|---|---|
| 1 | `entendimiento-entidad` | Papel 1.1: negocio, sector, **marco contable verificado** contra los límites legales, ciclos, TI y partes vinculadas |
| 2 | `materialidad` | Papel 1.4: magnitud justificada, MG, MP, específicas y umbral de insignificancia |
| 3 | `mapa-de-riesgos` | Papel 1.5: riesgos por área y afirmación, con su espectro y factores concurrentes |
| 4 | `diseno-de-pruebas` | Papel 1.5: el procedimiento más barato que sigue siendo suficiente, con su fundamento |
| 5 | `plan-y-solicitud-informacion` | PBC personalizada y priorizada por ruta crítica |

> **Al invocarla, empieza por aquí.** Di en tres líneas: en qué paso estás, qué
> necesitas para darlo y el comando exacto con las rutas reales. Si falta algo,
> pídelo y **no lo inventes**.

## El orden importa

**Antes que nada, `ingesta-y-cuadres`.** Sin la contabilidad cuadrada no se puede
determinar la materialidad ni contar las poblaciones. Si el papel `2.1` no está
concluido, detente.

**El entendimiento no es relleno.** Es lo que permite que el mapa de riesgos
identifique riesgos *reales* en vez de una lista genérica de manual. Verifica el
marco contable contra los límites del art. 257 LSC y del RD 1515/2007 — no lo
presumas del ejercicio anterior. Señal de alerta: cuentas de los grupos 8 y 9 en
el balance, que no existen en el PGC PYMES.

**La materialidad se gradúa por perfil** (`LIGERO` 75 %, `ESTÁNDAR` 65 %,
`COMPLEJO` 55 % de la global):

```bash
audita materialidad '{"cifra_negocios": 1850000, "total_activo": 920000}' \
    --perfil ESTANDAR --encargo . \
    --especifica "M:0.25:retribuciones al órgano de administración"
```

El error más común en PYME es aferrarse al resultado antes de impuestos cuando la
entidad está cerca de cero: produce una materialidad ridícula que dispara el
alcance sin ganar calidad. El script lo detecta y cambia de magnitud
**explicando por qué**.

**Al recalcular al cierre**, lo relevante no es que cambie: es que **baje**. Si la
MP final es inferior a la usada para dimensionar las muestras, el trabajo se ha
quedado corto y hay que ampliarlo. La alerta es automática.

## Riesgos que se presumen siempre

No se identifican, **ya están**. Lo que se documenta es cómo se responden:

1. **Fraude en el reconocimiento de ingresos** (NIA-ES 240.25). Presunción
   rebatible: si se rebate, hay que documentar el razonamiento. El silencio no vale.
2. **Elusión de controles por la dirección** (NIA-ES 240.31). **No rebatible**, en
   toda entidad. Respuesta obligatoria: test de asientos del diario.

El catálogo por área está en `referencias/catalogo-riesgos.md`.

## La regla de los huérfanos

- **Todo riesgo tiene al menos un procedimiento que lo responde.**
- **Todo procedimiento responde a un riesgo identificado.**

`revision-de-calidad` falla en bloqueante si hay huérfanos en cualquiera de los
dos sentidos. Un procedimiento sin riesgo suele ser trabajo heredado de campañas
anteriores: ahí hay ahorro real.

## Checklist de autoverificación

- [ ] El papel `2.1` estaba concluido antes de empezar.
- [ ] El marco contable está **verificado** contra los límites legales, no presumido.
- [ ] La magnitud de la materialidad está justificada por escrito.
- [ ] Hay materialidad específica para las áreas de desglose legalmente exigido.
- [ ] Cada riesgo tiene afirmación asignada y factores de riesgo inherente enumerados.
- [ ] La presunción de fraude en ingresos está respondida o rebatida por escrito.
- [ ] El test de asientos del diario está programado.
- [ ] Cero riesgos sin respuesta y cero pruebas sin riesgo.
- [ ] Donde se ha elegido la opción barata, consta qué la haría dejar de ser defendible.
- [ ] La PBC solo pide lo que se va a usar, y la ruta crítica sale primero.
