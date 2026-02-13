import streamlit as st
import pandas as pd

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="El Hoyo 19", layout="wide", initial_sidebar_state="collapsed")

ID_PLANILLA = "1y3UgOy3gjJSJYM1GBmZYeATYhUZaz9Xv690CUX-m8Xw"
URL = f"https://docs.google.com/spreadsheets/d/{ID_PLANILLA}/export?format=csv&gid=0"

def load_data():
    try:
        return pd.read_csv(URL)
    except:
        return pd.DataFrame()

# --- LÓGICA DE POSICIONES TIPO GOLF ---
def obtener_ranking_formateado(df):
    if df.empty: return pd.DataFrame()
    
    # 1. Agrupar y calcular puntos
    df["Puntos_Stableford"] = pd.to_numeric(df["Puntos_Stableford"])
    resumen = []
    for jugador in df["Jugador"].unique():
        data_jugador = df[df["Jugador"] == jugador]
        scores = sorted(data_jugador["Puntos_Stableford"].tolist(), reverse=True)
        total_8 = sum(scores[:8])
        # Intentar obtener foto y país si existen en las columnas, sino poner default
        foto = data_jugador["Foto"].iloc[0] if "Foto" in df.columns else "https://www.w3schools.com/howto/img_avatar.png"
        bandera = data_jugador["Pais"].iloc[0] if "Pais" in df.columns else "https://cdn-icons-png.flaticon.com/512/921/921443.png"
        
        resumen.append({
            "Foto": foto,
            "Pais": bandera,
            "Jugador": jugador,
            "Puntos": total_8,
            "Fechas": len(scores)
        })
    
    rank_df = pd.DataFrame(resumen).sort_values(by="Puntos", ascending=False).reset_index(drop=True)
    
    # 2. Calcular Posiciones con "T" para empates
    posiciones = []
    puntos_lista = rank_df["Puntos"].tolist()
    
    for i, pts in enumerate(puntos_lista):
        count = puntos_lista.count(pts)
        real_pos = i + 1
        if count > 1:
            # Buscar la posición del primero que tiene este mismo puntaje
            primera_aparicion = puntos_lista.index(pts) + 1
            posiciones.append(f"T{primera_aparicion}")
        else:
            posiciones.append(str(real_pos))
            
    rank_df.insert(0, "Pos", posiciones)
    return rank_df

# --- INTERFAZ ---
st.image("https://images.unsplash.com/photo-1535131749006-b7f58c99034b?q=80&w=2070&auto=format&fit=crop", use_container_width=True)

# Menú de navegación (Session State)
if 'menu' not in st.session_state: st.session_state.menu = "🏆 Ranking"
c1, c2, c3 = st.columns(3)
with c1: 
    if st.button("🏆 Ranking"): st.session_state.menu = "🏆 Ranking"
with c2: 
    if st.button("📅 Fechas"): st.session_state.menu = "📅 Fechas"
with c3: 
    if st.button("📜 Reglas"): st.session_state.menu = "📜 Reglas"

st.markdown("---")

df_actual = load_data()

if st.session_state.menu == "🏆 Ranking":
    st.subheader("Leaderboard Oficial")
    ranking = obtener_ranking_formateado(df_actual)
    
    if not ranking.empty:
        # Configuración de columnas para mostrar imágenes
        st.column_config = {
            "Foto": st.column_config.ImageColumn(" ", help="Avatar"),
            "Pais": st.column_config.ImageColumn(" ", help="País"),
            "Puntos": st.column_config.NumberColumn("PTS", format="%d ⛳"),
        }
        
        # Mostramos la tabla con el nuevo formato de imágenes
        st.data_editor(
            ranking,
            column_config=st.column_config,
            hide_index=True,
            use_container_width=True,
            disabled=True # Para que no sea editable
        )
    else:
        st.info("Sincronizando con Google Sheets...")

# (Mantener las secciones de Fechas y Reglas igual que antes)
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
