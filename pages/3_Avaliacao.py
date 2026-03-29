import streamlit as st
import datetime
import json
import utils.db_manager as db

st.set_page_config(page_title="Avaliação", layout="wide")

st.title("Avaliação de Desempenho")
st.markdown("Registe as notas de um jogador numa partida específica.")

players = db.get_players()
sports = db.get_sports()

if not players or not sports:
    st.warning("Precisa de registar pelo menos um jogador e um esporte antes de avaliar.")
    st.stop()

player_dict = {p[1]: p[0] for p in players}
sport_dict = {s[1]: {"id": s[0], "attributes": s[2]} for s in sports}

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Dados da Partida")
    selected_date = st.date_input("Data do Jogo", datetime.date.today())
    selected_player_name = st.selectbox("Jogador", list(player_dict.keys()))
    selected_sport_name = st.selectbox("Esporte", list(sport_dict.keys()))

with col2:
    st.subheader("Notas por Atributo")
    st.markdown("Atribua uma nota de 0 a 10 para cada fundamento. Passe o rato por cima da interrogação (?) para ver o detalhe.")
    
    sport_info = sport_dict[selected_sport_name]
    
    # Processa os atributos salvos (compatível com o modelo velho e o novo)
    try:
        attr_dict = json.loads(sport_info["attributes"])
    except:
        attr_dict = {a.strip(): "" for a in sport_info["attributes"].split(",") if a.strip()}
    
    scores_dict = {}
    
    with st.form("form_evaluation", clear_on_submit=True):
        # Item 2: Usa o parâmetro 'help' nativo do Streamlit para criar a interrogação explicativa
        for attr_name, attr_desc in attr_dict.items():
            help_text = attr_desc if attr_desc else "Sem descrição definida"
            scores_dict[attr_name] = st.slider(
                attr_name, 
                min_value=0, max_value=10, value=5, step=1,
                help=help_text
            )
            
        submitted = st.form_submit_button("Guardar Avaliação")
        
        if submitted:
            player_id = player_dict[selected_player_name]
            sport_id = sport_info["id"]
            date_str = selected_date.strftime("%Y-%m-%d")
            
            db.add_evaluation(date_str, player_id, sport_id, scores_dict)
            st.success("Avaliação guardada com sucesso!")