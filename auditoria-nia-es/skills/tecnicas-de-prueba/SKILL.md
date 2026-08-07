---
name: tecnicas-de-prueba
description: Muestreo, procedimientos analíticos y test de asientos del diario.
when_to_use: 'Úsala cuando haya que seleccionar partidas para probar, dimensionar una muestra o proyectar los errores encontrados a la población; cuando toque un procedimiento analítico —variaciones interanuales, ratios, márgenes, análisis mensual de ingresos o una expectativa construida con datos independientes—; y para el test de asientos inusuales del diario, que es obligatorio en todo encargo. Términos: muestra, muestreo, MUS, unidades monetarias, atributos, dirigido, semilla, población, estratificación, proyección, tainting, analítico, variación, ratio, margen, expectativa, umbral, asientos, diario, elusión, fraude.'
argument-hint: '[población.xlsx] o [diario.xlsx]'
---

# Técnicas de prueba

Tres técnicas transversales que usan todas las áreas.

```bash
cat ${CLAUDE_PLUGIN_ROOT}/shared/procedimientos/<nombre>.md
```

| Procedimiento | Para qué |
|---|---|
| `muestreo` | Seleccionar partidas y proyectar los errores a la población |
| `analiticos` | Variaciones, ratios y expectativas con umbral fijado a priori |
| `test-asientos-diario` | Asientos inusuales — **obligatorio en todo encargo** |

> **Al invocarla, empieza por aquí.** Di en tres líneas: qué técnica vas a usar,
> qué necesitas y el comando exacto con las rutas reales. Si falta algo, pídelo y
> **no lo inventes**.

## Muestreo — la semilla no es un detalle

```bash
audita muestreo poblacion.xlsx importe --metodo mus --materialidad <MP> --semilla 12345
audita muestreo poblacion.xlsx importe --metodo atributos --frecuencia mensual
audita muestreo poblacion.xlsx importe --metodo dirigido --materialidad <MP>
```

**Sin semilla registrada, la muestra no es reejecutable por un revisor, y eso la
hace indefendible ante inspección.** El script la publica siempre.

`n = (población × factor de fiabilidad) / materialidad de ejecución`. Riesgo del
5 % → factor 3,00. Las partidas de importe ≥ intervalo se examinan al 100 %: no
pueden no salir.

**Una sola desviación** en una muestra de atributos significa que no se puede
confiar en el control. No se amplía la muestra buscando que salga bien.

El **dirigido no permite extrapolar**: la conclusión se limita a lo examinado más
el analítico sobre el resto. Decirlo así en el papel es lo que lo hace defendible.

En la **proyección**, las partidas de examen individual **no se proyectan**: su
error es conocido. Si el error total estimado supera la MP hay tres salidas y hay
que elegir una: ampliar la muestra, aplicar procedimientos alternativos, o
proponer el ajuste y pedir a la dirección que investigue la causa y corrija la
población completa. Ignorarlo no es una opción.

## Analíticos — el umbral se fija ANTES

```bash
audita analiticos cifras_actual.json cifras_anterior.json --materialidad <MP>
```

**Si el umbral se fija después de ver las cifras, el procedimiento no es un
analítico sustantivo: es una racionalización de lo que ha salido**, y no vale como
evidencia ante un revisor.

Umbral **doble**: se investiga lo que supera **a la vez** el 50 % de la MP y el
10 % de variación relativa. Solo el absoluto dispara por cambios porcentuales
enormes en partidas irrelevantes; solo el relativo deja pasar variaciones grandes
en partidas estables.

Un analítico vale como **evidencia sustantiva** solo si la relación es predecible,
la expectativa se construye con **datos independientes del registro auditado**, y
el riesgo no es significativo (los significativos exigen pruebas de detalle,
NIA-ES 330.21).

Y una explicación de la dirección **no corroborada no es evidencia** (NIA-ES
520.7). «Según nos informa la dirección» y cerrar el papel es exactamente lo que
señala un inspector.

El de mayor rendimiento por hora: el **análisis mensual de ingresos**. La
concentración en diciembre es la señal más barata y más productiva.

## Test de asientos — obligatorio, sin excepción

```bash
audita asientos diario.xlsx 2025-12-31 --materialidad <MP> --perfil ESTANDAR
```

El riesgo de elusión de controles por la dirección se presume presente en toda
entidad y **no es rebatible** (NIA-ES 240.31).

Nueve filtros puntuados: ingreso sin contrapartida en clientes ni tesorería (5),
contrapartida no habitual (4), últimos 5 días del ejercicio (3), sin descripción
(3), cuentas de uso excepcional (3), usuario de baja frecuencia (3), fin de semana
(2), festivo (2), importe redondo (2). En perfil `LIGERO` se aplican los cuatro de
mayor rendimiento; **la prueba no se elimina nunca**.

Un asiento seleccionado **no es un asiento irregular**: el filtro dirige la
inspección, no presume nada. Para cada uno de los reportados: obtén el soporte,
verifica su razonabilidad y **documenta la conclusión**, aunque sea «correcto,
corresponde a X». Un papel que lista los seleccionados y no dice qué se hizo con
cada uno **no responde al riesgo**.

Requiere diario con **fecha y usuario**. Sin usuario, tres de los nueve filtros no
se aplican y así hay que hacerlo constar.

## Checklist de autoverificación

- [ ] La población está definida y cuadra con el saldo contable del área.
- [ ] El método es el elegido en el diseño de pruebas, con su fundamento.
- [ ] La **semilla está registrada** en el papel de trabajo.
- [ ] El tamaño se ha calculado con la MP **vigente**, no con una anterior.
- [ ] Si el método es dirigido, consta que **no se extrapola**.
- [ ] El umbral analítico se fijó **antes** de ver las cifras, y consta así.
- [ ] Las explicaciones de la dirección están corroboradas con evidencia.
- [ ] El test de asientos se ha ejecutado, con independencia del perfil.
- [ ] Cada asiento reportado tiene soporte obtenido y conclusión documentada.
