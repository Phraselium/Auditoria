---
name: cierre-del-encargo
description: Cierre — incorrecciones, hechos posteriores, empresa en funcionamiento, manifestaciones y archivo.
when_to_use: 'Úsala en la fase de cierre, antes de redactar el informe: sumario de ajustes corregidos y no corregidos con su evaluación cualitativa, procedimientos sobre hechos posteriores, evaluación de la empresa en funcionamiento, carta de manifestaciones de la dirección, comunicación de deficiencias de control interno y ensamblado del archivo final. También cada vez que un área proponga un ajuste, y siempre que aparezcan indicadores de dificultades financieras. Términos: cierre, ajustes, reclasificaciones, incorrecciones, sumario, cualitativa, hechos posteriores, empresa en funcionamiento, manifestaciones, deficiencias, control interno, gobierno, archivo, conservación.'
argument-hint: '[carpeta-del-encargo]'
---

# Cierre del encargo

Cuatro procedimientos, en este orden:

```bash
cat ${CLAUDE_PLUGIN_ROOT}/shared/procedimientos/<nombre>.md
```

| Orden | Procedimiento | Qué produce |
|---|---|---|
| 1 | `hechos-posteriores-y-empresa-en-funcionamiento` | Papeles N-1 y N-2, y el tipo de opinión que resulta del árbol de decisión |
| 2 | `evaluacion-de-incorrecciones` | Papel 8.1: sumario y conclusión frente a la materialidad |
| 3 | `comunicaciones-y-manifestaciones` | Papeles 8.2 a 8.4: manifestaciones **adaptadas**, deficiencias y comunicación con el gobierno |
| 4 | `archivo-y-cierre` | Papel 9.9: índice, referencias cruzadas y plazos de conservación — **solo tras la firma** |

> **Al invocarla, empieza por aquí.** Di en tres líneas: en qué paso estás, qué
> necesitas y el comando exacto con las rutas reales. Si falta algo, pídelo y
> **no lo inventes**.

## Antes de nada: recalcula la materialidad

Con las cifras definitivas. Si la materialidad de ejecución **baja**, el trabajo
ejecutado se ha quedado corto y hay que evaluar qué ampliar.

## Lo que más se hace mal en el cierre

**Las incorrecciones proyectadas del muestreo se olvidan.** Se acumulan las tres
clases: factuales, de juicio y **proyectadas**. Omitir estas últimas hace que el
sumario infravalore el efecto real.

**La evaluación cualitativa no es opcional.** Una incorrección puede ser
cuantitativamente inmaterial y cualitativamente significativa: si afecta a
covenants, a la clasificación de partidas, a las retribuciones de la dirección, o
si convierte una pérdida en beneficio. Y sobre todo: **varias incorrecciones
pequeñas en la misma dirección no son ruido, son un patrón** — probablemente el
hallazgo más importante del cierre.

**La carta de manifestaciones genérica no sirve.** Debe llevar una manifestación
específica por cada juicio y estimación relevante del encargo: condiciones de las
subvenciones, cumplimiento de covenants, clasificación de arrendamientos,
recuperabilidad de los impuestos diferidos. Fecha **no posterior** a la del
informe. Si la dirección se niega a firmarla, normalmente procede **opinión
denegada** (NIA-ES 580.20).

**Los hechos posteriores son de dos tipos opuestos** (NRV 23ª): los que ponen de
manifiesto condiciones que **ya existían** al cierre exigen **ajuste**; los que
muestran condiciones **surgidas después**, solo **desglose**. Confundirlos es el
error habitual, y va en las dos direcciones. El periodo cubierto llega hasta la
**fecha del informe**, no hasta el cierre.

**Las recomendaciones de control interno deben ser aplicables.** En una PYME de
cinco personas, recomendar segregación de funciones completa es un brindis al
sol. Lo útil son controles compensatorios que el administrador pueda ejercer.

## Empresa en funcionamiento: el árbol

```
¿Hay hechos o condiciones que generen dudas significativas?
├── NO ──► Opinión favorable, sin sección adicional.
└── SÍ ──► ¿La dirección ha hecho su valoración a 12 meses?
     ├── NO, y se niega ──► OPINIÓN DENEGADA
     └── SÍ ──► ¿Los planes son realizables y están soportados?
          ├── NO ──► ¿Es adecuado el principio de empresa en funcionamiento?
          │           └── NO ──► OPINIÓN DESFAVORABLE
          └── SÍ, pero subsiste INCERTIDUMBRE MATERIAL
               └── ¿La memoria la desglosa adecuadamente?
                    ├── SÍ ──► Sección específica. OPINIÓN NO MODIFICADA.
                    └── NO ──► CON SALVEDADES o DESFAVORABLE
```

Una carta de apoyo del socio **no es evidencia suficiente por sí sola**: hay que
evaluar su capacidad real de prestarlo. Y un acuerdo de refinanciación «en
negociación» no es un acuerdo. Contrasta además las previsiones del ejercicio
anterior con lo realmente ocurrido: es el mejor indicador de la fiabilidad de la
dirección al estimar, y casi nadie lo hace.

## El archivo

Se ensambla **oportunamente tras la fecha del informe** (referencia habitual: 60
días). Pasado ese momento no se puede eliminar documentación, y toda modificación
debe dejar constancia de quién, cuándo, por qué y con qué efecto. Conservación:
**5 años** desde la fecha del informe (art. 30 LAC); 10 años la documentación de
prevención del blanqueo.

Antes de cerrar, `dula validar <encargo> --listar`: no debe quedar ninguna
ejecución asistida sin validar.

## Checklist de autoverificación

- [ ] La materialidad se ha recalculado con las cifras definitivas.
- [ ] Todas las áreas han registrado sus ajustes propuestos.
- [ ] Las incorrecciones **proyectadas** del muestreo están incluidas.
- [ ] Cada no corregida tiene evaluación cualitativa redactada.
- [ ] Se ha evaluado si el conjunto revela un sesgo de la dirección.
- [ ] Los hechos posteriores cubren hasta la fecha del informe y están bien clasificados.
- [ ] La carta de manifestaciones lleva una manifestación por cada juicio relevante.
- [ ] Su fecha no es posterior a la del informe y está firmada.
- [ ] Las deficiencias significativas se han comunicado **por escrito**.
- [ ] El archivo se ensambla solo tras la firma, y sin ejecuciones de IA sin validar.
