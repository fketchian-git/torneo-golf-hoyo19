import streamlit as st
import pandas as pd

# Configuración para que se vea bien en celular
st.set_page_config(page_title="El Hoyo 19", layout="wide", initial_sidebar_state="collapsed")

# --- ESTILOS CSS PERSONALIZADOS ---
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #ffffff;
        color: #1e3d59;
        border: 1px solid #e0e0e0;
        font-weight: bold;
    }
    .stButton>button:hover {
        border: 1px solid #2e7d32;
        color: #2e7d32;
    }
    [data-testid="stMetricValue"] {
        font-size: 24px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER CON IMAGEN ---
# Usamos una imagen profesional de un hoyo icónico (Kapalua o similar)
st.image("https://images.unsplash.com/photo-1535131749006-b7f58c99034b?q=80&w=2070&auto=format&fit=crop", 
         caption="Tour El Hoyo 19 - 2026", use_container_width=True)

# --- CONFIGURACIÓN DE DATOS ---
ID_PLANILLA = "1y3UgOy3gjJSJYM1GBmZYeATYhUZaz9Xv690CUX-m8Xw"
URL = f"https://docs.google.com/spreadsheets/d/{ID_PLANILLA}/export?format=csv&gid=0"

def load_data():
    try:
        return pd.read_csv(URL)
    except:
        return pd.DataFrame()

def calcular_ranking(df):
    if df.empty: return pd.DataFrame()
    df["Puntos_Stableford"] = pd.to_numeric(df["Puntos_Stableford"])
    resumen = []
    for jugador in df["Jugador"].unique():
        scores = sorted(df[df["Jugador"] == jugador]["Puntos_Stableford"].tolist(), reverse=True)
        total_8 = sum(scores[:8])
        resumen.append({
            "Jugador": jugador,
            "Puntos (Top 8)": total_8,
            "Jugadas": len(scores)
        })
    return pd.DataFrame(resumen).sort_values(by="Puntos (Top 8)", ascending=False)

# --- MENÚ DE NAVEGACIÓN POR BOTONES (MÓVIL FRIENDLY) ---
# Creamos tres columnas para los botones del menú
col_nav1, col_nav2, col_nav3 = st.columns(3)

if 'menu' not in st.session_state:
    st.session_state.menu = "🏆 Ranking"

with col_nav1:
    if st.button("🏆 Ranking"):
        st.session_state.menu = "🏆 Ranking"
with col_nav2:
    if st.button("📅 Fechas"):
        st.session_state.menu = "📅 Fechas"
with col_nav3:
    if st.button("📜 Reglas"):
        st.session_state.menu = "📜 Reglas"

st.markdown("---")

# --- CONTENIDO SEGÚN SELECCIÓN ---
df_actual = load_data()

if st.session_state.menu == "🏆 Ranking":
    st.subheader("Leaderboard General")
    ranking = calcular_ranking(df_actual)
    if not ranking.empty:
        # Mostramos el podio destacado
        top_3 = ranking.head(3)
        cols = st.columns(3)
        for i, row in enumerate(top_3.itertuples()):
            cols[i].metric(f"{i+1}º {row.Jugador}", f"{row._2} pts")
        
        st.write("")
        st.dataframe(ranking, use_container_width=True, hide_index=True)
        st.caption("ℹ️ El ranking suma tus 8 mejores tarjetas del año.")
    else:
        st.info("Cargando datos...")

elif st.session_state.menu == "📅 Fechas":
    st.subheader("Cronograma 2026")
    fechas = [
        ["1/3", "Pilará Golf", "Afuera"],
        ["28/3", "El Cantón", "Local"],
        ["18/4", "A definir", "Afuera"],
        ["9/5", "El Cantón", "Local"],
        ["30/5", "A definir", "Afuera"],
        ["27/6", "El Cantón", "Local"],
        ["11/7", "A definir", "Afuera"],
        ["8/8", "El Cantón", "Local"],
        ["5/9", "A definir", "Afuera"],
        ["3/10", "El Cantón", "Local"],
        ["7/11", "A definir", "Afuera"],
        ["28/11", "El Cantón", "Final"]
    ]
    st.table(pd.DataFrame(fechas, columns=["Fecha", "Sede", "Tipo"]))

elif st.session_state.menu == "📜 Reglas":
    st.subheader("Reglamento Oficial")
    st.info("Inscripción: $70.000 (Premios y Asados)")
    st.markdown("""
    - **Modalidad:** Stableford.
    - **Hándicap:** 85% en El Cantón, 100% Fuera.
    - **Puntos:** Albatros 5, Águila 4, Birdie 3, Par 2, Bogey 1.
    - **Desempate:** 1º Fechas jugadas, 2º Mejores 4 fuera, 3º Mejores 4 dentro.
    """)
