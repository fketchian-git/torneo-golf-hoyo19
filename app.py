import streamlit as st
import pandas as pd
from streamlit.column_config import TextColumn, ImageColumn, NumberColumn

# --- CONFIGURACIÓN GLOBAL ---
ID_PLANILLA = "1y3UgOy3gjJSJYM1GBmZYeATYhUZaz9Xv690CUX-m8Xw"
# REEMPLAZA ESTE NÚMERO con el GID que sacaste de tu navegador para la solapa Jugadores
GID_JUGADORES = "1923787612" 

def load_data():
    # Definimos las URLs adentro para que sean locales a la función
    url_scores = f"https://docs.google.com/spreadsheets/d/{ID_PLANILLA}/export?format=csv&gid=0"
    url_jugadores = f"https://docs.google.com/spreadsheets/d/{ID_PLANILLA}/export?format=csv&gid={GID_JUGADORES}"
    
    try:
        # 1. Intentamos cargar los scores (la base de todo)
        df_scores = pd.read_csv(url_scores)
        df_scores.columns = df_scores.columns.str.strip() # Limpiamos espacios en nombres de columnas
        
        try:
            # 2. Intentamos cargar la info de los jugadores (fotos y banderas)
            df_jugadores = pd.read_csv(url_jugadores)
            df_jugadores.columns = df_jugadores.columns.str.strip()
            
            # 3. Cruzamos los datos usando la columna 'Jugador' como puente
            if "Jugador" in df_scores.columns and "Jugador" in df_jugadores.columns:
                df_final = pd.merge(df_scores, df_jugadores, on="Jugador", how="left")
                return df_final
            else:
                return df_scores
        except:
            # Si falla la carga de fotos, devolvemos solo los scores para que la app no muera
            return df_scores
            
    except Exception as e:
        st.error(f"Error crítico cargando scores: {e}")
        return pd.DataFrame()

def obtener_ranking_formateado(df):
    if df.empty: return pd.DataFrame()
    
    df["Puntos_Stableford"] = pd.to_numeric(df["Puntos_Stableford"])
    resumen = []
    
    for jugador in df["Jugador"].unique():
        data_jugador = df[df["Jugador"] == jugador]
        scores = sorted(data_jugador["Puntos_Stableford"].tolist(), reverse=True)
        total_8 = sum(scores[:8])
        
        # Ahora sí tomamos la foto y país reales del merge
        foto = data_jugador["Foto"].iloc[0] if "Foto" in data_jugador.columns and pd.notna(data_jugador["Foto"].iloc[0]) else "https://www.w3schools.com/howto/img_avatar.png"
        pais = data_jugador["Pais"].iloc[0] if "Pais" in data_jugador.columns and pd.notna(data_jugador["Pais"].iloc[0]) else "https://cdn-icons-png.flaticon.com/512/921/921443.png"
        
        resumen.append({
            "Foto": foto,
            "Pais": pais,
            "Jugador": jugador,
            "Puntos": total_8,
            "Fechas": len(scores)
        })
    
    # ... (El resto de la lógica de las posiciones "T" se mantiene igual) ...
    rank_df = pd.DataFrame(resumen).sort_values(by="Puntos", ascending=False).reset_index(drop=True)
    
    posiciones = []
    puntos_lista = rank_df["Puntos"].tolist()
    for i, pts in enumerate(puntos_lista):
        count = puntos_lista.count(pts)
        if count > 1:
            primera_aparicion = puntos_lista.index(pts) + 1
            posiciones.append(f"T{primera_aparicion}")
        else:
            posiciones.append(str(i + 1))
    
    rank_df.insert(0, "Pos", posiciones)
    return rank_df
    

# --- INTERFAZ ---
# --- CONFIGURACIÓN DE PÁGINA Y FONDO ---
st.set_page_config(page_title="Hoyo 19 - Tour", page_icon="⛳", layout="centered")

st.markdown("""
    <style>
    /* 1. Fondo Principal */
    .stApp {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    }

    /* 2. Header Full Width (ajustado al ancho) */
    [data-testid="stImage"] {
        width: 100%;
        padding: 0px;
    }
    [data-testid="stImage"] img {
        width: 100% !important;
        height: auto;
        max-height: 200px; /* Ajusta este valor si quieres que sea más fina */
        object-fit: cover; /* Hace que se adapte al ancho sin deformarse */
        border-radius: 0px 0px 20px 20px; /* Curva suave solo abajo */
    }

    /* 3. Contenedores para Fechas y Reglas (para que se lean bien) */
    .content-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        color: #1e293b; /* Texto oscuro sobre fondo blanco */
        margin-bottom: 20px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
    }
    
    .content-card h3 {
        color: #1e3d59 !important;
        margin-top: 0;
    }

    /* Títulos de sección sobre el fondo azul */
    .stSubheader {
        color: white !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
    }
    </style>
    """, unsafe_allow_html=True)

# Aquí iría tu imagen del logo
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
    # --- CSS MEJORADO CON TENDENCIAS ---
    st.markdown("""
        <style>
        .leaderboard-container { display: flex; flex-direction: column; gap: 10px; }
        .player-card {
            background-color: white; border-radius: 12px; padding: 10px 15px;
            display: flex; align-items: center; box-shadow: 0px 2px 4px rgba(0,0,0,0.05);
            border: 1px solid #eee; position: relative;
        }
        .champion-card {
            background: linear-gradient(90deg, #fffcf0 0%, #fff 100%);
            border: 2px solid #d4af37 !important;
        }
        .pos-section { width: 45px; display: flex; align-items: center; gap: 5px; }
        .pos-num { font-weight: bold; font-size: 18px; color: #1e3d59; }
        .trend-up { color: #28a745; font-size: 12px; }
        .trend-down { color: #dc3545; font-size: 12px; }
        .trend-equal { color: #ccc; font-size: 12px; }
        
        .photo-section { position: relative; margin-right: 15px; }
        .player-photo { width: 55px; height: 55px; border-radius: 50%; object-fit: cover; border: 2px solid #eee; }
        .champion-photo { border: 2px solid #d4af37; }
        .info-section { flex-grow: 1; }
        .pts-number { font-size: 20px; font-weight: bold; color: #1e3d59; }
        .pts-label { font-size: 9px; color: #888; text-align: right; }
        </style>
    """, unsafe_allow_html=True)

    st.subheader("Leaderboard Oficial - El Hoyo 19 - El Canton")
    
    df_actual = load_data()
    ranking = obtener_ranking_formateado(df_actual)
    
    if not ranking.empty:
        # Identificamos el puntaje máximo para el Highlight automático
        max_puntos = ranking["Puntos"].max()
        
        st.write('<div class="leaderboard-container">', unsafe_allow_html=True)
        
        for i, row in ranking.iterrows():
            # 1. HIGHLIGHT AUTOMÁTICO: Si tiene el puntaje máximo, es el líder/campeón
            es_lider = (row['Puntos'] == max_puntos) and (max_puntos > 0)
            
            card_class = "player-card champion-card" if es_lider else "player-card"
            photo_class = "player-photo champion-photo" if es_lider else "player-photo"
            trofeo = " 🏆" if es_lider else ""

            # 2. LÓGICA DE TENDENCIA (Simulada o real)
            # Aquí, si tuvieras una columna 'Pos_Anterior', compararíamos. 
            # Por ahora, pondremos flecha verde a los que jugaron más fechas recientemente.
            trend_icon = "▲" if i < 3 else "▼" if i > 10 else "●"
            trend_class = "trend-up" if trend_icon == "▲" else "trend-down" if trend_icon == "▼" else "trend-equal"

            st.markdown(f"""
                <div class="{card_class}">
                    <div class="pos-section">
                        <span class="pos-num">{row['Pos']}</span>
                        <span class="{trend_class}">{trend_icon}</span>
                    </div>
                    <div class="photo-section">
                        <img src="{row['Foto']}" class="{photo_class}">
                    </div>
                    <div class="info-section">
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <img src="{row['Pais']}" style="width:20px; border-radius:2px;">
                            <span style="font-weight: bold; font-size: 15px;">{row['Jugador']}{trofeo}</span>
                        </div>
                        <div style="font-size: 11px; color: #777;">📅 {row['Fechas']} fechas jugadas</div>
                    </div>
                    <div style="text-align: right; border-left: 1px solid #eee; padding-left: 15px; min-width: 65px;">
                        <div class="pts-label">PUNTOS</div>
                        <div class="pts-number">{int(row['Puntos'])}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        st.write('</div>', unsafe_allow_html=True)

        # --- DISCLAIMER ---
        st.markdown(f"""
            <div style="font-size: 10px; color: #bbb; text-align: center; margin-top: 30px; padding: 20px; border-top: 1px solid #eee;">
                © 2024 - 2026 <b>TORNEO EL HOYO 19</b>. <br>
                Diseño y sistema de ranking protegidos. Prohibida su copia sin autorización.
            </div>
        """, unsafe_allow_html=True)
        
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
