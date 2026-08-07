---
name: plan-y-solicitud-informacion
description: Genera la lista de documentación a solicitar al cliente personalizada al perfil de la entidad, priorizada por ruta crítica, con calendario, responsables y seguimiento de pendientes y recordatorios. Incluye modo específico para cliente que no responde (escalado, alternativas de evidencia, impacto en alcance y en el informe) y para cliente que envía todo desordenado (triaje y clasificación automática de lo recibido). Úsala tras la planificación y para hacer seguimiento de pendientes durante toda la campaña.
---

# Plan y solicitud de información (PBC)

Una PBC genérica es una PBC que el cliente ignora. Esta se construye con las áreas
que el encargo tiene realmente activas, con lo que de verdad hace falta, y
priorizada por lo que bloquea el resto del trabajo.

## 1. Construcción de la PBC

Se compone a partir de:

- Las áreas activas según el perfil (`escalado-del-encargo`).
- La sección **«Documentación a solicitar al cliente»** de cada pack de programa
  en `shared/references/programas/`.
- Los riesgos identificados que exigen documentación específica.

**No pidas lo que no vas a usar.** Cada elemento de la PBC debe apuntar a un
procedimiento concreto. Una PBC inflada retrasa la entrega de lo importante.

## 2. Ruta crítica

| Prioridad | Qué | Por qué bloquea |
|---|---|---|
| **1 — Bloqueante** | Balance de sumas y saldos y diario | Sin ellos no hay cuadres y sin cuadres no hay trabajo de campo |
| **1 — Bloqueante** | Autorización firmada para circularizar bancos | El plazo de respuesta de las entidades es de semanas |
| **2 — Calendario** | Fecha del recuento de existencias | Si se pasa, no se puede recuperar |
| **2 — Calendario** | Autorización para circularizar clientes, proveedores y abogados | Plazo de respuesta y reiteraciones |
| **3 — Alto impacto** | Cuadros de leasing y de financiación **en Excel** | Es donde más horas se ahorran o se pierden |
| **4 — Resto** | Inventarios, contratos, actas, modelos fiscales | Se pueden solapar con el trabajo de campo |

Las peticiones de prioridad 1 y 2 **salen antes de que empiece el trabajo de
campo**, no cuando se llega al área.

## 3. Formato de la petición

Pide **datos, no PDF**. La diferencia entre recibir el listado de facturas en
Excel o en PDF son horas de trabajo por área. Dilo expresamente en la PBC:

> «Los listados de facturas, el inventario de inmovilizado y los cuadros de
> amortización de las entidades financieras, **en formato Excel o CSV**. Si solo
> están disponibles en PDF, indíquenoslo para planificar el tiempo adicional de
> extracción.»

## 4. Modo «cliente que no responde»

Escalado en cuatro pasos, documentando cada uno:

1. **Recordatorio** al interlocutor con la lista de pendientes y su fecha.
2. **Escalado** a la dirección financiera o al administrador, por escrito.
3. **Comunicación formal** de que la falta de información afecta al calendario y
   puede afectar al alcance. Es el momento de dejarlo por escrito.
4. **Evaluación del efecto**: si no se obtiene la evidencia, hay **limitación al
   alcance**, con su efecto en la opinión según el árbol de decisión de
   `redaccion-informe`.

**Alternativas de evidencia antes de concluir que hay limitación:** movimientos
posteriores al cierre, confirmaciones de terceros, documentación pública
(Registro Mercantil, catastro, registros administrativos), procedimientos
analíticos con datos independientes.

## 5. Modo «cliente que envía todo desordenado»

El problema opuesto y casi igual de caro. Triaje de lo recibido:

1. **Inventario de lo que ha llegado**, con su huella SHA-256.
2. **Clasificación por área** según el índice de papeles de trabajo.
3. **Identificación de duplicados y versiones**: el mismo fichero enviado tres
   veces con nombres distintos es habitual. La huella lo detecta.
4. **Contraste contra la PBC**: qué está cubierto, qué sigue pendiente y qué ha
   llegado sin haberse pedido (que a veces es lo más interesante).
5. **Devolución al cliente** de la lista de pendientes **reducida**, solo con lo
   que falta. Mandarle la PBC entera otra vez garantiza que no la lea.

## 6. Seguimiento

Los pendientes viven en `encargo.json`, no en un correo:

```bash
export PYTHONPATH=${CLAUDE_PLUGIN_ROOT}/shared/scripts
python3 -m dula.cli pbc <encargo> --anadir "Cuadros de leasing en Excel" \
    --area F --prioridad 1 --responsable "Dirección financiera" --comprometido 2026-02-15
python3 -m dula.cli pbc <encargo> --recordar P001     # anota un recordatorio
python3 -m dula.cli pbc <encargo> --recibido P001     # sale de la lista
python3 -m dula.cli pbc <encargo>                     # listado por ruta crítica
```

Prioridades: **1** bloqueante · **2** calendario · **3** alto impacto en horas ·
**4** resto. `estado-del-encargo` los muestra ordenados y los usa para determinar
el siguiente paso recomendado: mientras haya pendientes de prioridad 1 o 2 sin
recibir, reclamarlos es lo que desbloquea más trabajo.

## Outputs

- `02-documentos/PBC <cliente> <ejercicio>.xlsx` — por área, con prioridad,
  responsable y fechas.
- Lista de pendientes viva en `encargo.json`.
- Correos de petición y de recordatorio redactados.

## Checklist de autoverificación

- [ ] La PBC se ha construido con las áreas **activas** del encargo, no con una
      plantilla completa.
- [ ] Cada elemento apunta a un procedimiento concreto.
- [ ] Las peticiones de ruta crítica están identificadas y salen primero.
- [ ] Se pide formato de datos, no PDF, allí donde importa.
- [ ] Las autorizaciones de circularización están solicitadas con antelación.
- [ ] La fecha del recuento de existencias está confirmada, si aplica.
- [ ] Los pendientes están registrados en `encargo.json`.
