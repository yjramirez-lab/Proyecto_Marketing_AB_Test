# 📊 Marketing A/B Testing Pipeline — Notion Portfolio Document

## 🎯 Cuadro de Mando del Proyecto

| Propiedad | Detalle |
|---|---|
| **Estado** | ✅ Completado |
| **Tipo** | Data Engineering + Product Analytics |
| **Rol demostrado** | Analytics Engineer / Product Analyst |
| **Dificultad** | ⭐⭐⭐⭐ Avanzado |
| **Demo en vivo** | [Link a Streamlit App] |
| **Repositorio** | [Link a GitHub] |
| **Herramientas** | Python · dbt · DuckDB · Streamlit · Pandas · SciPy |
| **Industria** | Marketing Digital / Growth / E-commerce |

---

## 🧠 El Problema de Negocio

> *"La Variante B tuvo más ventas este mes, ¿la desplegamos a todos los usuarios?"*

Esta es la pregunta que cualquier PM o Director de Marketing te va a hacer. El trabajo del analista **no** es decir "sí porque el número es mayor". El trabajo es responder:

**¿La diferencia es estadísticamente significativa, o fue el azar?**

Enviamos dos versiones de una campaña:
- **Variante A (Control):** Diseño y CTA tradicional.
- **Variante B (Tratamiento):** CTA nuevo con mensaje de urgencia.

---

## 🏗 Arquitectura Técnica (Modern Data Stack Local)

```
raw_leads.csv (Python Script)
       │
       ▼
[dbt-DuckDB: Staging Layer]  ← stg_leads.sql (Limpieza + Deduplicación)
       │
       ▼
[dbt-DuckDB: Marts Layer]    ← fct_ab_test_metrics.sql (Agregación)
       │
       ▼
[Streamlit App / Jupyter Notebook] ← Z-Test + Visualización
```

### ¿Por qué esta pila tecnológica?

| Herramienta | Rol en el Proyecto | Por Qué se Eligió |
|---|---|---|
| **Python (random)** | Generador de datos sintéticos | Simula un tracker de eventos real con ruido deliberado |
| **dbt-core** | Capa de transformación SQL | Estándar de la industria en Analytics Engineering |
| **DuckDB** | Base de datos analítica local | OLAP en un solo archivo, sin servidores ni costos |
| **Streamlit** | Dashboard interactivo | Demuestra la capacidad de comunicar hallazgos a no-técnicos |
| **SciPy / StatsModels** | Inferencia estadística | Z-Test de proporciones para validar hipótesis de negocio |
| **Pandas + Seaborn** | EDA en Jupyter Notebook | Pipeline de análisis reproducible y documentado |

---

## 🗄 Diseño de Datos

### Fuente: `raw_leads.csv` (Datos Sintéticos Intencionalmente "Sucios")

| Columna | Tipo | Descripción | Ruido Inyectado |
|---|---|---|---|
| `lead_id` | STRING | ID único del usuario | Duplicados deliberados (tracking bugs) |
| `timestamp` | DATETIME | Hora del evento | Fechas imposibles (1999, 2050) |
| `variante` | STRING | Grupo A o B | Variantes inválidas ('C', 'test') |
| `dispositivo` | STRING | Mobile / Desktop | Nulos (~5% del dataset) |
| `fuente` | STRING | Email / Social / Paid | — |
| `conversion` | INT (0/1) | Si compró o no | — |

### Modelos dbt

**`models/staging/stg_leads.sql`** — *Vista (View)*
- Lee el CSV directamente con `read_csv_auto()`
- Filtra variantes inválidas (`WHERE variante IN ('A','B')`)
- Elimina fechas absurdas
- Deduplica con `ROW_NUMBER() OVER (PARTITION BY lead_id)`

**`models/marts/fct_ab_test_metrics.sql`** — *Tabla*
- Agrupa por variante
- Calcula `total_users`, `total_conversions`, `conversion_rate_pct`

---

## 📐 Metodología Estadística

**Test:** Z-Test para Proporciones de Dos Colas (one-sided, `alternative='larger'`)
**Nivel de Significancia (α):** 0.05
**Hipótesis Nula (H₀):** La Variante B NO tiene una tasa de conversión mayor que la A.
**Hipótesis Alternativa (H₁):** La Variante B SÍ tiene una tasa de conversión mayor que la A.

### Resultados Obtenidos

| Métrica | Variante A | Variante B |
|---|---|---|
| **Usuarios** | ~2,400 | ~2,400 |
| **Conversiones** | ~200 | ~270 |
| **Tasa de Conversión** | **~8.25%** | **~11.15%** |
| **p-value** | — | **0.0006** |

✅ **Decisión:** Rechazamos H₀. La subida de +2.9pp es estadísticamente significativa. **El nuevo CTA funciona y se debe desplegar a producción.**

---

## 📁 Estructura del Repositorio

```
Proyecto_Marketing_AB_Test/
├── app.py                          # 🚀 Dashboard interactivo Streamlit
├── AB_Testing_Report.ipynb         # 📓 Análisis completo con EDA y Z-Test
├── 00_generador_trafico.py         # ⚙️  Generador de datos sintéticos
├── raw_leads.csv                   # 📦 Dataset crudo (con ruido)
├── requirements.txt                # 📋 Dependencias del proyecto
├── 01_Documentacion_Proyecto.md    # 📚 Guía técnica completa (para NotebookLM)
└── marketing_dbt/                  # 🗄  Proyecto dbt
    ├── dbt_project.yml
    ├── profiles.yml
    ├── marketing.duckdb             # Base de datos generada por dbt run
    └── models/
        ├── staging/
        │   ├── stg_leads.sql
        │   └── schema.yml
        └── marts/
            └── fct_ab_test_metrics.sql
```

---

## ▶️ Cómo Ejecutar el Proyecto

```bash
# 1. Clonar e instalar dependencias
pip install -r requirements.txt

# 2. Generar los datos crudos
python 00_generador_trafico.py

# 3. Correr el pipeline de Data Warehouse con dbt
cd marketing_dbt
dbt run --profiles-dir .
dbt test --profiles-dir .
cd ..

# 4. Lanzar el dashboard interactivo
python -m streamlit run app.py

# 5. Abrir el notebook de análisis en VS Code o Jupyter Lab
# Abrir: AB_Testing_Report.ipynb
```

---

## 🔍 Key Takeaways y Aprendizajes

- **Analytics Engineering:** dbt no es solo SQL; es el sistema de control de calidad y documentación de transformaciones en un equipo de datos.
- **DuckDB como Data Warehouse local:** Permite iterar rapidísimo en análisis OLAP sin servidores. Perfecto para portafolios, MVPs y análisis ad-hoc.
- **Datos "sucios" intencionales:** El verdadero skill de un analista se mide en cómo trabaja con datos imperfectos, no con datasets de Kaggle ya limpios.
- **Comunicación con Streamlit:** El 90% del valor de un análisis se pierde si no se comunica bien. Una app interactiva es un "traductor" para el negocio.

---

## 🗣 Cómo Presentar este Proyecto en Entrevistas

**Pregunta:** *"Cuéntame de un proyecto de analytics que hayas hecho."*

**Respuesta:**
*"Construí un pipeline completo de A/B Testing para analizar si un rediseño de CTA en una campaña de marketing generaba conversiones reales o era ruido aleatorio. Usé dbt con DuckDB como capa de Data Warehouse para limpiar y estructurar los datos con SQL, detecté y eliminé duplicados usando funciones de ventana analíticas, y validé estadísticamente la hipótesis con un Z-Test de proporciones. El p-value resultó de 0.0006, lo que confirmó que el nuevo diseño generaba un lift real de ~2.9 puntos porcentuales. Presenté los resultados en una app de Streamlit para que el equipo de marketing pudiera consultar los resultados sin necesidad de conocimientos técnicos."*
