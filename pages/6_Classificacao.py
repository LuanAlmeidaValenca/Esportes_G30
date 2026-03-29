import streamlit as st
import pandas as pd
import json
import datetime
import utils.db_manager as db

st.set_page_config(page_title="Classificacao", layout="wide")

st.title("Tabela de Classificacao")
st.markdown("Ranking baseado na media de desempenho dos ultimos 30 dias.")

sports = db.get_sports()
if not sports:
    st.warning("Nenhum esporte cadastrado.")
    st.stop()

sport_dict = {s[1]: {"id": s[0], "attributes": s[2]} for s in sports}
selected_sport_name = st.selectbox("Selecione o Esporte", list(sport_dict.keys()))

sport_info = sport_dict[selected_sport_name]
sport_id = sport_info["id"]

evaluations = db.get_evaluations(sport_id=sport_id)

if not evaluations:
    st.info(f"Faltam dados para gerar a classificacao de {selected_sport_name}.")
    st.stop()

# Definir a janela de tempo (Ultimos 30 dias)
hoje = datetime.date.today()
limite_30_dias = hoje - datetime.timedelta(days=30)
limite_str = limite_30_dias.strftime("%Y-%m-%d")

st.markdown(f"*Considerando partidas entre **{limite_30_dias.strftime('%d/%m/%Y')}** e **{hoje.strftime('%d/%m/%Y')}**.*")

# Dicionario para acumular as notas dos ultimos 30 dias
player_recent_stats = {}

for eval_data in evaluations:
    eval_id, date, player_name, sport_name, scores_json, p_id, s_id = eval_data
    
    # Filtra apenas os jogos que ocorreram nos ultimos 30 dias
    if date >= limite_str:
        scores_dict = json.loads(scores_json)
        
        if scores_dict:
            match_avg = sum(scores_dict.values()) / len(scores_dict)
        else:
            match_avg = 0
            
        if player_name not in player_recent_stats:
            player_recent_stats[player_name] = {
                "total_score": 0,
                "matches": 0
            }
            
        player_recent_stats[player_name]["total_score"] += match_avg
        player_recent_stats[player_name]["matches"] += 1

if not player_recent_stats:
    st.info("Nenhuma partida registrada nos ultimos 30 dias para este esporte.")
    st.stop()

# Montando a tabela de lideres baseada na media do periodo
leaderboard = []
for player, stats in player_recent_stats.items():
    period_avg = stats["total_score"] / stats["matches"]
    leaderboard.append({
        "Jogador": player,
        "Dias": stats["matches"], # Mudou de "Partidas (30d)" para "Dias"
        "Nota Media (30d)": round(period_avg, 2)
    })

# Ordenando a lista da maior nota para a menor
leaderboard_sorted = sorted(leaderboard, key=lambda x: x["Nota Media (30d)"], reverse=True)

for index, item in enumerate(leaderboard_sorted):
    item["Posicao"] = index + 1

df = pd.DataFrame(leaderboard_sorted)
# Atualizamos também a ordem das colunas para refletir o novo nome
df = df[["Posicao", "Jogador", "Nota Media (30d)", "Dias"]]

st.subheader(f"Ranking - {selected_sport_name}")
st.dataframe(
    df, 
    use_container_width=True, 
    hide_index=True,
    column_config={
        "Posicao": st.column_config.NumberColumn("Posicao", format="%d"),
        "Nota Media (30d)": st.column_config.NumberColumn("Nota Media", format="%.2f")
    }
)