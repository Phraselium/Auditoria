---
name: estado-del-encargo
description: 'Muestra en una pantalla dónde está el encargo y qué falta: fase, perfil, materialidad vigente, papeles concluidos y pendientes, riesgos sin respuesta, excepciones abiertas por severidad, documentación pendiente del cliente y horas consumidas frente a las estimadas. Úsala cuando alguien pregunte cómo va un encargo, qué falta para cerrarlo, o al retomar un encargo tras unos días sin tocarlo.'
---

# Estado del encargo

Con treinta y tantas skills y un estado persistente, «¿dónde estamos y qué falta?»
no es un lujo: es lo primero que se pregunta cualquiera que retoma un encargo.

## Ejecución

```bash
dula estado <carpeta-encargo>
```

El subcomando lee `encargo.json` y `uso-ia.log` y presenta:

## Qué mostrar, y en este orden

```
ENCARGO: <cliente> - ejercicio <AAAA>          Perfil: <PERFIL> (<n> pts)
Marco: <PGC-PYMES|PGC|consolidado>             Actualizado: <fecha>

FASES        aceptación ✔  planificación ✔  campo ◐  cierre ○

MATERIALIDAD Global <MG> EUR | Ejecución <MP> EUR | versión <n> de <total>
             <alerta si el último recálculo afecta al alcance ya ejecutado>

PAPELES      <concluidos>/<total>    Pendientes: <refs>
RIESGOS      <total>, de los cuales <n> sin respuesta ejecutada
EXCEPCIONES  <b> bloqueantes · <r> a resolver · <d> de documentación

PENDIENTES DEL CLIENTE (ruta crítica primero)
  [P1] <área> <descripción>            solicitado <fecha>, comprometido <fecha>
  ...

HORAS        Estimadas <n> h | consumidas <n> h | desviación <±n> h

SIGUIENTE PASO RECOMENDADO
  <la acción concreta que desbloquea más trabajo>
```

Complementos:

```bash
dula horas <encargo>                          # horas por papel
dula horas <encargo> --papel-ref F-1 --imputar 3.5 --quien "LG"
dula pbc <encargo>                            # pendientes del cliente
dula pbc <encargo> --anadir "Cuadros de leasing en Excel" --area F --prioridad 1
dula pbc <encargo> --recibido P001            # marcar como recibido
dula validar <encargo> --listar               # bitácora de uso de IA
```

## El «siguiente paso recomendado»

Es la parte útil. Se determina con esta prioridad:

1. ¿Hay **excepciones bloqueantes**? → resolverlas. Nada más avanza.
2. ¿Está el papel `2.1` sin concluir? → los cuadres, antes que cualquier área.
3. ¿Hay **pendientes de ruta crítica** sin recibir? → reclamarlos, porque su plazo
   de respuesta es lo que marca el calendario.
4. ¿Hay **riesgos sin respuesta** asignada? → `diseno-de-pruebas`.
5. ¿Hay áreas activas sin empezar? → la de mayor saldo primero.
6. ¿Están todas las áreas cerradas? → `evaluacion-de-incorrecciones` y cierre.

## Uso recomendado

- Al **retomar** un encargo tras unos días.
- En la **reunión de seguimiento** del equipo.
- Cuando el socio pregunte por un encargo que no está llevando él.
- Antes de comprometer una fecha de entrega con el cliente.

## Checklist de autoverificación

- [ ] El estado se lee de `encargo.json`, no de la memoria de la conversación.
- [ ] Los pendientes del cliente están ordenados por ruta crítica.
- [ ] El siguiente paso recomendado es **una acción concreta**, no una categoría.
- [ ] Si hay bloqueantes, aparecen los primeros y el siguiente paso es resolverlos.
- [ ] La desviación de horas se muestra aunque sea desfavorable.
