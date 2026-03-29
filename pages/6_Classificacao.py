import streamlit as st
import pandas as pd
import json
import datetime
import utils.db_manager as db

st.set_page_config(page_title="Classificacao", layout="wide")

st.title("Tabela de Classificacao")
st.markdown("Veja quem sao os jogadores em melhor forma nos ultimos 30 dias e a sua evolucao.")

sports = db.get_sports()
if not sports:
    st.warning("Cadastre um esporte primeiro.")
    st.stop()

sport_dict = {s[1]: s[0] for s in sports}
selected_sport_name = st.selectbox("Selecione o Esporte", list(sport_dict.keys()), label_visibility="collapsed")
sport_id = sport_dict[selected_sport_name]

evaluations = db.get_evaluations(sport_id=sport_id)

if not evaluations:
    st.info(f"Nenhuma partida registrada para {selected_sport_name} ainda.")
    st.stop()

hoje = datetime.date.today()
player_stats = {}

# Agrupa as notas do periodo atual (0-30 dias) e anterior (31-60 dias)
for eval_data in evaluations:
    eval_id, date_str, player_name, s_name, scores_json, p_id, s_id = eval_data
    date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    days_diff = (hoje - date_obj).days
    
    scores_dict = json.loads(scores_json)
    match_avg = sum(scores_dict.values()) / len(scores_dict) if scores_dict else 0
    
    if player_name not in player_stats:
        player_stats[player_name] = {"current_sum": 0, "current_matches": 0, "prev_sum": 0, "prev_matches": 0}
        
    if days_diff <= 30:
        player_stats[player_name]["current_sum"] += match_avg
        player_stats[player_name]["current_matches"] += 1
    elif 30 < days_diff <= 60:
        player_stats[player_name]["prev_sum"] += match_avg
        player_stats[player_name]["prev_matches"] += 1

# Monta o ranking
leaderboard = []
for player, stats in player_stats.items():
    if stats["current_matches"] > 0:
        current_avg = stats["current_sum"] / stats["current_matches"]
        
        # Calcula a media do mes passado para ver a evolucao
        if stats["prev_matches"] > 0:
            prev_avg = stats["prev_sum"] / stats["prev_matches"]
            delta = current_avg - prev_avg
        else:
            delta = 0.0 # Sem dados anteriores para comparar
            
        # Formata a seta
        if delta > 0:
            evolucao = f"⬆️ +{delta:.2f}"
        elif delta < 0:
            evolucao = f"⬇️ {delta:.2f}"
        else:
            evolucao = "➖ 0.00"
            
        leaderboard.append({
            "Jogador": player,
            "Nota Media (30d)": round(current_avg, 2),
            "Evolucao": evolucao,
            "Dias": stats["current_matches"]
        })

if not leaderboard:
    st.info("Nenhum jogador atuou nos ultimos 30 dias.")
    st.stop()

# Ordena do melhor para o pior
leaderboard_sorted = sorted(leaderboard, key=lambda x: x["Nota Media (30d)"], reverse=True)

for index, item in enumerate(leaderboard_sorted):
    item["Posicao"] = index + 1

df = pd.DataFrame(leaderboard_sorted)
df = df[["Posicao", "Jogador", "Nota Media (30d)", "Evolucao", "Dias"]]

st.markdown("---")
st.dataframe(
    df, 
    use_container_width=True, 
    hide_index=True,
    column_config={
        "Posicao": st.column_config.NumberColumn("Pos", format="%d"),
        "Nota Media (30d)": st.column_config.NumberColumn("Nota Atual", format="%.2f")
    }
)