---
name: estimacion-y-aceptacion
description: Perfil de complejidad, horas y honorarios, independencia, y el alcance que se activa.
when_to_use: 'Úsala cuando el socio esté valorando si aceptar un cliente, fijando precio, presupuestando o planificando la carga de trabajo; cuando pregunte cuánto va a costar un encargo o qué lo encarece; al evaluar la independencia y las incompatibilidades antes de aceptar y al renovar cada ejercicio; y cada vez que aparezca un hallazgo que pueda invalidar la simplificación del perfil. Términos: captar, aceptar, presupuesto, honorarios, precio, tarifa, punto muerto, complejidad, perfil, drivers, independencia, incompatibilidad, amenaza, salvaguarda, blanqueo, titular real, predecesor, carta de encargo, escalado, alcance.'
argument-hint: '[balance.xlsx] o [carpeta-del-encargo]'
---

# Estimación, aceptación y alcance

Tres procedimientos que giran alrededor del mismo dato: **el perfil de
complejidad**.

```bash
cat ${CLAUDE_PLUGIN_ROOT}/procedimientos/<nombre>.md
```

| Procedimiento | Cuándo |
|---|---|
| `estimacion-encargo` | El socio valora si acepta y a qué precio |
| `aceptacion-e-independencia` | Antes de aceptar, y **de nuevo cada ejercicio** |
| `escalado-del-encargo` | Al fijar el alcance, y cada vez que un hallazgo lo invalide |

> **Al invocarla, empieza por aquí.** Di en tres líneas: qué necesitas (el
> balance de sumas y saldos y cinco respuestas del socio), qué vas a devolver
> (informe de decisión en una página) y el comando exacto. Si falta algo, pídelo
> y **no lo inventes**.

## 1. El perfil

Se puntúa 0-100 sobre los drivers que de verdad mueven las horas en el despacho:
volumen de asientos, nº de cuentas, automatización de la facturación, créditos y
pólizas, **leasings**, existencias, subvenciones, operaciones vinculadas, moneda
extranjera, consolidación, primer encargo e **historial de respuesta del cliente**.

```bash
audita estimar drivers.json --tarifas referencias/tarifas.json --encargo .
```

`LIGERO` ≤ 20 · `ESTÁNDAR` 21-50 · `COMPLEJO` > 50.
**Overrides duros:** EIP → COMPLEJO. Consolidación sobre LIGERO → ESTÁNDAR.

Del balance salen solos los drivers cuantitativos. Al socio hay que preguntarle
**en una sola tanda**: automatización de la facturación, nº de leasings, nº de
instrumentos de financiación, cómo responde el cliente, y si es primer encargo,
consolidación o EIP.

**Lo que convierte la estimación en negociación** son los tres factores que más
encarecen, cada uno con su palanca: pedir los cuadros de leasing en Excel y no en
PDF, el listado de facturas en formato de datos, el CIRBE al inicio, un
interlocutor único con calendario comprometido.

Sin `tarifas.json`, los honorarios salen `[PENDIENTE-CLIENTE]`. **No se inventa un
precio.** Y si `historico-encargos.json` está vacío, dilo: el rango sale de horas
base genéricas, no de la experiencia del despacho.

## 2. La aceptación

Las cinco amenazas del Código de Ética (interés propio, autorrevisión, abogacía,
familiaridad, intimidación), cada una con su salvaguarda y su conclusión. Si una
no puede reducirse a un nivel aceptable, **no se acepta** — y eso también se
documenta.

Incompatibilidades de los arts. 14-20 LAC verificadas sobre el auditor, **la red y
las personas vinculadas**, no solo sobre el firmante. Concentración de honorarios.
Prevención del blanqueo con identificación del **titular real**. Y la pregunta que
más se ignora: **¿hay equipo disponible en el calendario del encargo?**

## 3. El alcance, y cuándo deja de valer

| | LIGERO | ESTÁNDAR | COMPLEJO |
|---|---|---|---|
| Materialidad de ejecución | 75 % de MG | 65 % | 55 % |
| Enfoque | Analítico + 100 % de partidas significativas | Mixto | Controles + muestreo estadístico |
| Muestreo | Dirigido | MUS en 2-3 áreas | MUS con estratificación |
| Test de asientos | 4 filtros | 9 filtros | 9 + perfilado de usuarios |
| Revisión de calidad del encargo | No | Según política | Sí |

**Lo que no se simplifica en ningún perfil:** circularización de **todas** las
entidades financieras incluidos riesgos indirectos; test de asientos del diario;
respuesta a la presunción de fraude en ingresos; búsqueda de pasivos no
registrados; cuadres de integridad completos; evaluación de independencia; carta
de manifestaciones adaptada; verificación del informe contra las cuentas
definitivas.

**Elevación automática.** Si aparece indicio de fraude, incorrección material,
deficiencia significativa de control, duda sobre empresa en funcionamiento,
limitación al alcance, covenant incumplido u operación vinculada no declarada, el
perfil sube un escalón. Y lo importante no es subirlo: es que **el trabajo ya
ejecutado se dimensionó con el perfil anterior y puede haberse quedado corto**.
Hay que recalcular la MP, revisar los tamaños de muestra y reevaluar las áreas ya
cerradas.

## Checklist de autoverificación

- [ ] Los drivers cuantitativos salen del balance, no de una suposición.
- [ ] Los no informados figuran `[PENDIENTE-CLIENTE]` y **no puntúan**.
- [ ] Los overrides duros (EIP, consolidación) están aplicados.
- [ ] Sin tarifas, los honorarios salen `[PENDIENTE-CLIENTE]`, no un número.
- [ ] Los factores encarecedores llevan su palanca de abaratamiento.
- [ ] Las cinco amenazas están evaluadas, aunque la conclusión sea que no concurren.
- [ ] Las incompatibilidades se han verificado sobre la red y personas vinculadas.
- [ ] Constan las comprobaciones de blanqueo y el titular real.
- [ ] La disponibilidad real del equipo en el calendario está confirmada.
- [ ] Ninguna de las ocho prácticas no simplificables se ha omitido.
- [ ] Si el perfil se ha elevado, consta la revisión del trabajo ya ejecutado.
