import streamlit as st
import pandas as pd
import json
import datetime
import utils.db_manager as db

st.set_page_config(page_title="Historico Geral", layout="wide")

st.title("Historico Geral de Partidas")
st.markdown("Verifique os registos detalhados dos jogos.")

sports = db.get_sports()
if not sports:
    st.warning("Cadastre um esporte primeiro.")
    st.stop()

sport_dict = {s[1]: {"id": s[0], "attributes": s[2]} for s in sports}
selected_sport_name = st.selectbox("Selecione o Esporte", list(sport_dict.keys()), label_visibility="collapsed")
sport_info = sport_dict[selected_sport_name]
sport_id = sport_info["id"]

evaluations = db.get_evaluations(sport_id=sport_id)

if not evaluations:
    st.info(f"Nenhum historico para {selected_sport_name}.")
    st.stop()

st.markdown("---")
# ITEM 11: Filtro temporal obrigatorio
period_type = st.radio("Filtrar por:", ["Ultimos 30 Dias", "Mes Especifico"], horizontal=True)

filtered_evals = []
hoje = datetime.date.today()

if period_type == "Ultimos 30 Dias":
    limite = (hoje - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
    filtered_evals = [e for e in evaluations if e[1] >= limite]
else:
    available_months = sorted(list(set([datetime.datetime.strptime(e[1], "%Y-%m-%d").strftime("%m/%Y") for e in evaluations])), reverse=True)
    if not available_months:
        st.stop()
    selected_month = st.selectbox("Selecione o Mes/Ano:", available_months)
    filtered_evals = [e for e in evaluations if datetime.datetime.strptime(e[1], "%Y-%m-%d").strftime("%m/%Y") == selected_month]

if not filtered_evals:
    st.info("Nenhuma partida encontrada neste periodo.")
else:
    table_data = []
    for eval_data in filtered_evals:
        eval_id, date_str, player_name, s_name, scores_json, p_id, s_id = eval_data
        scores_dict = json.loads(scores_json)
        
        row = {
            "ID": eval_id,
            "Data": date_str,
            "Jogador": player_name,
            "Media": round(sum(scores_dict.values()) / len(scores_dict), 2)
        }
        row.update(scores_dict)
        table_data.append(row)

    df = pd.DataFrame(table_data)
    df = df.sort_values(by="Data", ascending=False)
    
    st.write(f"**Total de Partidas no periodo:** {len(table_data)}")
    st.dataframe(df, use_container_width=True, hide_index=True)