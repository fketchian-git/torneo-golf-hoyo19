import streamlit as st
import pandas as pd

# --- CONFIGURACIÓN DE LA HOJA DE GOOGLE ---
# Reemplaza con tu ID real de Google Sheets
SHEET_ID = "https://docs.google.com/spreadsheets/d/1y3UgOy3gjJSJYM1GBmZYeATYhUZaz9Xv690CUX-m8Xw/edit?usp=sharing"
SHEET_NAME = "scores"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"

st.set_page_config(page_title="El Hoyo 19", layout="wide")

# --- CARGA DE DATOS ---
def load_data():
    try:
        # Cargamos los datos directamente desde la URL de Google Sheets
        return pd.read_csv(URL)
    except:
        return pd.DataFrame(columns=["Fecha", "Jugador", "Campo", "Puntos_Stableford"])

# --- LÓGICA DE RANKING ---
def calcular_ranking(df):
    if df.empty: return pd.DataFrame()
    
    # Asegurar que los puntos sean numéricos
    df["Puntos_Stableford"] = pd.to_numeric(df["Puntos_Stableford"])
    
    resumen = []
    for jugador in df["Jugador"].unique():
        scores_jugador = df[df["Jugador"] == jugador]["Puntos_Stableford"].tolist()
        jugadas = len(scores_jugador)
        # Regla: Mejores 8 tarjetas
        mejores_8 = sorted(scores_jugador, reverse=True)[:8]
        total = sum(mejores_8)
        resumen.append({
            "Jugador": jugador,
            "Puntos Totales (Top 8)": total,
            "Fechas Jugadas": jugadas,
            "Promedio": round(total / jugadas, 2)
        })
    
    return pd.DataFrame(resumen).sort_values(by="Puntos Totales (Top 8)", ascending=False)

# --- INTERFAZ ---
st.title("⛳ El Hoyo 19 - El Canton - Tour 2026")

menu = st.sidebar.radio("Navegación", ["Leaderboard", "Reglamento", "Cronograma"])
df_actual = load_data()

if menu == "Leaderboard":
    st.header("🏆 Tabla General")
    ranking = calcular_ranking(df_actual)
    if not ranking.empty:
        st.dataframe(ranking, use_container_width=True, hide_index=True)
    else:
        st.info("No hay datos registrados todavía.")

elif menu == "Reglamento":
    st.header("📜 Reglamento del Comité")
    st.markdown("""
    * **Modalidad:** Stableford Individual.
    * **Puntaje Neto:** Albatros (+5), Águila (+4), Birdie (+3), Par (+2), Bogey (+1).
    * **Handicap:** 85% en El Cantón, 100% fuera de casa.
    * **Clasificación:** Mínimo 8 tarjetas para el ranking general.
    * **Inscripción:** $70.000 (premios y asado).
    """)

elif menu == "Cronograma":
    st.header("📅 Calendario de Fechas")
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
        ["28/11", "El Cantón", "Final y Asado"]
    ]
    st.table(pd.DataFrame(fechas, columns=["Fecha", "Sede", "Tipo"]))

# --- NOTA PARA LA CARGA ---
st.sidebar.markdown("---")
st.sidebar.info("💡 Para cargar scores, el administrador debe completar la Google Sheet vinculada.")
