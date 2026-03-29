import streamlit as st
import pandas as pd
import json
import datetime
import plotly.express as px
import utils.db_manager as db
from utils.charts import create_radar_chart

st.set_page_config(page_title="Dashboard", layout="wide")

players = db.get_players()
if not players:
    st.warning("Nenhum jogador registado.")
    st.stop()

player_dict = {p[1]: {"id": p[0], "photo": p[2]} for p in players}
selected_player_name = st.selectbox("Selecione o Jogador", list(player_dict.keys()), label_visibility="collapsed")

p_info = player_dict[selected_player_name]
player_id = p_info["id"]

col_img, col_title = st.columns([1, 6])
with col_img:
    if p_info["photo"]:
        st.image(f"data:image/jpeg;base64,{p_info['photo']}", width=100)
    else:
        st.image("https://via.placeholder.com/150?text=Sem+Foto", width=100)
with col_title:
    st.title(f"Dashboard: {selected_player_name}")
    st.markdown("Acompanhe as suas estatisticas e evolucao comparativa.")

sports = db.get_sports()
if not sports:
    st.stop()

sport_dict = {s[1]: {"id": s[0], "attributes": s[2]} for s in sports}
selected_sport_name = st.selectbox("Selecione o Esporte", list(sport_dict.keys()), label_visibility="collapsed")
sport_info = sport_dict[selected_sport_name]
sport_id = sport_info["id"]

try:
    attributes_list = list(json.loads(sport_info["attributes"]).keys())
except:
    attributes_list = [attr.strip() for attr in sport_info["attributes"].split(",") if attr.strip()]

evaluations = db.get_evaluations(sport_id=sport_id, player_id=player_id)

st.markdown("---")

tab1, tab2, tab3 = st.tabs(["Visao Geral", "Registar Partida", "O Meu Historico"])

if evaluations:
    history_data = []
    for eval_data in evaluations:
        eval_id, date_str, p_name, s_name, scores_json, p_id, s_id = eval_data
        scores_dict = json.loads(scores_json)
        match_avg = sum(scores_dict.values()) / len(scores_dict) if scores_dict else 0
        history_data.append({"ID": eval_id, "Data": date_str, "Media": match_avg, "Notas": scores_dict})
    
    history_data = sorted(history_data, key=lambda x: x["Data"])
    hoje = datetime.date.today()

with tab1:
    if not evaluations:
        st.info("Nenhum dado encontrado para analisar.")
    else:
        # ITEM 11: Filtro de periodo obrigatorio, removido historico completo padrao
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            period_type = st.radio("Período de Analise:", ["Ultimos 30 Dias", "Mes Especifico"], horizontal=True)
        
        current_matches = []
        prev_matches = []
        
        if period_type == "Ultimos 30 Dias":
            limite_atual = (hoje - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
            limite_anterior = (hoje - datetime.timedelta(days=60)).strftime("%Y-%m-%d")
            
            current_matches = [m for m in history_data if m["Data"] >= limite_atual]
            prev_matches = [m for m in history_data if limite_anterior <= m["Data"] < limite_atual]
            
        else:
            available_months = sorted(list(set([datetime.datetime.strptime(m["Data"], "%Y-%m-%d").strftime("%m/%Y") for m in history_data])), reverse=True)
            if not available_months:
                st.warning("Sem meses validos.")
                st.stop()
            with col_f2:
                selected_month = st.selectbox("Selecione o Mes:", available_months)
                
            # Identifica o mes selecionado e o mes imediatamente anterior para comparacao
            m_obj = datetime.datetime.strptime(selected_month, "%m/%Y")
            mes_anterior = (m_obj.replace(day=1) - datetime.timedelta(days=1)).strftime("%m/%Y")
            
            current_matches = [m for m in history_data if datetime.datetime.strptime(m["Data"], "%Y-%m-%d").strftime("%m/%Y") == selected_month]
            prev_matches = [m for m in history_data if datetime.datetime.strptime(m["Data"], "%Y-%m-%d").strftime("%m/%Y") == mes_anterior]

        if not current_matches:
            st.warning("Nenhuma partida jogada neste periodo especifico.")
        else:
            # Calcula medias do periodo atual
            num_current = len(current_matches)
            total_current_avg = sum(m["Media"] for m in current_matches) / num_current
            current_attrs = {attr: sum(m["Notas"].get(attr, 0) for m in current_matches) / num_current for attr in attributes_list}
            
            # Calcula medias do periodo anterior (para as setas)
            num_prev = len(prev_matches)
            if num_prev > 0:
                total_prev_avg = sum(m["Media"] for m in prev_matches) / num_prev
                prev_attrs = {attr: sum(m["Notas"].get(attr, 0) for m in prev_matches) / num_prev for attr in attributes_list}
            else:
                total_prev_avg = total_current_avg # Força delta 0
                prev_attrs = current_attrs

            st.markdown("### Forma no Periodo")
            # Metrica Geral com Seta
            delta_geral = total_current_avg - total_prev_avg
            st.metric(label="Nota Media Geral", value=f"{total_current_avg:.2f}", delta=f"{delta_geral:.2f}")
            
            st.markdown("---")
            col_grafico, col_metricas = st.columns([2, 1])
            
            with col_grafico:
                avg_scores_list = [round(current_attrs[attr], 2) for attr in attributes_list]
                fig_radar = create_radar_chart(
                    data_series=[{"name": f"Media do Periodo", "scores": avg_scores_list}],
                    attributes=attributes_list,
                    title="Desempenho por Atributo"
                )
                st.plotly_chart(fig_radar, use_container_width=True)
                
            with col_metricas:
                st.markdown("#### Evolucao dos Atributos")
                # ITEM 12: Setas de evolucao dinamicas para cada atributo isolado
                for attr in attributes_list:
                    val_atual = current_attrs[attr]
                    val_anterior = prev_attrs[attr]
                    delta_attr = val_atual - val_anterior
                    st.metric(label=attr, value=f"{val_atual:.2f}", delta=f"{delta_attr:.2f}")

with tab2:
    st.subheader("Registar Novo Jogo")
    selected_date = st.date_input("Data da Partida", datetime.date.today())
    scores_dict_new = {}
    with st.form("form_new_eval_dashboard", clear_on_submit=True):
        st.write("Insira as notas de 0 a 10:")
        for attr in attributes_list:
            scores_dict_new[attr] = st.slider(f"{attr} ", min_value=0, max_value=10, value=5, step=1)
        if st.form_submit_button("Guardar Partida"):
            date_str = selected_date.strftime("%Y-%m-%d")
            db.add_evaluation(date_str, player_id, sport_id, scores_dict_new)
            st.success("Partida registada! Atualize a pagina.")

with tab3:
    st.subheader("Historico Filtrado")
    if not evaluations:
        st.write("Sem historico para exibir.")
    else:
        # Mostra na tabela apenas os jogos do periodo selecionado na Tab 1
        if not current_matches:
            st.info("Altere o filtro na Visao Geral para ver jogos.")
        else:
            table_data = []
            for match in current_matches:
                row = {"ID": match["ID"], "Data": match["Data"], "Media": round(match["Media"], 2)}
                row.update(match["Notas"])
                table_data.append(row)
                
            df_history = pd.DataFrame(table_data).sort_values(by="Data", ascending=False)
            st.dataframe(df_history, use_container_width=True, hide_index=True)
            
            st.markdown("---")
            id_to_delete = st.selectbox("ID para excluir", [row["ID"] for row in table_data])
            if st.button("Excluir Partida", type="primary"):
                db.delete_evaluation(id_to_delete)
                st.success("Partida excluida! Atualize a pagina.")