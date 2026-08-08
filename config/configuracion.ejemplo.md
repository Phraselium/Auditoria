# Configuración del despacho

Copie este fichero a **`config/configuracion.md`** y complete los campos entre
`«»`. Ese destino está en `.gitignore`: los datos del despacho no se versionan.

El detalle completo de convenciones, umbrales e índice de papeles vive en
`skills/convenciones-despacho/SKILL.md`. Aquí solo van los datos identificativos
y los que cambian de un despacho a otro.

## Identificación

| Campo | Valor |
|---|---|
| Denominación social | «» |
| Nº de inscripción en el ROAC de la sociedad | «S____» |
| Socio firmante habitual y su nº de ROAC | «Nombre Apellidos — _____» |
| Domicilio a efectos del informe | «» |

## Operativa

| Campo | Valor |
|---|---|
| Ruta base de los encargos | «C:\Auditorias» |
| Ejercicio en curso | «2025» |
| Festivos locales de la sede | «» |
| Categorías profesionales y tarifa/hora | ver `referencias/tarifas.json` |

## Tarifas

Copie `referencias/tarifas-ejemplo.json` a `referencias/tarifas.json` (también
ignorado por git) y ponga las suyas. **Sin ese fichero el plugin estima horas
pero devuelve los honorarios como `[PENDIENTE-CLIENTE]`: no inventa un precio.**

## Verificación pendiente

Contraste los párrafos marcados `[VERIFICAR-LITERAL-ICAC]` de
`plantillas/informe-auditoria.md` contra el PDF oficial de la NIA-ES 700R del
ICAC, y borre la marca. Es cinco minutos y no se puede automatizar.
