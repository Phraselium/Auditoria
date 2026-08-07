---
description: 'Flujo 3 — Fase completa: cuadres, materialidad, riesgos, pruebas y PBC.'
argument-hint: '[ruta-del-encargo]'
---

Planifica el encargo: $ARGUMENTS

Secuencia, en este orden y sin saltarse pasos:

1. **`ingesta-y-cuadres`** — puerta de entrada. Si algún cuadre bloqueante falla,
   detente aquí y repórtalo.
2. **`entendimiento-entidad`** — perfil de negocio, sector, marco aplicable
   (verifícalo contra los límites legales, no lo presumas), ciclos, sistemas de
   TI, partes vinculadas y hechos relevantes.
3. **`materialidad`** — magnitud, porcentaje, materialidad de ejecución,
   específicas y umbral de insignificancia, todo con su fundamento redactado.
4. **`mapa-de-riesgos`** — por área y afirmación, con espectro y factores. Incluye
   siempre la presunción de fraude en ingresos y la elusión de controles.
5. **`escalado-del-encargo`** — configura qué se activa y con qué profundidad.
6. **`diseno-de-pruebas`** — asigna a cada riesgo su procedimiento. **Cero
   huérfanos** en ninguno de los dos sentidos.
7. **`plan-y-solicitud-informacion`** — PBC personalizada y priorizada por ruta
   crítica. Las autorizaciones de circularización salen ya.
8. **`area-fondos-propios-y-reservas`** (comprobación preliminar) — las reservas
   indisponibles y la causa de disolución del art. 363.1.e) LSC tienen
   implicaciones que condicionan el resto del trabajo.

Al terminar, marca la fase `planificacion` como `completa` y ejecuta
`revision-de-calidad --pre-vuelo` para ver qué queda abierto.
