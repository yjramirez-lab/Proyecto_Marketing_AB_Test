# 📊 Marketing A/B Testing Pipeline

> **App en vivo →** https://proyectomarketingabtest-wpzvh3ecsi8cqqbtunwn3q.streamlit.app/
> **Código →** https://github.com/yjramirez-lab/Proyecto_Marketing_AB_Test

---

⬆️ **INSTRUCCIÓN PARA NOTION:** Pega este texto en una página nueva de Notion usando **"Import" → "Text & Markdown"**. Luego sube la imagen `app_preview.png` que está en la carpeta del proyecto y colócala al inicio de la página como imagen de portada o bloque de imagen.

---

## 🗂️ Ficha del Proyecto

| | |
| --- | --- |
| **Estado** | ✅ Publicado |
| **Demo** | [Ver App en Vivo](https://proyectomarketingabtest-wpzvh3ecsi8cqqbtunwn3q.streamlit.app/) |
| **Repositorio** | [GitHub](https://github.com/yjramirez-lab/Proyecto_Marketing_AB_Test) |
| **Tipo** | Data Engineering + Product Analytics |
| **Rol demostrado** | Analytics Engineer / Product Analyst |
| **Herramientas** | Python, dbt, DuckDB, Streamlit, Pandas, SciPy |
| **Industria** | Marketing Digital / Growth / E-commerce |


## 🎯 El Problema de Negocio

La campaña de email marketing probó dos versiones de un botón de llamada a la acción (CTA):

- **Variante A — Control:** Diseño tradicional, sin cambios
- **Variante B — Tratamiento:** Nuevo CTA + mensaje de urgencia

La pregunta del equipo de Marketing fue: *"La Variante B tiene más ventas este mes, ¿la desplegamos a todos?"*

La respuesta de un analista profesional no es "sí porque el número es mayor". La respuesta es: **¿Es la diferencia estadísticamente significativa o fue simple azar?**


## 📐 Arquitectura del Pipeline

```
Script Python   →   raw_leads.csv (con ruido intencional)
                            ↓
    dbt + DuckDB   →   stg_leads (limpieza) → fct_ab_test_metrics
                            ↓
  Jupyter Notebook   →   EDA + Z-Test estadístico
                            ↓
  Streamlit App   →   Dashboard ejecutivo interactivo
```


## 🛠️ Stack Tecnológico

**Python** — Generación de datos sintéticos con ruido intencional (duplicados, nulos, fechas inválidas) para simular realidad.

**dbt-core + dbt-duckdb** — Capa de transformación SQL. Dos modelos:
- `stg_leads.sql` — Limpieza con `ROW_NUMBER() OVER (PARTITION BY lead_id)` para deduplicar
- `fct_ab_test_metrics.sql` — Métricas de negocio agregadas por variante

**DuckDB** — Base de datos analítica OLAP local. Lee el CSV directamente sin servidor.

**SciPy / StatsModels** — Z-Test de proporciones para inferencia estadística.

**Streamlit** — Dashboard interactivo desplegado en la nube (gratuito).


## 📊 Resultados del Experimento

| Métrica | Variante A (Control) | Variante B (Tratamiento) |
| --- | --- | --- |
| Usuarios | 2,425 | 2,475 |
| Conversiones | 200 | 276 |
| **Tasa de Conversión** | **8.25%** | **11.15%** |
| **Lift** | — | **+2.90 pp** |
| **P-Value** | — | **0.0006** |

✅ **Conclusión:** Rechazamos la hipótesis nula. La Variante B genera un incremento real y estadísticamente significativo. El nuevo CTA debe desplegarse a producción.


## �️ Diseño de Datos

El dataset crudo `raw_leads.csv` tiene 5,000 registros con ruido deliberado:

| Campo | Tipo | Ruido Inyectado |
| --- | --- | --- |
| `lead_id` | String | Duplicados (simula bug del tracker) |
| `timestamp` | Datetime | Fechas de 1999 y 2050 |
| `variante` | String | Valores `'C'`, `'test'` inválidos |
| `dispositivo` | String | ~5% de valores nulos |
| `conversion` | Integer (0/1) | — |

La capa de **staging en dbt** elimina todo ese ruido antes del análisis.


## ⚗️ Metodología Estadística

**Test utilizado:** Z-Test para Proporciones de Dos Muestras

**¿Por qué Z-Test y no T-Test?**
Porque comparamos proporciones (tasas de conversión), no medias de variables continuas. El T-Test es para medias; el Z-Test para proporciones es el estándar de la industria.

**Hipótesis:**
- H₀: La Variante B no convierte más que la A (la diferencia es ruido)
- H₁: La Variante B sí convierte más que la A
- Alfa: 0.05 (5% de tolerancia al falso positivo)

**Resultado:** p-value = 0.0006 → Rechazamos H₀ con 99.94% de confianza.


## � Aprendizajes Clave

**Analytics Engineering con dbt**
dbt separa la lógica de limpieza técnica (staging) de la lógica de negocio (marts), permitiendo que cada capa sea reutilizable, testeable y documentada.

**DuckDB como Data Warehouse local**
Permite hacer analítica OLAP de alto rendimiento sin infraestructura cloud. El mismo código de dbt funciona con Snowflake o BigQuery cambiando solo el perfil de conexión.

**Datos sucios como ejercicio pedagógico**
Construir datos con errores intencionales demuestra que entiendes los problemas reales de producción, no solo los datasets perfectos de Kaggle.

**Streamlit como capa de comunicación**
El 90% del valor de un análisis se pierde si no se comunica bien. Streamlit traduce el resultado estadístico en un dashboard que cualquier decisor puede entender sin conocer Python.


## 🗣️ Cómo Presentar Este Proyecto en Entrevistas

*"Construí un pipeline completo de A/B Testing para validar si un rediseño de CTA generaba conversiones reales o era ruido estadístico. Usé dbt con DuckDB para limpiar y estructurar los datos con SQL, eliminé duplicados usando funciones de ventana analíticas (ROW_NUMBER), y validé la hipótesis con un Z-Test de proporciones. El p-value fue de 0.0006, confirmando un lift real de 2.9 puntos porcentuales. Presenté los resultados en una app Streamlit pública para que el equipo de marketing pueda consultarlo sin conocimientos técnicos."*


---


## ⚙️ Ejecución Técnica Completa — Paso a Paso

Esta sección documenta cada comando, instalación y decisión técnica tomada durante la construcción del proyecto, desde cero hasta el despliegue en producción.


### PASO 1 — Estructura del Proyecto

Se creó la carpeta del proyecto y los archivos base a mano (sin scaffolds genéricos):

```
Proyecto_Marketing_AB_Test/
├── 00_generador_trafico.py
├── AB_Testing_Report.ipynb
├── app.py
├── requirements.txt
├── .gitignore
├── 01_Documentacion_Proyecto.md
├── 02_Notion_Portfolio.md
└── marketing_dbt/
    ├── dbt_project.yml
    ├── profiles.yml
    └── models/
        ├── staging/
        │   ├── stg_leads.sql
        │   └── schema.yml
        └── marts/
            └── fct_ab_test_metrics.sql
```

**¿Por qué crear la estructura manualmente y no usar `dbt init`?**
`dbt init` genera decenas de archivos de ejemplo que añaden ruido. Crear la estructura mínima mano demuestra que se entienden las entrañas del framework, no solo que se sabe ejecutar un comando.


### PASO 2 — Generación de Datos Sintéticos

**Script:** `00_generador_trafico.py`

```python
# Librerías usadas — todas de la librería estándar de Python, sin instalación extra
import random
import csv
from datetime import datetime, timedelta

# El "lifting" real que hace el test statisticamente significativo
base_rate = 0.08 if variant == "A" else 0.12

# Ruido intencional inyectado al dataset
# 1. Duplicados (~7 registros)
# 2. Variantes inválidas ('C', 'test', 'X') en ~15 registros
# 3. Fechas imposibles (1999) en ~10 registros
# 4. Dispositivo None en ~5% del dataset
```

**Ejecución:**

```bash
python 00_generador_trafico.py
# Output: raw_leads.csv generado con 5,000+ registros
```

**¿Por qué 5,000 registros y no 500?**
Con menos de 1,000 registros por variante, el test estadístico tiene muy bajo "poder" y el p-value puede no ser significativo aunque la diferencia real exista. 5,000 garantiza suficiente potencia estadística.


### PASO 3 — Instalación de dbt y DuckDB

```bash
pip install dbt-core dbt-duckdb
```

**¿Por qué dos paquetes separados?**
`dbt-core` es el motor (el intérprete de SQL y la lógica de transformación). `dbt-duckdb` es el adaptador específico para DuckDB. Este modelo de plugins hace que dbt sea compatible con cualquier base de datos cambiando solo el adaptador: el mismo código funciona con Snowflake, BigQuery o Postgres.

**Nota:** La instalación dejó el ejecutable `dbt.exe` en una ruta no incluida en el PATH de Windows:
```
C:\Users\yrami\AppData\Roaming\Python\Python313\Scripts\dbt.exe
```
Por eso los comandos dbt se ejecutaron con la ruta absoluta o desde Python directamente.


### PASO 4 — Configuración de dbt

**`marketing_dbt/dbt_project.yml`** — Define el nombre del proyecto y la materialización:
```yaml
name: 'marketing_dbt'
models:
  marketing_dbt:
    staging:
      +materialized: view     # Las vistas no ocupan espacio, son consultas guardadas
    marts:
      +materialized: table    # Las tablas sí persisten en disco, más rápidas de consultar
```

**`marketing_dbt/profiles.yml`** — Define la conexión a DuckDB:
```yaml
marketing_duckdb:
  outputs:
    dev:
      type: duckdb
      path: marketing.duckdb  # Crea el archivo .duckdb en la carpeta del proyecto
  target: dev
```

**¿Por qué guardar `profiles.yml` dentro del proyecto?**
Por defecto dbt lo busca en `~/.dbt/` (carpeta home). Al guardarlo en el proyecto y pasar `--profiles-dir .` al ejecutar, el proyecto se vuelve portátil: cualquier persona que clone el repositorio lo corre sin configurar nada.


### PASO 5 — Modelos dbt

**`models/staging/stg_leads.sql`** — Capa de limpieza:

```sql
WITH raw_data AS (
    -- DuckDB lee el CSV directamente, sin necesidad de importarlo previamente
    SELECT * FROM read_csv_auto('../raw_leads.csv')
),
cleaned AS (
    SELECT
        lead_id,
        CAST(timestamp AS TIMESTAMP) AS event_timestamp,
        variante AS test_variant,
        -- Imputa nulos con 'unknown' (no elimina filas, conserva información)
        CASE WHEN dispositivo IS NULL THEN 'unknown' ELSE dispositivo END AS device_type,
        fuente AS traffic_source,
        CAST(conversion AS INTEGER) AS is_converted
    FROM raw_data
    -- Filtros de Data Quality
    WHERE variante IN ('A', 'B')                        -- Elimina variantes inválidas
      AND CAST(timestamp AS TIMESTAMP) >= '2020-01-01'  -- Elimina fechas absurdas
      AND CAST(timestamp AS TIMESTAMP) <= '2030-01-01'
),
-- Deduplicación con función de ventana (estándar de la industria)
, deduplicated AS (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY lead_id ORDER BY event_timestamp DESC) AS rn
    FROM cleaned
)
SELECT lead_id, event_timestamp, test_variant, device_type, traffic_source, is_converted
FROM deduplicated
WHERE rn = 1  -- Conserva solo el registro más reciente por usuario
```

**¿Por qué `ROW_NUMBER()` y no `SELECT DISTINCT`?**
`DISTINCT` elimina filas solo si todos los campos son idénticos. En nuestro dataset, los duplicados tienen timestamps distintos (el bug del tracker disparó el evento en dos momentos). `ROW_NUMBER()` permite seleccionar lógicamente el más reciente, que es la lógica de negocio correcta.

**`models/marts/fct_ab_test_metrics.sql`** — Capa de métricas:

```sql
WITH leads AS (
    SELECT * FROM {{ ref('stg_leads') }}  -- ref() es la forma dbt de referenciar modelos
),
aggregated AS (
    SELECT
        test_variant,
        COUNT(DISTINCT lead_id)           AS total_users,
        SUM(is_converted)                 AS total_conversions,
        ROUND(AVG(is_converted) * 100, 2) AS conversion_rate_pct
    FROM leads
    GROUP BY 1
)
SELECT * FROM aggregated ORDER BY test_variant
```

**`models/staging/schema.yml`** — Tests de calidad de datos:

```yaml
models:
  - name: stg_leads
    columns:
      - name: lead_id
        tests:
          - unique      # Detecta duplicados
          - not_null    # Detecta registros sin ID
      - name: test_variant
        tests:
          - accepted_values:
              values: ['A', 'B']  # Detecta variantes inválidas que pasaron el filtro
```


### PASO 6 — Ejecución del Pipeline dbt

```bash
# Desde la carpeta marketing_dbt/
C:\Users\yrami\AppData\Roaming\Python\Python313\Scripts\dbt.exe run --profiles-dir .
```

**Output exitoso:**
```
21:02:30  1 of 2 START sql view model main.stg_leads ............. [RUN]
21:02:31  1 of 2 OK created sql view model main.stg_leads ........ [OK in 0.92s]
21:02:31  2 of 2 START sql table model main.fct_ab_test_metrics .. [RUN]
21:02:32  2 of 2 OK created sql table model main.fct_ab_test_metrics [OK in 0.77s]
Done. PASS=2 WARN=0 ERROR=0 SKIP=0
```

```bash
C:\Users\yrami\AppData\Roaming\Python\Python313\Scripts\dbt.exe test --profiles-dir .
```

**Error detectado en la primera ejecución:**
```
FAIL 7 unique_stg_leads_lead_id
Got 7 results, configured to fail if != 0
```

**¿Qué significó este error?** dbt detectó exactamente los 7 duplicados con timestamps distintos que inyectamos. El `SELECT DISTINCT` inicial no los eliminó porque eran registros técnicamente distintos. Se aplicó la corrección con `ROW_NUMBER()`.

**Output exitoso tras el fix:**
```
PASS=5 WARN=0 ERROR=0 SKIP=0 — Completed successfully
```


### PASO 7 — Análisis en Jupyter Notebook

**Error encontrado:**
```
ModuleNotFoundError: No module named 'pandas'
```

**Causa:** VS Code seleccionó automáticamente un kernel de Python que no tenía las librerías instaladas.

**Solución aplicada:** Seleccionar manualmente el kernel de Python 3.13 desde la UI de VS Code (esquina superior derecha del notebook).

**Instalación de dependencias del análisis:**
```bash
pip install pandas numpy seaborn matplotlib scipy statsmodels
```

**Código del Z-Test en el notebook:**
```python
from statsmodels.stats.proportion import proportions_ztest

successes = [n_conversiones_B, n_conversiones_A]
nobs      = [n_usuarios_B, n_usuarios_A]
z_stat, p_value = proportions_ztest(successes, nobs=nobs, alternative='larger')

# Resultado:
# z_stat  = 3.4
# p_value = 0.0006
```


### PASO 8 — App Streamlit (Versión para Deploy)

**Instalación:**
```bash
pip install streamlit plotly duckdb
```

**Problema con el comando `streamlit run`:**
```
streamlit : El término 'streamlit' no se reconoce como nombre de un cmdlet
```

**Causa:** Streamlit se instaló en `C:\Users\yrami\AppData\Roaming\Python\Python313\Scripts\`, que no está en el PATH de Windows.

**Solución permanente:**
```bash
python -m streamlit run app.py
```

**El diseño del `app.py` para Streamlit Cloud:**
La app original leía del `.duckdb` generado por dbt. El problema: Streamlit Cloud no puede ejecutar `dbt run`. Solución: la app reemplaza el pipeline dbt con DuckDB puro en Python, usando `@st.cache_data` para que los datos no se regeneren en cada recarga:

```python
@st.cache_data
def build_clean_metrics():
    con = duckdb.connect()
    # Replica stg_leads.sql
    stg = con.execute("""
        WITH cleaned AS (...), deduped AS (...)
        SELECT ... FROM deduped WHERE rn = 1
    """).df()
    # Replica fct_ab_test_metrics.sql
    metrics = con.execute("SELECT ... FROM stg GROUP BY test_variant").df()
    return stg, metrics
```


### PASO 9 — Control de Versiones y Deploy

**Inicialización del repositorio:**
```bash
git init
git add .
git commit -m "feat: Marketing A/B Testing Pipeline — dbt + DuckDB + Streamlit"
git branch -M main
git remote add origin https://github.com/yjramirez-lab/Proyecto_Marketing_AB_Test.git
git push -u origin main
```

**¿Por qué `git branch -M main`?**
Git crea la rama inicial con el nombre `master`. GitHub usa `main` como convención moderna. Este comando la renombra antes del primer push para que sea compatible.

**Deploy en Streamlit Cloud:**
1. Ingresar a share.streamlit.io con cuenta de GitHub
2. New App → Seleccionar repositorio `Proyecto_Marketing_AB_Test`
3. Branch: `main` | Main file: `app.py`
4. Streamlit Cloud lee `requirements.txt` automáticamente e instala las dependencias
5. URL pública generada automáticamente

**Actualización de documentación tras el deploy:**
```bash
git add 01_Documentacion_Proyecto.md
git commit -m "docs: add comprehensive step-by-step study guide for NotebookLM"
git push
```

**`.gitignore` — Archivos excluidos del repositorio:**
```
*.duckdb          # Se genera corriendo dbt localmente
raw_leads.csv     # Se genera corriendo el script Python
marketing_dbt/target/     # Output de compilación de dbt
.ipynb_checkpoints/       # Checkpoints del Jupyter
02_Notion_Portfolio.md    # Solo para uso local / copy-paste en Notion
```


### Resumen de Todos los Comandos Ejecutados

```bash
# Generación de datos
python 00_generador_trafico.py

# Instalación de dependencias
pip install dbt-core dbt-duckdb
pip install pandas numpy seaborn matplotlib scipy statsmodels
pip install streamlit plotly duckdb

# Pipeline dbt (desde marketing_dbt/)
dbt run --profiles-dir .
dbt test --profiles-dir .

# App local
python -m streamlit run app.py

# Git y deploy
git init
git add .
git commit -m "feat: Marketing A/B Testing Pipeline — dbt + DuckDB + Streamlit"
git branch -M main
git remote add origin https://github.com/yjramirez-lab/Proyecto_Marketing_AB_Test.git
git push -u origin main
```

