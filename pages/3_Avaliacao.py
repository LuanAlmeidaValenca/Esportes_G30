import streamlit as st
import datetime
import utils.db_manager as db

st.set_page_config(page_title="Avaliacao", layout="wide")

st.title("Avaliacao de Desempenho")
st.markdown("Registre as notas de um jogador em uma partida especifica.")

# Carregar dados necessarios
players = db.get_players()
sports = db.get_sports()

if not players or not sports:
    st.warning("Voce precisa cadastrar pelo menos um jogador e um esporte antes de avaliar.")
    st.stop()

# Criar dicionarios para facilitar a selecao
player_dict = {p[1]: p[0] for p in players}
sport_dict = {s[1]: {"id": s[0], "attributes": s[2]} for s in sports}

# Layout da pagina
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Dados da Partida")
    selected_date = st.date_input("Data do Jogo", datetime.date.today())
    selected_player_name = st.selectbox("Jogador", list(player_dict.keys()))
    selected_sport_name = st.selectbox("Esporte", list(sport_dict.keys()))

with col2:
    st.subheader("Notas por Atributo")
    st.markdown("Atribua uma nota de 0 a 10 para cada fundamento.")
    
    # Recupera os atributos do esporte selecionado e separa em uma lista
    sport_info = sport_dict[selected_sport_name]
    attributes_list = sport_info["attributes"].split(",")
    
    # Dicionario para armazenar as notas que o usuario escolher
    scores_dict = {}
    
    with st.form("form_evaluation", clear_on_submit=True):
        for attr in attributes_list:
            # Cria um slider para cada atributo
            scores_dict[attr.strip()] = st.slider(attr.strip(), min_value=0, max_value=10, value=5, step=1)
            
        submitted = st.form_submit_button("Salvar Avaliacao")
        
        if submitted:
            player_id = player_dict[selected_player_name]
            sport_id = sport_info["id"]
            
            # Converte a data para string no formato AAAA-MM-DD
            date_str = selected_date.strftime("%Y-%m-%d")
            
            db.add_evaluation(date_str, player_id, sport_id, scores_dict)
            st.success("Avaliacao salva com sucesso!")