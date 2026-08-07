---
name: muestreo
description: Ejecuta la selección de muestras conforme al método elegido en el diseño de pruebas (MUS por unidades monetarias, atributos para pruebas de controles, o dirigido no estadístico), documentando población, unidad de muestreo, estratificación, semilla de aleatoriedad para reproducibilidad, tamaño y su fundamento; evalúa los errores encontrados, los proyecta a la población y concluye frente a la materialidad de ejecución. Úsala cuando haya que seleccionar partidas para probar o evaluar los errores de una muestra ya examinada.
---

# Muestreo de auditoría (NIA-ES 530)

## La semilla no es un detalle

**Sin semilla registrada, la muestra no es reejecutable por un revisor, y eso la
hace indefendible ante inspección.** El script la registra siempre, y siempre
aparece en el papel de trabajo. Si el revisor ejecuta el mismo comando con la
misma semilla, obtiene exactamente las mismas partidas.

## Métodos

```bash
export PYTHONPATH=${CLAUDE_PLUGIN_ROOT}/shared/scripts

# MUS - poblacion numerosa, riesgo de sobrevaloracion, se necesita extrapolar
python3 -m dula.cli muestreo poblacion.xlsx importe --metodo mus \
    --materialidad <MP> --riesgo 0.05 --errores 0 --semilla 12345 --excel salida.xlsx

# Atributos - pruebas de controles
python3 -m dula.cli muestreo poblacion.xlsx importe --metodo atributos --frecuencia mensual

# Dirigido - perfil LIGERO, poblacion concentrada
python3 -m dula.cli muestreo poblacion.xlsx importe --metodo dirigido --materialidad <MP>
```

### MUS (unidades monetarias)

`n = (población × factor de fiabilidad) / materialidad de ejecución`

| Riesgo de aceptación incorrecta | Factor (0 errores esperados) |
|---|---|
| 5 % | 3,00 |
| 10 % | 2,31 |
| 15 % | 1,90 |
| 20 % | 1,61 |
| 25 % | 1,39 |

Las partidas de importe **igual o superior al intervalo de muestreo** se examinan
individualmente al 100 %: no pueden no salir. Sobre el resto, selección
sistemática con arranque aleatorio.

### Atributos (controles)

| Frecuencia del control | Tamaño |
|---|---|
| Varias veces al día | 40 |
| Diaria | 25 |
| Semanal | 15 |
| Mensual | 5 |
| Trimestral | 2 |
| Anual | 1 |

**Una sola desviación** en la muestra de atributos significa que no se puede
confiar en el control: hay que reconsiderar el enfoque hacia pruebas sustantivas.
No se amplía la muestra buscando que salga bien.

### Dirigido no estadístico

Todas las partidas por encima de la MP más las que cumplan criterios
cualitativos. **No permite extrapolar**: la conclusión se limita a lo examinado
más el analítico sobre el resto de la población. Decirlo así en el papel de
trabajo es lo que lo hace defendible.

## Evaluación y proyección de errores

```python
from dula import muestreo
muestreo.evalua(m, errores=[
    {"referencia": "F-2025-0412", "descripcion": "Ingreso del ejercicio siguiente",
     "importe_registrado": 12_400.00, "importe_auditado": 0.00},
], materialidad_ejecucion=15_031.25)
```

En MUS, la proyección se hace por **tainting**: la tasa de error de la partida ×
el intervalo de muestreo. Las partidas de examen individual **no se proyectan**:
su error es conocido, no estimado.

Si el error total estimado supera la MP, hay tres salidas y hay que elegir una:
(a) ampliar la muestra, (b) aplicar procedimientos alternativos, o (c) proponer el
ajuste y **solicitar a la dirección que investigue la causa y corrija la población
completa**. Ignorarlo no es una opción.

## Checklist de autoverificación

- [ ] La población está definida y cuadra con el saldo contable del área.
- [ ] El método es el elegido en `diseno-de-pruebas`, con su fundamento.
- [ ] La **semilla está registrada** en el papel de trabajo.
- [ ] El tamaño de muestra se ha calculado con la MP **vigente**, no con una
      anterior.
- [ ] Las partidas de examen individual están identificadas.
- [ ] Los errores se han proyectado correctamente (los individuales no se
      proyectan).
- [ ] La conclusión se contrasta contra la materialidad de ejecución.
- [ ] Si el método es dirigido, consta que **no se extrapola**.
