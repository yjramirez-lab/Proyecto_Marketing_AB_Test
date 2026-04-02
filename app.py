import streamlit as st
import duckdb
import pandas as pd
import numpy as np
import plotly.express as px
import statsmodels.stats.api as sms
import random
from datetime import datetime, timedelta

# ──────────────────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────────────────
st.set_page_config(page_title="Marketing A/B Testing", layout="wide", page_icon="📈")

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

# ──────────────────────────────────────────────────────────
# DATA GENERATION (Self-contained — no dbt or CSV needed)
# Replicates the full pipeline inline so Streamlit Cloud works
# ──────────────────────────────────────────────────────────
@st.cache_data
def build_clean_metrics():
    """
    Genera datos sintéticos, inyecta ruido, los limpia con DuckDB 
    y calcula las métricas de A/B Test — todo en memoria.
    Esto replica lo que dbt hace localmente, pero sin infraestructura.
    """
    N = 5000
    devices = ["mobile", "desktop", "tablet"]
    sources = ["email", "social_media", "paid_ads", "organic"]
    
    start_date = datetime(2024, 1, 1)
    
    rows = []
    for i in range(N):
        lead_id = f"LEAD-{i+1:05d}"
        variant = "A" if random.random() < 0.5 else "B"
        # B convierte más (lift real)
        base_rate = 0.08 if variant == "A" else 0.12
        conversion = 1 if random.random() < base_rate else 0
        ts = start_date + timedelta(days=random.randint(0, 180),
                                     hours=random.randint(0, 23))
        device = random.choice(devices) if random.random() > 0.05 else None
        source = random.choice(sources)
        rows.append([lead_id, ts, variant, device, source, conversion])
    
    # ── Ruido intencional (para que el pipeline haga su trabajo) ──
    # 1. Duplicados (~7 registros)
    for i in range(7):
        rows.append(rows[random.randint(0, N - 1)])
    # 2. Variantes inválidas
    for i in range(15):
        rows[random.randint(0, N - 1)][2] = random.choice(["C", "test", "X"])
    # 3. Fechas absurdas
    for i in range(10):
        rows[random.randint(0, N - 1)][1] = datetime(1999, 1, 1)

    df_raw = pd.DataFrame(rows, columns=["lead_id", "timestamp", "variante",
                                          "dispositivo", "fuente", "conversion"])

    # ── Limpieza equivalente a stg_leads.sql en dbt ──────────────────
    con = duckdb.connect()
    con.register("raw_leads", df_raw)

    stg = con.execute("""
        WITH cleaned AS (
            SELECT
                lead_id,
                CAST(timestamp AS TIMESTAMP) AS event_timestamp,
                variante AS test_variant,
                CASE WHEN dispositivo IS NULL OR dispositivo = '' 
                     THEN 'unknown' ELSE dispositivo END AS device_type,
                fuente AS traffic_source,
                CAST(conversion AS INTEGER) AS is_converted
            FROM raw_leads
            WHERE variante IN ('A', 'B')
              AND CAST(timestamp AS TIMESTAMP) >= '2020-01-01'
              AND CAST(timestamp AS TIMESTAMP) <= '2030-01-01'
        ),
        deduped AS (
            SELECT *,
                   ROW_NUMBER() OVER (PARTITION BY lead_id ORDER BY event_timestamp DESC) AS rn
            FROM cleaned
        )
        SELECT lead_id, event_timestamp, test_variant, device_type,
               traffic_source, is_converted
        FROM deduped
        WHERE rn = 1
    """).df()

    # ── Agregación equivalente a fct_ab_test_metrics.sql en dbt ─────
    metrics = con.execute("""
        SELECT
            test_variant,
            COUNT(DISTINCT lead_id)    AS total_users,
            SUM(is_converted)          AS total_conversions,
            ROUND(AVG(is_converted) * 100, 2) AS conversion_rate_pct
        FROM stg
        GROUP BY test_variant
        ORDER BY test_variant
    """).df()

    con.close()
    return stg, metrics


# ──────────────────────────────────────────────────────────
# LAYOUT
# ──────────────────────────────────────────────────────────
st.title("🎯 Product Analytics: A/B Testing Dashboard")
st.caption("Pipeline: Python (Synthetic Data) → DuckDB Transform (Staging + Marts) → Z-Test Inferential Statistics")
st.markdown("---")

with st.spinner("Ejecutando pipeline de datos..."):
    stg_df, metrics_df = build_clean_metrics()

# ── 1. Raw metrics ────────────────────────────────────────
st.subheader("1. Métricas Agregadas (Data Warehouse en DuckDB)")
st.dataframe(metrics_df.rename(columns={
    "test_variant": "Variante",
    "total_users": "Usuarios",
    "total_conversions": "Conversiones",
    "conversion_rate_pct": "Tasa de Conversión (%)"
}), use_container_width=True, hide_index=True)

# ── 2. KPIs ──────────────────────────────────────────────
a = metrics_df[metrics_df["test_variant"] == "A"].iloc[0]
b = metrics_df[metrics_df["test_variant"] == "B"].iloc[0]
lift = b["conversion_rate_pct"] - a["conversion_rate_pct"]

st.markdown("### 2. Resumen de Desempeño")
col1, col2, col3 = st.columns(3)
col1.metric("Conversion Rate (A – Control)", f"{a['conversion_rate_pct']:.2f}%")
col2.metric("Conversion Rate (B – Tratamiento)", f"{b['conversion_rate_pct']:.2f}%",
            delta=f"{lift:+.2f}% (Lift)")
col3.metric("Audiencia Total", f"{int(a['total_users'] + b['total_users']):,}")

# ── 3. Bar chart ─────────────────────────────────────────
fig = px.bar(
    metrics_df, x="test_variant", y="conversion_rate_pct", color="test_variant",
    text="conversion_rate_pct",
    title="Comparación de Conversion Rate (%)",
    color_discrete_map={"A": "#1f77b4", "B": "#2ca02c"},
    labels={"test_variant": "Variante", "conversion_rate_pct": "Tasa de Conversión (%)"}
)
fig.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
fig.update_layout(showlegend=False, yaxis_range=[0, 15])
st.plotly_chart(fig, use_container_width=True)

# ── 4. Device breakdown ───────────────────────────────────
st.markdown("### 3. Distribución por Dispositivo y Variante")
device_df = stg_df.groupby(["test_variant", "device_type"])["is_converted"] \
                  .mean().reset_index()
device_df.columns = ["Variante", "Dispositivo", "Tasa de Conversión"]
fig2 = px.bar(device_df, x="Dispositivo", y="Tasa de Conversión",
              color="Variante", barmode="group",
              color_discrete_map={"A": "#1f77b4", "B": "#2ca02c"})
st.plotly_chart(fig2, use_container_width=True)

# ── 5. Z-Test ─────────────────────────────────────────────
st.markdown("---")
st.subheader("🧪 4. Prueba de Hipótesis (Z-Test de Proporciones)")

with st.expander("ℹ️ ¿Qué significa este test?"):
    st.markdown("""
    **H₀ (Nula):** La Variante B NO convierte más que la A. La diferencia es ruido aleatorio.  
    **H₁ (Alternativa):** La Variante B SÍ convierte más que la A.  
    **Nivel de significancia:** α = 0.05 (5% de tolerancia a falso positivo)  
    Si el **p-value < 0.05** → rechazamos H₀ → la subida es real → se puede desplegar en producción.
    """)

successes = [b["total_conversions"], a["total_conversions"]]
nobs      = [b["total_users"],       a["total_users"]]
z_stat, pval = sms.proportions_ztest(successes, nobs=nobs, alternative="larger")

col_a, col_b = st.columns(2)
col_a.metric("Estadístico Z", f"{z_stat:.4f}")
col_b.metric("P-Value", f"{pval:.6f}")

if pval < 0.05:
    st.success(
        f"✅ **Rechazamos H₀** (p = {pval:.4f} < 0.05)  \n"
        f"La Variante B genera un lift real de **+{lift:.2f}pp**. "
        f"El nuevo CTA con mensaje de urgencia funciona y se debe desplegar a producción."
    )
else:
    st.warning(
        f"⚠️ **No rechazamos H₀** (p = {pval:.4f} ≥ 0.05)  \n"
        f"La diferencia podría ser ruido. Se recomienda continuar el experimento."
    )

# ── 6. Footer ─────────────────────────────────────────────
st.markdown("---")
st.caption("Stack: Python · DuckDB · Streamlit · Plotly · SciPy/StatsModels | Portafolio: Data Analytics")
