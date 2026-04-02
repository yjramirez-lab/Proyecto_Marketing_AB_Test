# Guía de Estudio y Arquitectura: Proyecto Marketing A/B Testing & Data Engineering

Esta es tu bitácora de aprendizaje profundo. Está diseñada específicamente para ser ingerida por **NotebookLM**, sirviendo como base de conocimiento para tu preparación de entrevistas y como pilar de tu portafolio personal.

> **Filosofía del Proyecto: El Analista como Socio Estratégico**
> *El mercado no premia saber hacer gráficos o consultas SQL complejas; premia la capacidad de actuar como un traductor entre los datos y la estrategia, reduciendo la incertidumbre.*
> Este proyecto está diseñado bajo la mentalidad del **Top 1% de Analistas**:
> - **El Jefe Supremo:** El cliente. Comprobamos si el nuevo diseño le sirve al usuario final.
> - **Manejo de la Ambigüedad:** Partimos de una pregunta vaga (*"¿Sirve el nuevo botón?"*) y construimos un sistema riguroso para responderla.
> - **Enfoque en el Impacto:** El objetivo no es codificar en Python, es descubrir si el rediseño es lo bastante rentable como para enviarlo a producción.

---

## 1. El 'Por Qué' de este Proyecto (Contexto de Negocio)
En el rol de **Product Analyst** o **Growth Data Analyst**, no basta con mostrar qué pasó (Reporte Descriptivo). Tienes que demostrar matemáticamente *por qué* pasó y *si va a volver a pasar* (Inferencia Predictiva). 

**El Escenario:**
El equipo de Marketing cambió el diseño de un botón (CTA) y añadió un "mensaje de urgencia" (Variante B) frente al diseño habitual (Variante A). Enviaron tráfico a ambos diseños. Algunos usuarios compraron (conversión = 1), otros no (conversión = 0).

**La Misión del Analista:**
El mánager pregunta: *"La Variante B tuvo más ventas, ¿desplegamos el diseño B a todos los usuarios?"*.
Tu respuesta como analista profesional no puede ser "Sí, porque el número es mayor". Debe ser: *"Necesitamos verificar si la subida es estadísticamente significativa y no un simple golpe de suerte o ruido aleatorio"*.

---

## 2. Arquitectura y "El Por Qué" de cada Herramienta

La arquitectura elegida emula un flujo corporativo real *Modern Data Stack*, ejecutado localmente. 

### A. Python (Generación Sintética)
* **Archivo:** `00_generador_trafico.py`
* **Por qué:** En la vida real conectas una base de datos. Para este portafolio, construimos un generador sintético parametrizado con la librería `random`.
* **El "Truco" Educativo:** Inyectamos ruido deliberado (dispositivos nulos `NaN`, leads duplicados por fallos en el tracker de eventos, variantes inválidas y fechas locas como el año 1999 o 2050). Esto fuerza la necesidad de tener una capa sólida de Ingeniería de Datos antes de analizar.

### B. dbt-duckdb (La Capa de Transformación / Data Warehouse)
* **Por qué DuckDB:** En vez de levantar un pesado Postgres o Snowflake que cuesta dinero, usamos DuckDB. Es una base de datos OLAP que corre en un solo archivo local (`marketing.duckdb`). Es rapidísima y perfecta para Analítica.
* **Por qué dbt (Data Build Tool):** Podríamos limpiar usando pandas, pero los equipos maduros usan herramientas de *Analytics Engineering* como dbt. Escribimos SQL declarativo que hace las transformaciones, y dbt se encarga de crear las tablas por debajo.
* **El código clave de limpieza (Staging):**
  Usamos `row_number() over (partition by lead_id order by event_timestamp desc)` para dededuplicar los ids. En pandas sería un simple `drop_duplicates`, pero en bases de datos analíticas masivas (SQL), la función de ventana `row_number()` es el estándar de oro de la industria.

### C. Jupyter Notebook (.ipynb) + SciPy (El Análisis Exploratorio e Inferencia)
* **Por qué:** Jupyter narra la historia del análisis combinando razonamientos (Markdown), visualizaciones (Seaborn) y cálculos complejos.
* **El "Z-Test para Proporciones":** Como analizamos la "proporción de gente que compró" (tasas de conversión), usamos esta prueba matemática. SciPy y StatsModels calculan el `p-value`. Si `p-value < 0.05` (nuestro alfa de riesgo), asumimos que el rediseño sí impactó en el comportamiento humano y rechazamos que fue simplemente casualidad.

### D. Streamlit (La Aplicación de Presentación para el Portafolio)
* **Por qué:** Los reclutadores raramente leen el código fuente o SQL bruto. Quieren ver un producto final. Streamlit levanta una app web interactiva construida 100% en Python, leyendo del DuckDB limpio y renderizando las gráficas.

---

## 3. Guía Paso a Paso (Procedimiento y Comandos)

Aquí está la crónica de los comandos que ejecuté en la terminal para que este proyecto cobrara vida.

### Paso 1: Configurar el Entorno y crear los Datos Base
```bash
# 1. Crear script de generación
# 2. Ejecutarlo para generar raw_leads.csv
python 00_generador_trafico.py
```
> **Lección aprendida:** Siempre que veas datos listos en Kaggle, desconfía. Los verdaderos ingenieros de datos pasan el 80% del tiempo limpiando datos sucios. Nosotros creamos nuestra propia basura para demostrar que la sabemos limpiar.

### Paso 2: Análisis Estadístico Inicial en Exploratorio
> Creamos el archivo Jupyter y nos topamos con un error clásico en VS Code:
* **Error:** `ModuleNotFoundError: No module named 'pandas'`
* **Causa:** VS Code seleccionó un "kernel" (un ejecutable de Python 3.11 aislado) que no compartía librerías con el sistema (Python 3.13).
* **Soluciones Posibles:**
  1. Usar las "magic commands": `%pip install pandas ...` en la primera celda del Notebook, forzando la instalación en ese preciso entorno.
  2. Ajustar manualmente la configuración del Kernel en VS Code seleccionando el entorno global. Optamos por la segunda para estandarizar.

### Paso 3: Data Build Tool (dbt)
```bash
# Instalar el core y el adaptador específico para DuckDB
pip install dbt-core dbt-duckdb
```
En lugar del tedioso comando `dbt init`, creé a mano la jerarquía corporativa limpia (`marketing_dbt`, `models`, `models/staging`, `models/marts`, `dbt_project.yml`, `profiles.yml`). Esto demuestra que entiendes las entrañas estructurales.

```bash
# Estando dentro de la carpeta /marketing_dbt
dbt run --profiles-dir .
dbt test --profiles-dir .
```

* **El Error Pedagógico del `dbt test`:**
  * Configuramos que la columna `lead_id` fuera `unique` y `not_null` en el archivo `schema.yml`.
  * ¡El `dbt test` falló descubriendo 7 duplicados!
  * **Causa & Solución:** Esto ocurrió porque el ruido se inyectó de forma "desigual" a los duplicados en Python. Arreglamos el modelo `stg_leads.sql` para usar `row_number()` forzando la extracción de un solo registro por persona.

### Paso 4: Streamlit Web App (El Front-End)
Se creó un dashboard (`app.py`) con comandos como `pip install streamlit plotly`. 
```bash
streamlit run app.py
```
La aplicación extrae el resumen directly desde la base `marketing.duckdb` y orquesta la calculadora de Z-Test dinámicamente.

---

## 4. Preguntas de Entrevista basadas en este Proyecto

Cuando expliques este proyecto, te pueden preguntar:

**Q: ¿Por qué usaste DuckDB y no conectaste un Postgres normal?**
"Porque el volumen de datos cabía cómodamente en memoria local y quería minimizar la fricción de DevOps mientras demostraba la capacidad de construir ETLs con SQL usando un adaptador in-process."

**Q: En dbt, ¿cómo solucionaste el problema persistente de duplicados?**
"Cuando `dbt test` saltó la alarma por una violación de la constraint de unicidad, el simple `SELECT DISTINCT` no sirvió porque algunas copias del registro tenían timestamps distintos a causa de ruido del tracker. Apliqué una función de agregación analítica de SQL (`row_number() over(partition by id order by timestamp desc)`) para seleccionar exhaustivamente el evento más reciente."

**Q: Cuéntame del concepto detrás de tu P-Value en el Notebook.**
"Mi P-value fue 0.0006. Establecí un nivel de significancia de alfa 0.05, indicando que solo toleraba un 5% de probabilidad de afirmar una falacia de Falso Positivo. Como el P-value era menor a alfa, rechacé la Hipótesis Nula: la subida de 8.25% a 11.15% en el diseño con urgencia en el CTA tenía suficiente relevancia para desplegarse globalmente en producción."
