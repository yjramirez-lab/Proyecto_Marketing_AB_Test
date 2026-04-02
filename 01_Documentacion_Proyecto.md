# 📚 Crónica Completa del Proyecto: Marketing A/B Testing Pipeline

**App en Vivo:** https://proyectomarketingabtest-wpzvh3ecsi8cqqbtunwn3q.streamlit.app/  
**Repositorio:** https://github.com/yjramirez-lab/Proyecto_Marketing_AB_Test  
**Fecha de creación:** Abril 2026  
**Autor:** Yramis J. Ramírez

> Esta guía es una crónica exhaustiva, paso a paso y con el "pequeño por qué" de cada decisión. Está diseñada para ser ingerida por NotebookLM y servir como base de conocimiento profundo para entrevistas, tu web de aprendizaje personalizado y la construcción de futuros proyectos.

---

## PARTE 0 — Filosofía y Marco Estratégico

### ¿Por qué existe este proyecto?

El mercado laboral está saturado de analistas que pueden hacer gráficas bonitas con datos de Kaggle. Lo que diferencia al **Top 1% de Analistas** (el "Socio Estratégico") es la capacidad de:

- **Reducir incertidumbre:** Transformar preguntas vagas de negocio en hipótesis medibles.
- **Tomar decisiones basadas en evidencia estadística**, no en intuición.
- **Comunicar hallazgos** a perfiles no técnicos (PMs, Management, Marketing).

Este proyecto responde la pregunta más concreta y recurrente de cualquier equipo de Marketing o Producto:

> *"La Variante B tuvo más ventas, ¿la desplegamos a todos los usuarios?"*

La respuesta profesional no es "sí, porque el número es más alto". La respuesta es: **"Hagamos una prueba de hipótesis y determinemos si el incremento fue real o producto del azar estadístico."**

---

## PARTE 1 — Diseño de la Arquitectura (La Hoja en Blanco)

### ¿Qué construimos?

Antes de escribir una línea de código, definimos la arquitectura del pipeline completo:

```
[Python Script]         →  raw_leads.csv (datos sucios)
     ↓
[dbt + DuckDB]          →  stg_leads (limpieza) → fct_ab_test_metrics (métricas)
     ↓
[Jupyter Notebook]      →  EDA + Z-Test (análisis estadístico detallado)
     ↓
[Streamlit App]         →  Dashboard interactivo (presentación ejecutiva)
     ↓
[GitHub + Streamlit Cloud] → Publicación pública en el portafolio
```

### ¿Por qué este flujo y no simplemente un Jupyter + CSV?

| Enfoque Básico | Nuestro Enfoque (Modern Data Stack) |
|---|---|
| CSV → Pandas → Jupyter | Python → dbt/DuckDB → Streamlit |
| No se puede presentar a no-técnicos | App interactiva accesible para cualquiera |
| No demuestra Data Engineering | Demuestra Analytics Engineering real |
| No tiene estructura corporativa | Tiene capas (Staging, Marts) igual que grandes compañías |

---

## PARTE 2 — El Generador de Datos Sintéticos (`00_generador_trafico.py`)

### ¿Qué hace este script?

En un empresa real, conectarías a una base de datos de producción (MySQL, Postgres, BigQuery). Como este es un proyecto de portafolio, creamos un generador de datos que simula exactamente cómo lucen los datos reales de un "tracker de eventos" de marketing.

### ¿Por qué generamos datos "sucios" a propósito?

Este es el punto diferenciador frente a usar un dataset limpio de Kaggle. En el mundo real:
- **Los trackers tienen bugs**: un mismo usuario puede registrarse dos veces (lead duplicado).
- **Los formularios tienen campos opcionales**: el campo `dispositivo` puede estar vacío.
- **Las zonas horarias fallan**: generan timestamps imposibles (año 1999 o futuro).
- **El código de campaña es inconsistente**: llegan variantes `'C'`, `'test'`, `'X'` por error humano.

Al generar estos problemas nosotros mismos, demostramos que los conocemos y sabemos cómo atacarlos.

### Detalle técnico del script

```python
# El "lifting" que introduce sesgo estadístico real
# La Variante A convierte al 8%, la B convierte al 12%
base_rate = 0.08 if variant == "A" else 0.12
conversion = 1 if random.random() < base_rate else 0
```

**¿Por qué la diferencia de rates?** Para que el test estadístico al final tenga algo significativo que detectar. En un test real no sabes el rate de antemano; ese es el objetivo del A/B test.

### Ruido inyectado

| Tipo de Ruido | Cantidad | Por Qué Importa |
|---|---|---|
| Leads duplicados | ~7 registros | Simula un tracker que dispara el evento dos veces |
| Variantes inválidas | ~15 registros | Error humano en el etiquetado de la campaña |
| Fechas imposibles | ~10 registros | Bug en sincronización de zona horaria del servidor |
| Dispositivos nulos | ~5% del total | Campo opcional en el formulario de registro |

---

## PARTE 3 — El Data Warehouse con dbt + DuckDB

### Paso 3.1 — Instalación

```bash
pip install dbt-core dbt-duckdb
```

**¿Por qué `dbt-core` Y `dbt-duckdb` por separado?**  
`dbt-core` es el motor de transformación (el intérprete de SQL). `dbt-duckdb` es el "adaptador" que le dice a dbt cómo hablar con DuckDB específicamente. Para cada base de datos (Snowflake, BigQuery, Postgres) existe un adaptador diferente. Este modelo de plugins hace que dbt sea universalmente compatible.

### Paso 3.2 — Estructura de carpetas (sin usar `dbt init`)

En lugar de correr `dbt init` (que genera decenas de archivos de ejemplo innecesarios), creamos la estructura mínima a mano:

```
marketing_dbt/
├── dbt_project.yml       ← Configuración del proyecto (nombre, rutas, materialización)
├── profiles.yml          ← Credenciales y conexión a la BD (en local, dentro del proyecto)
└── models/
    ├── staging/
    │   ├── stg_leads.sql  ← Capa de limpieza
    │   └── schema.yml     ← Tests de calidad de datos
    └── marts/
        └── fct_ab_test_metrics.sql  ← Capa de métricas de negocio
```

**¿Por qué 2 capas (staging + marts)?**  
Este es el estándar de la industria. La capa `staging` hace transformaciones de datos crudos (limpieza técnica: tipos de datos, nulos, duplicados). La capa `marts` hace transformaciones de negocio (calcular métricas como tasas de conversión). Separarlos permite reutilizar el staging en múltiples marts y mantener la lógica de negocio centralizada.

### Paso 3.3 — `profiles.yml` (la conexión)

```yaml
marketing_duckdb:
  outputs:
    dev:
      type: duckdb
      path: marketing.duckdb   # crea el archivo .duckdb en el mismo directorio
```

**¿Por qué guardamos el `profiles.yml` dentro del proyecto?**  
Por defecto, dbt busca `profiles.yml` en `~/.dbt/` (la carpeta home del usuario). Al guardarlo dentro del proyecto y pasar `--profiles-dir .` al correr dbt, el proyecto se vuelve **portátil**: cualquier persona que clone el repositorio puede correrlo sin configurar nada manualmente.

### Paso 3.4 — `stg_leads.sql` (El modelo de limpieza)

```sql
WITH raw_data AS (
    SELECT * FROM read_csv_auto('../raw_leads.csv')
),
cleaned AS (
    SELECT
        lead_id,
        CAST(timestamp AS TIMESTAMP) AS event_timestamp,
        variante AS test_variant,
        CASE WHEN dispositivo IS NULL THEN 'unknown' ELSE dispositivo END AS device_type,
        fuente AS traffic_source,
        CAST(conversion AS INTEGER) AS is_converted
    FROM raw_data
    WHERE variante IN ('A', 'B')          -- Elimina variantes inválidas
      AND CAST(timestamp AS TIMESTAMP) >= '2020-01-01'  -- Elimina fechas absurdas
      AND CAST(timestamp AS TIMESTAMP) <= '2030-01-01'
),
, deduplicated AS (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY lead_id ORDER BY event_timestamp DESC) AS rn
    FROM cleaned
)
SELECT lead_id, event_timestamp, test_variant, device_type, traffic_source, is_converted
FROM deduplicated
WHERE rn = 1  -- Conserva solo el registro más reciente por lead
```

**¿Por qué `ROW_NUMBER() OVER (PARTITION BY lead_id)` y no simplemente `SELECT DISTINCT`?**  
`DISTINCT` falla cuando los duplicados tienen *diferente* timestamp (mismo usuario, dos momentos distintos). En nuestro dataset, el ruido intencional generó exactamente eso. La función de ventana `ROW_NUMBER()` nos permite seleccionar el registro más reciente de cada usuario, que es la lógica correcta de negocio (queremos el estado más actualizado del lead).

**Esto es lo que preguntaría un Senior Engineer en entrevista.** La respuesta correcta es siempre `ROW_NUMBER()` + filtro, no `DISTINCT`.

### Paso 3.5 — Error detectado por `dbt test` (y su solución)

Al correr `dbt test` por primera vez:
```
FAIL 7 unique_stg_leads_lead_id
```

dbt detectó exactamente los 7 duplicados que inyectamos intencionalmente. El error fue pedagógicamente valioso: nos obligó a mejorar el SQL de limpieza usando `ROW_NUMBER()`, pasando de una solución naïve a la solución estándar de la industria.

Después del fix:
```
PASS=5 WARN=0 ERROR=0 SKIP=0 — Completed successfully
```

### Paso 3.6 — Comandos de ejecución

```bash
# Estando dentro de marketing_dbt/
dbt run --profiles-dir .
# ✅ 1 of 2 OK: stg_leads (vista)
# ✅ 2 of 2 OK: fct_ab_test_metrics (tabla)

dbt test --profiles-dir .
# ✅ PASS=5: unique_lead_id, not_null_lead_id, accepted_values_variant, etc.
```

---

## PARTE 4 — El Notebook de Análisis (`AB_Testing_Report.ipynb`)

### Error encontrado: `ModuleNotFoundError: No module named 'pandas'`

**¿Por qué ocurrió?** VS Code puede tener varios "kernels" de Python (entornos). Al abrir el notebook, seleccionó automáticamente un kernel que no tenía las librerías instaladas.

**Soluciones:**
1. Usar magic commands en la primera celda: `%pip install pandas numpy seaborn scipy statsmodels`
2. Seleccionar manualmente el kernel correcto (Python 3.13 del sistema) desde la esquina superior derecha del notebook en VS Code.

Optamos por la segunda para que el entorno sea estable y consistente.

### La Prueba de Hipótesis (Z-Test de Proporciones)

**¿Por qué usamos Z-Test y no T-Test o Chi-Square?**

| Test | Cuándo Usarlo |
|---|---|
| T-Test | Comparar medias de variables continuas (ej. tiempo en página) |
| Chi-Square | Comparar frecuencias categóricas (ej. distribución de dispositivos) |
| **Z-Test para proporciones** | **Comparar tasas (ej. % de conversión)** ← Nuestro caso |

Como comparamos tasas de conversión (proporciones: `conversiones / usuarios`), el Z-Test es matemáticamente el más apropiado.

### Resultados obtenidos

| Métrica | Variante A | Variante B |
|---|---|---|
| Usuarios | 2,425 | 2,475 |
| Conversiones | 200 | 276 |
| Tasa de conversión | **8.25%** | **11.15%** |
| **p-value** | — | **0.0006** |

**Interpretación:** Un p-value de 0.0006 significa que hay un 0.06% de probabilidad de haber visto esta diferencia *por azar puro*, asumiendo que ambas variantes son iguales. Como 0.06% < 5% (nuestro umbral de riesgo), rechazamos la hipótesis nula. La diferencia es real.

---

## PARTE 5 — La App de Presentación (`app.py`)

### Versión 1: Con dbt (solo local)

La primera versión del `app.py` leía del archivo `marketing.duckdb` generado por dbt. Funciona perfectamente en local:
```python
con = duckdb.connect('marketing_dbt/marketing.duckdb', read_only=True)
```

**Problema para el deploy:** Streamlit Cloud no puede correr `dbt run`. El archivo `.duckdb` no puede estar en el repositorio porque es un archivo binario pesado y se genera dinámicamente.

### Versión 2: Autocontenida (compatible con Streamlit Cloud)

Rediseñamos el `app.py` para que sea completamente autocontenido:
1. **Genera los datos sintéticos** en memoria con Python + `random`
2. **Los limpia con DuckDB** directamente (sin dbt), replicando el SQL de `stg_leads.sql`
3. **Agrega las métricas** (replicando `fct_ab_test_metrics.sql`)
4. **Renderiza el dashboard** con Streamlit + Plotly

```python
@st.cache_data  # Cachea el resultado para no regenerar en cada recarga
def build_clean_metrics():
    # ... genera datos, limpia con DuckDB, calcula métricas ...
    return stg_df, metrics_df
```

**¿Por qué `@st.cache_data`?** Streamlit re-ejecuta todo el script en cada interacción del usuario. Sin el caché, regeneraría datos aleatorios en cada clic, haciendo los resultados inconsistentes. El decorador asegura que los datos se generen una sola vez por sesión.

### Secciones del Dashboard

1. **Tabla de métricas** — Datos directos del "DWH" (DuckDB)
2. **KPIs en columnas** — Conversion Rate A, B y Lift (+2.90pp)
3. **Gráfico de barras comparativo** — Plotly Express con colores A=azul, B=verde
4. **Breakdown por dispositivo** — Demuestra que el efecto es consistente en todos los segmentos
5. **Z-Test interactivo** — Con expander explicativo y banner verde/amarillo según resultado

---

## PARTE 6 — Publicación en GitHub + Streamlit Cloud

### `.gitignore` (qué NO commit-ear)

Archivos que se crearon automáticamente y no deben estar en el repositorio:
- `*.duckdb` — Se genera corriendo dbt localmente
- `raw_leads.csv` — Se genera corriendo el script Python
- `marketing_dbt/target/` — Output de compilación de dbt
- `.ipynb_checkpoints/` — Checkpoints del Jupyter

### Comandos de Git ejecutados

```bash
git init
git add .
git commit -m "feat: Marketing A/B Testing Pipeline — dbt + DuckDB + Streamlit"
git branch -M main
git remote add origin https://github.com/yjramirez-lab/Proyecto_Marketing_AB_Test.git
git push -u origin main
```

**¿Por qué `git branch -M main`?** Git crea la rama por defecto con el nombre `master`. GitHub ahora usa `main` por convención. Este comando renombra la rama para que sea compatible.

### Proceso de deploy en Streamlit Cloud

1. Ingresar a [share.streamlit.io](https://share.streamlit.io)
2. Conectar con la cuenta de GitHub
3. Seleccionar repositorio `Proyecto_Marketing_AB_Test`
4. Branch: `main` | Main file path: `app.py`
5. Click **Deploy** → URL generada automáticamente

**¿Necesita un `requirements.txt`?** Sí. Streamlit Cloud lee este archivo para saber qué librerías instalar en el servidor. Sin él, fallará con un `ModuleNotFoundError`.

```
# requirements.txt
pandas
numpy
seaborn
matplotlib
scipy
statsmodels
streamlit
plotly
duckdb
dbt-core
dbt-duckdb
```

---

## PARTE 7 — Troubleshooting Completo (Errores Reales Enfrentados)

| Error | Causa | Solución |
|---|---|---|
| `ModuleNotFoundError: pandas` en Jupyter | VS Code eligió un kernel sin librerías | Seleccionar el kernel de Python 3.13 del sistema |
| `streamlit: no se reconoce como cmdlet` | Streamlit se instaló en una ruta no incluida en el PATH de Windows | Usar `python -m streamlit run app.py` en lugar de `streamlit run` |
| `dbt test FAIL 7 unique_stg_leads_lead_id` | Los duplicados inyectados tenían timestamps distintos, `DISTINCT` no los eliminó | Reimplementar con `ROW_NUMBER() OVER (PARTITION BY lead_id)` |
| `syntax error at or near "deduplicated"` en dbt | El segundo CTE no tenía coma separadora | Agregar `,` antes de `deduplicated as (` |
| `python -m dbt` falla | dbt no tiene módulo `__main__` ejecutable | Usar la ruta absoluta del ejecutable: `C:\Users\yrami\AppData\Roaming\Python\Python313\Scripts\dbt.exe` |

---

## PARTE 8 — Glosario Técnico del Proyecto

| Término | Definición |
|---|---|
| **A/B Test** | Experimento controlado donde se divide la audiencia en dos grupos para comparar dos versiones de algo |
| **Hipótesis Nula (H₀)** | La suposición inicial de que no hay diferencia entre A y B |
| **P-Value** | Probabilidad de observar los resultados obtenidos *si la hipótesis nula fuera verdadera*. Menor es más significativo |
| **Nivel de Significancia (α)** | Umbral de tolerancia al error. Usamos α=0.05 (5% de riesgo de falso positivo) |
| **Lift** | El incremento porcentual de la Variante B sobre la A |
| **dbt** | Data Build Tool. Herramienta que convierte SQL en pipelines de transformación de datos reproducibles y testeables |
| **DuckDB** | Base de datos OLAP (analítica) que corre en un archivo local. Muy rápida para queries analíticos |
| **OLAP** | Online Analytical Processing. Optimizado para consultas de agregación sobre grandes volúmenes |
| **Staging** | Primera capa de transformación: limpieza técnica del dato crudo |
| **Mart / Fact Table** | Segunda capa: métricas de negocio calculadas sobre datos ya limpios |
| **`ROW_NUMBER()`** | Función de ventana SQL que asigna un número de fila dentro de cada grupo (`PARTITION BY`) |
| **`@st.cache_data`** | Decorador de Streamlit que guarda el resultado de una función en caché para no reejecutarla |
| **Z-Test de Proporciones** | Test estadístico para comparar si dos tasas (proporciones) son significativamente distintas |

---

## PARTE 9 — Preguntas de Entrevista con Respuestas de Experto

**Q: ¿Por qué usaste DuckDB y no una base de datos "real" como PostgreSQL?**  
A: *"El volumen de datos (5,000 registros) cabía perfectamente en memoria local. DuckDB elimina toda la fricción de DevOps (no hay servidor que levantar, no hay costos de infra) mientras demuestra exactamente las mismas capacidades analíticas. Para producción con volúmenes de millones de registros, el mismo código dbt se conecta a Snowflake o BigQuery cambiando solo el perfil."*

**Q: ¿Por qué usaste dos capas en dbt (staging y marts) para un proyecto tan pequeño?**  
A: *"Porque demuestra pensar en sistemas y arquitecturas escalables, no en soluciones ad-hoc. Si mañana el negocio necesita una tabla de retención por dispositivo o por geografía, puedo construirla sobre `stg_leads` sin tocar el código de limpieza. La separación de responsabilidades es un principio de ingeniería de software aplicado a datos."*

**Q: ¿Cómo elegiste el nivel de significancia alfa = 0.05?**  
A: *"Es la convención de la industria para decisiones de marketing y producto, que equilibra el riesgo de falso positivo (desplegar algo que no funciona) contra el coste de oportunidad de falso negativo (no desplegar algo que sí funciona). En industrias de mayor riesgo como salud o banca, se usaría α=0.01."*

**Q: Si el p-value hubiera salido 0.08 (mayor que 0.05), ¿qué le dirías al PM?**  
A: *"Le diría que no podemos concluir que el cambio sea efectivo con el nivel de confianza requerido. La diferencia observada podría ser ruido estadístico. Recomendaría dos acciones: (1) aumentar el tamaño de la muestra para ganar más poder estadístico, o (2) revisar si el lift esperado justifica continuar el experimento según el análisis de MDE (Minimum Detectable Effect)."*
