---
name: hechos-posteriores-y-empresa-en-funcionamiento
description: 'Ejecuta los procedimientos sobre hechos posteriores al cierre y evalúa la capacidad de la entidad para continuar como empresa en funcionamiento, con árboles de decisión que conectan directamente con el efecto en el informe. Úsala en la fase de cierre, antes de redactar el informe, y siempre que aparezcan indicadores de dificultades financieras: patrimonio neto negativo, pérdidas recurrentes, fondo de maniobra negativo o incumplimiento de covenants.'
---

# Hechos posteriores y empresa en funcionamiento (NIA-ES 560 y 570 Revisada)

## Parte 1 — Hechos posteriores

**Dos tipos, con tratamiento contable opuesto** (NRV 23ª):

| Tipo | Definición | Tratamiento |
|---|---|---|
| Que **ponen de manifiesto condiciones que ya existían** al cierre | Insolvencia de un cliente cuyo deterioro ya se estaba gestando; sentencia sobre un litigio en curso | **Ajuste** de las cuentas anuales |
| Que **muestran condiciones surgidas después** del cierre | Incendio; ampliación de capital; adquisición de un negocio | **Desglose** en memoria si es significativo |

Confundirlos es el error habitual, y va en las dos direcciones.

**Procedimientos:**

1. Lectura de actas del órgano de administración y de la junta **posteriores al
   cierre**, hasta la fecha del informe.
2. Revisión de los estados financieros intermedios posteriores disponibles.
3. Indagación a la dirección sobre hechos relevantes ocurridos.
4. Revisión de movimientos bancarios y de facturación posteriores significativos.
5. Consulta de novedades registrales y de prensa.
6. **Manifestación específica** en la carta de manifestaciones.

**El periodo cubierto llega hasta la fecha del informe**, no hasta el cierre. Si
entre la formulación y la firma transcurre tiempo, hay que actualizar los
procedimientos.

## Parte 2 — Empresa en funcionamiento

### Indicadores a evaluar

| Financieros | Operativos | Otros |
|---|---|---|
| Patrimonio neto negativo o por debajo de la mitad del capital | Pérdida de un cliente o proveedor clave | Litigios de desenlace potencialmente ruinoso |
| Fondo de maniobra negativo | Salida de personal clave sin reemplazo | Incumplimientos normativos con sanción grave |
| Pérdidas recurrentes de explotación | Escasez de suministros | Cambio regulatorio adverso |
| Flujos de efectivo de explotación negativos | Obsolescencia del producto o del mercado | |
| **Incumplimiento de covenants** | | |
| Deuda a corto plazo que vence sin refinanciación acordada | | |
| Impago de dividendos o de deuda | | |

### Árbol de decisión → efecto en el informe

```
¿Hay hechos o condiciones que generen dudas significativas?
│
├── NO ──► Opinión favorable. Sin sección adicional.
│
└── SÍ ──► ¿La dirección ha hecho su valoración? (mínimo 12 meses desde el cierre)
     │
     ├── NO, y se niega a hacerla ──► OPINIÓN DENEGADA
     │
     └── SÍ ──► ¿Los planes son realizables y están soportados con evidencia?
          │
          ├── NO ──► ¿El uso del principio de empresa en funcionamiento es adecuado?
          │           └── NO ──► OPINIÓN DESFAVORABLE
          │
          └── SÍ, pero subsiste una INCERTIDUMBRE MATERIAL
               │
               └── ¿La memoria la desglosa adecuadamente?
                    ├── SÍ ──► Sección «Incertidumbre material relacionada con la
                    │          empresa en funcionamiento». OPINIÓN NO MODIFICADA.
                    └── NO ──► OPINIÓN CON SALVEDADES o DESFAVORABLE,
                               según la generalización del efecto.
```

### Lo que hay que exigir a la dirección

- Valoración formal que cubra **como mínimo doce meses desde la fecha de cierre**.
- **Previsiones de tesorería** con sus hipótesis explicitadas.
- Evidencia de los planes: cartas de apoyo de los socios, acuerdos de
  refinanciación firmados, contratos comprometidos.

**Una carta de apoyo del socio no es evidencia suficiente por sí sola**: hay que
evaluar la capacidad real del socio para prestar ese apoyo. Y un acuerdo de
refinanciación «en negociación» no es un acuerdo.

### Contraste retrospectivo

Compara las previsiones que la dirección presentó **el ejercicio anterior** con lo
realmente ocurrido. Es el mejor indicador disponible sobre la fiabilidad de sus
estimaciones, y casi nadie lo hace.

## Checklist de autoverificación

- [ ] Los procedimientos sobre hechos posteriores cubren hasta la **fecha del
      informe**, no hasta el cierre.
- [ ] Los hechos identificados están clasificados en los dos tipos y tratados en
      consecuencia.
- [ ] Se han leído las actas posteriores al cierre.
- [ ] Los indicadores de empresa en funcionamiento están evaluados, aunque la
      conclusión sea que no concurren.
- [ ] Si hay dudas, consta la valoración formal de la dirección con horizonte de
      al menos doce meses.
- [ ] Las previsiones están soportadas con evidencia, no solo con manifestaciones.
- [ ] Se ha hecho el contraste retrospectivo de las previsiones anteriores.
- [ ] El efecto en el informe se ha determinado con el árbol de decisión y
      trasladado a `redaccion-informe`.
