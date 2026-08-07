# Guía de arranque — dula-audit

Una página. Léela entera antes del primer encargo.

---

## 1. Instalar (5 minutos, una sola vez)

### Si usa **claude.ai** (web o escritorio)

1. Descargue `build/dula-audit-claude-ai.zip` del repositorio.
2. **Ajustes → Capacidades**: active «Ejecución de código y creación de archivos».
3. **Ajustes → Capacidades → Skills → Subir skill** y elija el `.zip`.
4. Pruebe con: *«comprueba la instalación de dula-audit con dula doctor»*.

Necesita plan Pro, Max, Team o Enterprise. No hay menú `/`: Claude activa la
skill sola cuando el contexto lo pide.

### Si usa **Claude Code**

Descarga `build/dula-audit-claude-code.zip` y descomprímelo en tu directorio de
skills. **No hace falta marketplace ni git**, así que no hay sincronización que
pueda fallar:

```bash
mkdir -p ~/.claude/skills
unzip -o ~/Descargas/dula-audit-claude-code.zip -d ~/.claude/skills/
```

Reinicia Claude Code y comprueba que carga:

```bash
claude plugin list      # dula-audit@skills-dir · 1.5.0 · loaded
```

Para actualizar: borra la carpeta y vuelve a descomprimir.

<details><summary>Alternativa: desde el marketplace</summary>

```
/plugin marketplace add Phraselium/Auditoria
/plugin install dula-audit@dula
```

Si falla la sincronización, prueba con la URL completa
(`https://github.com/Phraselium/Auditoria.git`). Y para actualizar, sincronizar
no basta: hay que `uninstall` e `install`. Si ya tienes el plugin instalado por
esta vía, desinstálalo antes de usar el directorio de skills — la copia
instalada tiene precedencia.

</details>

Después, en el terminal:

```bash
pip install pandas openpyxl     # las dos únicas dependencias
```

Comprueba la instalación con:

```bash
dula doctor
```

Debe decir «El plugin es operativo». El lanzador `dula` se añade solo al `PATH`
mientras el plugin está activo: no tienes que configurar rutas.

Para probarlo sin instalarlo: `claude --plugin-dir /ruta/a/Auditoria/dula-audit`.

## 2. Configurar (20 minutos, una sola vez)

Abre `skills/convenciones-dula/SKILL.md` —es el fichero de configuración del
plugin— y completa **todos** los campos entre `«»`:

- Denominación del despacho y **números de ROAC** (sociedad y socio firmante).
- **Ruta base** donde vivirán las carpetas de los encargos.
- **Tarifas por categoría** → copia `shared/references/tarifas-ejemplo.json` a
  `tarifas.json` y pon las reales. *Sin esto, el plugin estima horas pero deja los
  honorarios como `[PENDIENTE-CLIENTE]`: no se inventa un precio.*
- **Festivos autonómicos y locales** de la sede de tus clientes (para el test de
  asientos del diario).

**Una tarea pendiente que solo puedes hacer tú:** abre el PDF de la NIA-ES 700R
del ICAC (RICAC de 22/01/2026) y contrasta los tres párrafos marcados
`[VERIFICAR-LITERAL-ICAC]` en `shared/templates/informe-auditoria.md`. Luego borra
la marca. Es cinco minutos y no se puede automatizar desde este entorno.

## 3. Un encargo, de principio a fin

```
/dula-audit:nuevo-encargo "ACME SL" 2025 PGC-PYMES
/estimacion-y-aceptacion 00-fuentes/sumas_y_saldos.xlsx
/ingesta-y-cuadres 00-fuentes/sumas_y_saldos.xlsx   ← puerta de entrada
/planificacion
/areas-de-campo arrendamientos            ← repite por cada área
/tecnicas-de-prueba                       ← muestreo, analíticos, test de asientos
/comparador-documental
/revision-de-calidad                      ← úsala siempre que retomes el encargo
/cierre-del-encargo
/redaccion-informe
```

Y durante la campaña, en la línea de comandos:

```bash
dula estado <encargo>                    # ¿dónde estamos y qué toca ahora?
dula pbc <encargo>                       # ¿qué falta del cliente?
dula horas <encargo>                     # ¿cómo va el presupuesto?
dula validar <encargo> --listar          # bitácora de uso de IA
```

O simplemente pídelo en lenguaje natural: *«audita el inmovilizado de ACME»*,
*«¿cuánto costaría auditar esta sociedad?»*, *«¿puedo firmar ya?»*.

## 4. Las cinco cosas que más tiempo te van a ahorrar

| | Cómo |
|---|---|
| **Leasings** | Junta los cuadros de todos los bancos, sin homogeneizarlos, y ejecuta `area-arrendamientos`. Recalcula el 100 %, clasifica con motivación y saca el cuadro de vencimientos para la memoria |
| **Cuadres** | `ingesta-y-cuadres` en cuanto llegue la contabilidad. Si algo no cuadra, para ahí: cualquier prueba sobre una base descuadrada es trabajo tirado |
| **Memoria** | `comparador-documental` detecta desgloses ausentes, notas heredadas del año anterior con cifras sin actualizar, y descuadres contra el balance |
| **Panel del socio** | `revision-de-calidad --pre-vuelo` **cada semana**, no solo al final |
| **Precio** | `estimacion-encargo` te da los tres factores que más encarecen y **qué pedirle al cliente para abaratarlo**. Eso es material de negociación |

## 5. Lo que hay que pedirle al cliente el primer día

Esto marca la diferencia entre un encargo caro y uno barato:

- Balance de sumas y saldos **al máximo detalle** y libro diario **con fecha y
  usuario**, en Excel o CSV.
- **Autorización firmada para circularizar bancos** — el plazo de respuesta de las
  entidades es de semanas, y es lo primero que se atasca.
- **Cuadros de amortización de las entidades financieras en Excel, no en PDF.**
- Listado de facturas emitidas **en formato de datos**, no en PDF.
- Fecha del recuento de existencias, con antelación para planificar la asistencia.
- Autorizaciones para circularizar clientes, proveedores y abogados.

## 6. Lo que el plugin **no** hace

- **No firma ni decide.** Todas sus conclusiones son propuestas fundamentadas
  sujetas a tu validación. La dirección, supervisión y revisión del encargo es
  responsabilidad indelegable del socio firmante (NIA-ES 220 Revisada).
- **No inventa.** Si falta un dato, sale `[PENDIENTE-CLIENTE]`. Si hace falta
  criterio, `[JUICIO-AUDITOR]`. Nunca rellena en silencio.
- **No recorta alcance para ahorrar tiempo.** Si un atajo no es defendible, te lo
  dice y te propone la alternativa correcta con su coste.
- **No lee contratos escaneados con garantías.** Declara su confianza por campo y
  manda a revisión humana todo lo que baje de 0,85.
- **No consolida.** En v1 detecta la consolidación, eleva el perfil y te lo marca
  como juicio del auditor.

## 7. Si algo falla

| Síntoma | Causa habitual |
|---|---|
| «No se ha localizado la fila de cabecera» | El fichero tiene menos de 2 columnas reconocibles. Comprueba que es la hoja correcta |
| Un cuadre bloqueante que no entiendes | Lee la **causa sugerida** de la excepción. Lo más frecuente: extracción parcial o filas de subtotal leídas como datos |
| La cuenta de resultados sale a cero | El balance está post-regularización. Pásale también el diario |
| Los honorarios salen `[PENDIENTE-CLIENTE]` | Falta `shared/references/tarifas.json` |
| Diferencias sistemáticas de tipo en leasings | Comisiones de apertura no incluidas en el cálculo del banco. Ver `ARR-020` |

| `dula: command not found` | El plugin no está activo. Compruébalo con `/plugin list`; si no aparece, reinstálalo |
| `ERROR: faltan dependencias` | `pip install pandas openpyxl`. El lanzador dice cuál falta |
| El informe de calidad avisa de ejecuciones sin validar | Es lo correcto: valide cada una con `dula validar <encargo> --entrada IA-000X --quien "..."` |

Para ver la traza completa de un error: `DULA_DEBUG=1 python3 -m dula.cli ...`

## 8. Una rutina que merece la pena

Al cerrar cada área: `--horas` en el comando, validar la entrada de la bitácora,
y `dula estado`. Son treinta segundos y evitan que el último día aparezcan a la
vez las excepciones, las horas descuadradas y la bitácora sin firmar.
