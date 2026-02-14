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
    # --- CSS PARA EL DISEÑO DE TARJETAS (CARDS) ---
    st.markdown("""
        <style>
        .player-card {
            background-color: white;
            border-radius: 12px;
            padding: 12px;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0px 2px 5px rgba(0,0,0,0.1);
            border-left: 5px solid #1e3d59; /* Borde azul lateral */
        }
        .player-info {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .player-photo {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            object-fit: cover;
            border: 1px solid #ddd;
        }
        .pos-badge {
            background-color: #333;
            color: white;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            font-size: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            position: absolute;
            margin-left: 42px;
            margin-top: 42px;
            border: 2px solid white;
        }
        .player-data {
            display: flex;
            flex-direction: column;
        }
        .name-row {
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .flag-mini {
            width: 18px;
            border-radius: 2px;
        }
        .fechas-tag {
            font-size: 11px;
            color: #666;
            background-color: #f0f2f6;
            padding: 2px 6px;
            border-radius: 4px;
            width: fit-content;
            margin-top: 4px;
        }
        .points-box {
            text-align: center;
            background-color: #1e3d59;
            color: white;
            padding: 8px 12px;
            border-radius: 10px;
            min-width: 50px;
        }
        .disclaimer {
            font-size: 10px;
            color: #999;
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            border-top: 1px solid #eee;
        }
        </style>
    """, unsafe_allow_html=True)

    st.subheader("Leaderboard Oficial")
    
    df_actual = load_data()
    ranking = obtener_ranking_formateado(df_actual)
    
    if not ranking.empty:
        for _, row in ranking.iterrows():
            # Construcción de la tarjeta de cada jugador
            st.markdown(f"""
                <div class="player-card">
                    <div class="player-info">
                        <div style="position: relative;">
                            <img src="{row['Foto']}" class="player-photo">
                            <div class="pos-badge">{row['Pos']}</div>
                        </div>
                        <div class="player-data">
                            <div class="name-row">
                                <img src="{row['Pais']}" class="flag-mini">
                                <span style="font-weight: bold; font-size: 16px;">{row['Jugador']}</span>
                            </div>
                            <div class="fechas-tag">📅 {row['Fechas']} fechas jugadas</div>
                        </div>
                    </div>
                    <div class="points-box">
                        <div style="font-size: 9px; opacity: 0.8;">PTS</div>
                        <div style="font-size: 18px; font-weight: bold;">{int(row['Puntos'])}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        # --- AGREGAMOS EL DISCLAIMER DE AUTORÍA AL FINAL ---
        st.markdown(f"""
            <div class="disclaimer">
                © 2024 - 2026 <b>TORNEO EL HOYO 19</b>. <br>
                Queda estrictamente prohibida la utilización, copia o distribución 
                del código fuente y diseño de esta plataforma sin la autorización 
                expresa de los creadores.
            </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Sincronizando datos...")
        
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
