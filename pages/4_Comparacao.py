import streamlit as st
import json
import datetime
import utils.db_manager as db
from utils.charts import create_radar_chart

st.set_page_config(page_title="Comparacao", layout="wide")

st.title("Comparacao de Desempenho (Medias)")
st.markdown("Compare a consistencia dos jogadores agrupando os dados por periodo.")

sports = db.get_sports()

if not sports:
    st.warning("Cadastre um esporte e registre avaliacoes primeiro.")
    st.stop()

sport_dict = {s[1]: {"id": s[0], "attributes": s[2]} for s in sports}
selected_sport_name = st.selectbox("Filtrar por Esporte", list(sport_dict.keys()))

sport_info = sport_dict[selected_sport_name]
sport_id = sport_info["id"]
attributes_list = [attr.strip() for attr in sport_info["attributes"].split(",")]

# Busca as avaliacoes do esporte selecionado
evaluations = db.get_evaluations(sport_id=sport_id)

if not evaluations:
    st.info(f"Nenhuma avaliacao registrada para {selected_sport_name} ainda.")
    st.stop()

st.markdown("---")
st.subheader("Filtro de Periodo")

period_type = st.radio(
    "Como deseja agrupar os dados?",
    ["Ultimos 30 Dias", "Mes Especifico"],
    horizontal=True
)

filtered_evals = []

if period_type == "Ultimos 30 Dias":
    hoje = datetime.date.today()
    limite = hoje - datetime.timedelta(days=30)
    limite_str = limite.strftime("%Y-%m-%d")
    
    for eval_data in evaluations:
        if eval_data[1] >= limite_str: # eval_data[1] e a data
            filtered_evals.append(eval_data)
            
    st.markdown(f"**Analisando partidas de:** {limite.strftime('%d/%m/%Y')} ate {hoje.strftime('%d/%m/%Y')}")

else:
    # Extrai os meses unicos que possuem dados salvos
    available_months = set()
    for eval_data in evaluations:
        try:
            d = datetime.datetime.strptime(eval_data[1], "%Y-%m-%d")
            available_months.add(d.strftime("%m/%Y"))
        except ValueError:
            pass
            
    available_months = sorted(list(available_months), reverse=True)
    
    if not available_months:
        st.warning("Nao foi possivel identificar os meses das partidas salvas.")
        st.stop()
        
    selected_month = st.selectbox("Selecione o Mes/Ano:", available_months)
    
    for eval_data in evaluations:
        try:
            d = datetime.datetime.strptime(eval_data[1], "%Y-%m-%d")
            if d.strftime("%m/%Y") == selected_month:
                filtered_evals.append(eval_data)
        except ValueError:
            pass

if not filtered_evals:
    st.info("Nenhuma partida encontrada para o periodo selecionado.")
    st.stop()

# Agrupa as notas por jogador dentro do periodo filtrado
player_aggregated_data = {}

for eval_data in filtered_evals:
    eval_id, date, player_name, sport_name, scores_json, p_id, s_id = eval_data
    scores_dict = json.loads(scores_json)
    
    if player_name not in player_aggregated_data:
        player_aggregated_data[player_name] = {
            "match_count": 0,
            "sum_attributes": {attr: 0 for attr in attributes_list}
        }
        
    player_aggregated_data[player_name]["match_count"] += 1
    
    for attr in attributes_list:
        player_aggregated_data[player_name]["sum_attributes"][attr] += scores_dict.get(attr, 0)

st.markdown("---")
st.subheader("Jogadores")

# Permite escolher os jogadores que tem dados nesse periodo
available_players = list(player_aggregated_data.keys())
selected_players = st.multiselect(
    "Selecione os jogadores para comparar no grafico:",
    options=available_players,
    default=available_players[:2] if len(available_players) >= 2 else available_players
)

if selected_players:
    data_series = []
    
    for player in selected_players:
        player_data = player_aggregated_data[player]
        count = player_data["match_count"]
        
        # Calcula a media de cada atributo dividindo a soma total pela quantidade de jogos
        avg_scores_list = [
            round(player_data["sum_attributes"][attr] / count, 2) 
            for attr in attributes_list
        ]
        
        label_with_count = f"{player} ({count} jogos)"
        
        data_series.append({
            "name": label_with_count,
            "scores": avg_scores_list
        })
        
    fig = create_radar_chart(
        data_series=data_series,
        attributes=attributes_list,
        title=f"Comparativo de Medias - {selected_sport_name}"
    )
    
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Selecione pelo menos um jogador para gerar o grafico.")