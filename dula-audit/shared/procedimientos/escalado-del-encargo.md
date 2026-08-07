# escalado-del-encargo

> Configura el alcance según el perfil, y lo eleva si un hallazgo invalida la simplificación.

> **Cuándo:** Úsala tras la estimación del encargo y cada vez que aparezca un hallazgo relevante. Términos: proporcionalidad, partir, perfil, complejidad, configura, automáticamente, skills, activan, profundidad, programas, simplifican, cuáles, refuerzan, perfiles.

> **Necesita:** `[perfil o hallazgo]`

---
Una S.L. de 900 asientos y una industrial de 200.000 no pueden recorrer el mismo
camino. Este motor lo evita, pero con un límite que no se cruza: **la
simplificación nunca compromete la suficiencia de la evidencia**.

## Configuración por perfil

| | LIGERO (2-5 días) | ESTÁNDAR (2-4 semanas) | COMPLEJO (1-2 meses) |
|---|---|---|---|
| Materialidad de ejecución | 75 % de MG | 65 % de MG | 55 % de MG |
| Enfoque dominante | Analítico sustantivo + 100 % de partidas significativas | Mixto | Controles + sustantivo + muestreo estadístico |
| Muestreo | Dirigido no estadístico | MUS en las 2-3 áreas de mayor riesgo | MUS con estratificación |
| Circularización de clientes | Solo si el analítico no concluye | Cobertura reducida | Cobertura plena + alternativos |
| Circularización de proveedores | Solo si el analítico no concluye | Saldos significativos y proveedores clave | Cobertura plena + pasivos no registrados |
| Circularización bancaria | **Siempre, todas las entidades** | **Siempre, todas las entidades** | **Siempre, todas las entidades** |
| Test de asientos del diario | 4 filtros | 9 filtros | 9 filtros + perfilado de usuarios |
| Áreas activadas | Solo con saldo > MP | Todas con saldo > umbral de insignificancia | Todas + específicas del sector |
| Revisión de calidad del encargo | No (salvo trigger) | Según política de la firma | Sí |
| Extracción documental | Muestra dirigida | Lote + muestra de verificación | Lote + muestra ampliada |

## Lo que NO se simplifica en ningún perfil

1. Circularización de **todas** las entidades financieras, incluidos riesgos
   indirectos.
2. Test de asientos del diario (NIA-ES 240.32.a) — se reduce el nº de filtros, no
   se elimina la prueba.
3. Respuesta a la presunción de fraude en el reconocimiento de ingresos.
4. Búsqueda de pasivos no registrados.
5. Cuadres de integridad completos.
6. Evaluación de la independencia y de la aceptación.
7. Carta de manifestaciones adaptada al encargo.
8. Verificación del informe contra las cuentas anuales definitivas.

## Elevación del perfil

Cuando concurre alguno de estos hallazgos, el perfil **sube un escalón**
automáticamente:

| Disparador |
|---|
| Indicio de fraude |
| Incorrección material detectada |
| Deficiencias significativas de control interno |
| Dudas sobre la empresa en funcionamiento |
| Limitación al alcance |
| Incumplimiento de un covenant |
| Operación vinculada no declarada |

```python
from dula import perfil
perfil.valida_simplificacion("LIGERO", {"incorreccion_material": True})
```

El mensaje que devuelve no es un aviso genérico: dice que **las pruebas ya
ejecutadas se dimensionaron con la configuración anterior y pueden haberse
quedado cortas**, y enumera los tres pasos obligatorios: recalcular la MP, revisar
los tamaños de muestra, y reevaluar el riesgo de las áreas ya cerradas.

**Esto es lo importante de esta skill.** Elevar el perfil sin revisar hacia atrás
no sirve de nada: el trabajo ya hecho con el perfil anterior es el que queda
expuesto.

## Sobre la NIA para EMC

La calibración de los programas del perfil LIGERO se ha inspirado en la NIA para
Entidades Menos Complejas del IAASB (efectiva internacionalmente desde el
15/12/2025). **El ICAC no la ha adoptado.** El marco aplicado sigue siendo NIA-ES
y así se declara en todos los papeles de trabajo. Se usa como referencia de
proporcionalidad, no como norma aplicable.

## Consolidación

En v1 el plugin **no construye un programa de consolidación**. Cuando la detecta:
eleva el perfil, marca `[JUICIO-AUDITOR]` y remite a la NIA-ES 600 (Revisada),
aplicable a ejercicios iniciados desde el 01/01/2024. Hacerlo mal sería peor que
no hacerlo.

## Checklist de autoverificación

- [ ] El perfil aplicado es el que consta en `encargo.json`, no uno supuesto.
- [ ] Los overrides duros (EIP, consolidación) se han aplicado.
- [ ] Las simplificaciones aplicadas están documentadas con su fundamento.
- [ ] Ninguna de las ocho prácticas no simplificables se ha omitido.
- [ ] Si el perfil se ha elevado, consta la revisión del trabajo ya ejecutado.
