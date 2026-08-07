---
name: materialidad
description: Materialidad global, de ejecución y específicas, con la justificación del criterio elegido.
when_to_use: 'Úsala en planificación tras la ingesta y de nuevo al cierre con las cifras definitivas. Términos: determina, magnitud, referencia, porcentaje, justificación, criterio, elegido, materialidad, global, ejecución, materialidades, específicas, sensibles, umbral.'
argument-hint: '[cifras.json]'
---

# Materialidad (NIA-ES 320 y 450)

> **Al invocarla, empieza por aquí.** Presenta en pantalla, en tres
> líneas y antes de hacer nada:
>
> 1. **Qué necesito:** cifra de negocios, total activo y resultado antes de impuestos.
> 2. **Qué vas a recibir:** papel 1.4 y, si es un recálculo, la alerta de si el alcance ya ejecutado se ha quedado corto.
> 3. **El comando exacto** que voy a ejecutar, con las rutas reales.
>
> Si falta algo de lo anterior, pídelo y **no lo inventes**.

## Procedimiento

**1. Elegir la magnitud de referencia — y justificarla.** El script propone, pero
el criterio es del auditor:

| Magnitud | Cuándo es la adecuada | Rango |
|---|---|---|
| Resultado antes de impuestos | Entidad con ánimo de lucro, resultado **positivo, estable y significativo** (≥ 2 % de la cifra de negocios) | 5-10 % |
| Cifra de negocios | El resultado es negativo, volátil o próximo a cero — una materialidad basada en él saldría anormalmente baja | 0,5-2 % |
| Total activo | Entidad patrimonial o sin actividad ordinaria relevante | 0,5-2 % |
| Patrimonio neto | Entidad en la que el interés se centra en la solvencia | 1-5 % |

El error más común en PYME es aferrarse al resultado antes de impuestos cuando la
entidad está cerca de cero: produce una materialidad ridícula que dispara el
alcance sin ganar un gramo de calidad. El script lo detecta y cambia de magnitud
**explicando por qué**.

**2. Ejecutar.**

```bash
dula materialidad '{"cifra_negocios": 1850000, "total_activo": 920000, "resultado_antes_impuestos": 41000}' \
    --perfil ESTANDAR --encargo . \
    --especifica "M:0.25:retribuciones al órgano de administración y operaciones con partes vinculadas, cuyo desglose es legalmente exigido con independencia de su importe"
```

**3. Materialidad de ejecución.** Se gradúa por perfil: `LIGERO` 75 %,
`ESTÁNDAR` 65 %, `COMPLEJO` 55 % de la global. A mayor riesgo, menor MP, porque
mayor es la expectativa de incorrecciones no detectadas.

**4. Materialidades específicas.** Más bajas, para partidas en las que la
expectativa del usuario no depende del importe:

- Retribuciones al órgano de administración y operaciones con partes vinculadas
  (art. 260 LSC): el desglose es exigible siempre.
- Cualquier partida cuyo desglose sea legalmente obligatorio.
- Partidas que afecten al cumplimiento de covenants.

**5. Recálculo al cierre.** Obligatorio cuando las cifras definitivas difieren de
las usadas en planificación.

## La alerta que importa

Lo relevante no es que la materialidad cambie: es que **baje**. Si la MP final es
inferior a la usada para dimensionar las muestras, el trabajo ejecutado se ha
quedado corto y hay que ampliarlo. `materialidad.evalua_recalculo()` lo detecta y
lo dice con todas las letras. Una bajada superior al 5 % dispara la alerta.

## Outputs

- `01-papeles/1.4 Materialidad.xlsx`
- Registro **versionado** en `encargo.json`: cada revisión se conserva, no se
  sobrescribe. Un revisor puede ver qué materialidad estaba vigente cuando se
  dimensionó cada prueba.

## Checklist de autoverificación

- [ ] La magnitud elegida está **justificada por escrito**, no solo indicada.
- [ ] El porcentaje está dentro del rango y su posición dentro del rango está
      motivada por el perfil de riesgo.
- [ ] La materialidad de ejecución corresponde al perfil vigente.
- [ ] Se han fijado materialidades específicas para las áreas de desglose
      legalmente exigido.
- [ ] Está fijado el umbral de incorrecciones claramente insignificantes.
- [ ] Si es un recálculo, consta la evaluación de su efecto sobre el alcance ya
      ejecutado.
- [ ] El fundamento está redactado para que un revisor externo lo reconstruya sin
      preguntar nada.
