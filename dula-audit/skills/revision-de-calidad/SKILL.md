---
name: revision-de-calidad
description: Actúa como revisor independiente y escéptico del archivo completo. Verifica que todo riesgo tiene respuesta ejecutada y concluida, que toda conclusión está soportada, que los cuadres pasan, que la materialidad es la vigente, que las incorrecciones están evaluadas, que la documentación permitiría reconstruir el trabajo y que el informe es coherente con el archivo. Entrega panel del socio en una página + listado completo por severidad. Ejecútala en MODO PRE-VUELO durante toda la campaña, no solo antes de firmar. Úsala cuando el socio pregunte "¿cómo va esto?", "¿puedo firmar?" o "¿qué me falta?".
---

# Revisión de calidad del archivo

**La skill más importante dado el contexto del despacho.** Si el socio solo ve
las excepciones el último día, el problema no se ha resuelto: se ha concentrado.

## Modo pre-vuelo: el cambio que más importa

Esta skill **no es solo para el momento de la firma**. Ejecútala en modo
pre-vuelo con regularidad durante la campaña —al cerrar cada área, o semanalmente
en encargos largos— para que las excepciones vayan apareciendo cuando aún hay
tiempo de resolverlas.

```bash
dula calidad <carpeta-encargo> --pre-vuelo     # durante la campaña
dula calidad <carpeta-encargo> \
    --panel "02-documentos/Panel del socio.txt" \
    --papel "01-papeles/9.2 Revision de calidad.xlsx"          # antes de firmar
```

El modo pre-vuelo degrada las alarmas que **solo** son bloqueantes en el momento
de la firma (revisión de calidad del encargo pendiente, fases posteriores sin
cerrar, apartado del informe aún no redactado) para que el ruido no oculte lo que
sí es urgente ahora.

## Lo que verifica

| Código | Comprobación | Norma |
|---|---|---|
| `CAL-001` | Riesgo sin ningún procedimiento que lo responda | NIA-ES 330.6 |
| `CAL-002` | Riesgo cuyas respuestas no están concluidas | NIA-ES 330.28 |
| `CAL-010` | Papel sin conclusión redactada | NIA-ES 230.8 |
| `CAL-011` | Conclusión demasiado escueta para reconstruir el razonamiento | NIA-ES 230.8 |
| `CAL-012` | Papel no vinculado a ningún riesgo | — |
| `CAL-020/021/022` | Materialidad ausente, sin fundamento, o revisada sin evaluar su efecto en el alcance | NIA-ES 320 |
| `CAL-030` | Excepción bloqueante sin resolver en cualquier área | — |
| `CAL-040/041` | Incorrecciones no corregidas que superan la materialidad, o sin evaluación **cualitativa** | NIA-ES 450 |
| `CAL-050` | Fases cerradas fuera de orden | — |
| `CAL-060` | Opinión favorable incoherente con las incorrecciones acumuladas | NIA-ES 700R/705R |
| `CAL-061` | Incertidumbre de empresa en funcionamiento sin sección en el informe | NIA-ES 570R.22 |
| `CAL-062` | **Informe sin el apartado del impuesto sobre sociedades** | RICAC 22/01/2026 |
| `CAL-063` | Salvedad sin cuantificar y sin explicar por qué no se cuantifica | NIA-ES 705R.18-20 |
| `CAL-070/071` | Sin registro de ficheros fuente, o papeles concluidos sin fichero | NIA-ES 230 |
| `CAL-080` | Revisión de calidad del encargo exigible y no realizada | NIGC2-ES; NIA-ES 220R.36 |
| `CAL-081` | Aceptación e independencia sin completar | LAC arts. 14-20 |
| `CAL-090` | Hay papeles en el archivo y ninguna ejecución registrada en `uso-ia.log` | NIGC1-ES |
| `CAL-091` | **Ejecución asistida sin validar cuyo resultado está en un papel concluido** | NIGC1-ES; NIA-ES 220R |
| `CAL-092` | Ejecuciones sin validar y sin papel asociado (cálculos exploratorios) | — |

## Las dos capas de salida

**(a) Panel del socio — una página.** Solo las cuestiones que exigen su juicio,
ordenadas por severidad, cada una con la acción concreta. Encabezado con perfil,
papeles concluidos, riesgos, materialidad y **estado apto / no apto para firma**.
Todo lo demás ya está cuadrado y evidenciado, y así se le dice expresamente.

**(b) Listado completo** de excepciones clasificadas en `BLOQUEANTE` (impide
firmar) / `RESOLVER` (antes de firmar) / `DOCUMENTAR` (mejora de documentación) /
`INFORMATIVA`.

## Mentalidad con la que hay que ejecutarla

Escéptica y sin complacencia. Esta skill **busca activamente lo que falta**, no
confirma lo que hay. Cuando la ejecutes:

- Un papel con conclusión de una línea **no está concluido**, está rellenado.
- Un riesgo con respuesta asignada pero papel `en curso` **no está cubierto**.
- Una incorrección no corregida sin evaluación cualitativa **no está evaluada**,
  aunque su importe sea pequeño: puede afectar a covenants, a la clasificación
  de partidas, a retribuciones de la dirección, o revelar un sesgo.
- Que no haya excepciones **no significa que el trabajo esté bien**: significa
  que las comprobaciones automáticas pasan. El juicio sigue siendo del socio.

Complementa la ejecución con el agente `revisor-critico` cuando el encargo sea de
perfil COMPLEJO o cuando el archivo "parezca demasiado limpio".

## El registro de asistencia por IA

`CAL-091` es la comprobación que cierra el bucle del `uso-ia.log`. **La
validación no es un trámite**: acredita que un auditor ha revisado el resultado
de la herramienta, no solo que la herramienta se ejecutó. Sin ella, ante una
inspección no hay forma de distinguir un cálculo revisado de uno aceptado a
ciegas.

```bash
dula validar <encargo> --listar                     # ver el registro
dula validar <encargo> --entrada IA-0003 --quien "MJ Pérez"
```

Al ejecutar la revisión en modo completo (no pre-vuelo) se genera además
`02-documentos/Registro de asistencia automatizada.txt` para el archivo.

## Revisión de calidad del encargo (NIGC2-ES)

Es cosa distinta de esta skill. Cuando el encargo la requiera (EIP siempre;
perfil COMPLEJO según la política de la firma), `CAL-080` la exige y verifica que
está **completada antes de la fecha del informe**. La designación del revisor y
su trabajo son humanos: el plugin solo comprueba que constan.

## Outputs

- `02-documentos/Panel del socio.txt`
- `01-papeles/9.2 Revision de calidad.xlsx`
- **Código de salida 2** si el archivo no está en condiciones de firma.

## Checklist de autoverificación

- [ ] Se ha ejecutado sobre el `encargo.json` **actualizado**, no sobre una copia.
- [ ] Todas las skills de área han registrado sus papeles y excepciones en el
      estado del encargo (si no, la revisión no ve lo que no está registrado).
- [ ] El panel del socio cabe en una página.
- [ ] Cada cuestión del panel lleva su acción concreta, no solo el diagnóstico.
- [ ] La conclusión sobre si se puede firmar es explícita.
- [ ] Se ha dejado constancia de que esta revisión **no sustituye** la revisión
      indelegable del socio firmante (NIA-ES 220 Revisada).
