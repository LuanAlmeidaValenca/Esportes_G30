import streamlit as st
import pandas as pd
import json
import datetime
import plotly.express as px
import utils.db_manager as db
from utils.charts import create_radar_chart

st.set_page_config(page_title="Dashboard do Jogador", layout="wide")

st.title("Dashboard do Jogador")
st.markdown("Acompanhe as suas estatisticas, a sua evolucao e faça a gestao dos seus jogos.")

# Carregar jogadores
players = db.get_players()
if not players:
    st.warning("Nenhum jogador registado.")
    st.stop()

player_dict = {p[1]: p[0] for p in players}
selected_player_name = st.selectbox("Selecione o Jogador", list(player_dict.keys()))
player_id = player_dict[selected_player_name]

# Carregar desportos
sports = db.get_sports()
if not sports:
    st.warning("Nenhum desporto registado.")
    st.stop()

sport_dict = {s[1]: {"id": s[0], "attributes": s[2]} for s in sports}
selected_sport_name = st.selectbox("Selecione o Desporto para analisar", list(sport_dict.keys()))

sport_info = sport_dict[selected_sport_name]
sport_id = sport_info["id"]
try:
    attributes_list = list(json.loads(sport_info["attributes"]).keys())
except:
    attributes_list = [attr.strip() for attr in sport_info["attributes"].split(",") if attr.strip()]

# Buscar avaliacoes especificas deste jogador e desporto
evaluations = db.get_evaluations(sport_id=sport_id, player_id=player_id)

st.markdown("---")

# Separar a interface em separadores (tabs) para organizar o dashboard
tab1, tab2, tab3 = st.tabs(["Visao Geral", "Registar Partida", "O Meu Historico"])

with tab1:
    if not evaluations:
        st.info(f"Nenhum dado encontrado para {selected_player_name} em {selected_sport_name}.")
    else:
        # Processar dados para a evolucao historica (todos os jogos)
        history_data = []
        for eval_data in evaluations:
            eval_id, date, p_name, s_name, scores_json, p_id, s_id = eval_data
            scores_dict = json.loads(scores_json)
            match_avg = sum(scores_dict.values()) / len(scores_dict) if scores_dict else 0
            
            row = {"ID": eval_id, "Data": date, "Media": match_avg, "Notas": scores_dict}
            history_data.append(row)
            
        # Ordenar cronologicamente para o grafico de linha
        history_data = sorted(history_data, key=lambda x: x["Data"])
        
        # Calcular a media dos ultimos 30 dias para o Radar
        hoje = datetime.date.today()
        limite_30_dias = hoje - datetime.timedelta(days=30)
        limite_str = limite_30_dias.strftime("%Y-%m-%d")
        
        recent_matches = [match for match in history_data if match["Data"] >= limite_str]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Forma Atual (Ultimos 30 Dias)")
            
            if not recent_matches:
                st.warning("Nenhuma partida jogada nos ultimos 30 dias. Jogue para atualizar a sua forma atual!")
            else:
                num_matches = len(recent_matches)
                st.write(f"**Partidas analisadas:** {num_matches}")
                
                # Somar e dividir os atributos pelo numero de jogos recentes
                sum_attributes = {attr: 0 for attr in attributes_list}
                total_recent_avg = 0
                
                for match in recent_matches:
                    total_recent_avg += match["Media"]
                    for attr in attributes_list:
                        sum_attributes[attr] += match["Notas"].get(attr, 0)
                
                avg_scores_list = [round(sum_attributes[attr] / num_matches, 2) for attr in attributes_list]
                final_recent_avg = round(total_recent_avg / num_matches, 2)
                
                st.write(f"**Nota Media Geral (30d):** {final_recent_avg}")
                
                fig_radar = create_radar_chart(
                    data_series=[{"name": f"{selected_player_name} (30d)", "scores": avg_scores_list}],
                    attributes=attributes_list,
                    title="Desempenho Medio Recente"
                )
                st.plotly_chart(fig_radar, use_container_width=True)
            
        with col2:
            st.subheader("Evolucao ao Longo do Tempo")
            df_evolution = pd.DataFrame(history_data)
            
            # Criar grafico de linha usando Plotly Express para mostrar todas as partidas
            fig_line = px.line(
                df_evolution, 
                x="Data", 
                y="Media", 
                markers=True,
                title="Historico da Nota Geral por Partida"
            )
            fig_line.update_yaxes(range=[0, 10])
            st.plotly_chart(fig_line, use_container_width=True)

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
            st.success("Partida registada com sucesso! Atualize a pagina para ver os graficos.")

with tab3:
    st.subheader("O Meu Historico de Jogos")
    if not evaluations:
        st.write("Sem historico para exibir.")
    else:
        # Prepara tabela de historico
        table_data = []
        for match in history_data: # history_data foi criado no tab1
            row = {"ID": match["ID"], "Data": match["Data"], "Media": round(match["Media"], 2)}
            row.update(match["Notas"])
            table_data.append(row)
            
        df_history = pd.DataFrame(table_data)
        # Ordenar da mais recente para a mais antiga na visualizacao
        df_history = df_history.sort_values(by="Data", ascending=False)
        st.dataframe(df_history, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.write("**Eliminar Registo:**")
        id_to_delete = st.selectbox("Selecione o ID para excluir", [row["ID"] for row in table_data])
        if st.button("Excluir Partida Selecionada", type="primary"):
            db.delete_evaluation(id_to_delete)
            st.success("Partida excluida! Atualize a pagina.")