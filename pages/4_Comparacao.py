import streamlit as st
import pandas as pd
import json
import datetime
import plotly.express as px
from utils.charts import create_radar_chart
import utils.db_manager as db

st.set_page_config(page_title="Comparacao", layout="wide")

st.title("Comparacao Avancada de Desempenho")
st.markdown("Analise os jogadores de forma dinamica, por periodo, atributos e tipos de graficos.")

sports = db.get_sports()
if not sports:
    st.warning("Cadastre um esporte e registre avaliacoes primeiro.")
    st.stop()

sport_dict = {s[1]: {"id": s[0], "attributes": s[2]} for s in sports}
selected_sport_name = st.selectbox("1. Filtrar por Esporte", list(sport_dict.keys()), label_visibility="collapsed")

sport_info = sport_dict[selected_sport_name]
sport_id = sport_info["id"]
try:
    all_attributes = list(json.loads(sport_info["attributes"]).keys())
except:
    all_attributes = [attr.strip() for attr in sport_info["attributes"].split(",") if attr.strip()]

evaluations = db.get_evaluations(sport_id=sport_id)
if not evaluations:
    st.info(f"Nenhuma avaliacao registrada para {selected_sport_name} ainda.")
    st.stop()

st.markdown("---")
col_filtros1, col_filtros2 = st.columns(2)

with col_filtros1:
    st.subheader("2. Filtro de Periodo")
    period_type = st.radio(
        "Selecione o tipo de analise no tempo:",
        ["Periodo Unico (Medias Agregadas)", "Passagem de Tempo (Evolucao)"],
        horizontal=True
    )
    
    if period_type == "Periodo Unico (Medias Agregadas)":
        single_period_choice = st.selectbox(
            "Qual periodo deseja agregar?", 
            ["Ultimos 30 Dias", "Mes Especifico", "Dia Especifico"]
        )
        
        if single_period_choice == "Ultimos 30 Dias":
            start_date = (datetime.date.today() - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
            end_date = datetime.date.today().strftime("%Y-%m-%d")
        elif single_period_choice == "Mes Especifico":
            available_months = sorted(list(set([datetime.datetime.strptime(e[1], "%Y-%m-%d").strftime("%m/%Y") for e in evaluations])), reverse=True)
            if not available_months:
                st.stop()
            selected_month = st.selectbox("Selecione o Mes:", available_months)
            # Logica simplificada: pega as datas que contem o mes selecionado mais a frente
        elif single_period_choice == "Dia Especifico":
            available_days = sorted(list(set([e[1] for e in evaluations])), reverse=True)
            if not available_days:
                st.stop()
            selected_day = st.selectbox("Selecione o Dia:", available_days)
            start_date = selected_day
            end_date = selected_day
            
    else: # Passagem de Tempo
        col_data1, col_data2 = st.columns(2)
        with col_data1:
            start_date = st.date_input("Data Inicial", datetime.date.today() - datetime.timedelta(days=90)).strftime("%Y-%m-%d")
        with col_data2:
            end_date = st.date_input("Data Final", datetime.date.today()).strftime("%Y-%m-%d")

with col_filtros2:
    st.subheader("3. Variaveis")
    
    # Pega todos os jogadores que jogaram esse esporte para o filtro
    all_players = list(set([e[2] for e in evaluations]))
    selected_players = st.multiselect("Selecione os Jogadores:", all_players, default=..., label_visibility="collapsed")
    
    selected_attributes = st.multiselect("Selecione os Atributos:", all_attributes, default=all_attributes)

if not selected_players or not selected_attributes:
    st.warning("Selecione pelo menos um jogador e um atributo para prosseguir.")
    st.stop()

# --- PROCESSAMENTO DOS DADOS ---
filtered_data = []

for eval_data in evaluations:
    eval_id, date, player_name, sport_name, scores_json, p_id, s_id = eval_data
    
    # Filtro de Jogador
    if player_name not in selected_players:
        continue
        
    # Filtro de Data
    is_valid_date = False
    if period_type == "Periodo Unico (Medias Agregadas)":
        if single_period_choice == "Mes Especifico":
            if datetime.datetime.strptime(date, "%Y-%m-%d").strftime("%m/%Y") == selected_month:
                is_valid_date = True
        else:
            if start_date <= date <= end_date:
                is_valid_date = True
    else:
        if start_date <= date <= end_date:
            is_valid_date = True
            
    if is_valid_date:
        scores_dict = json.loads(scores_json)
        # Transforma cada atributo em uma linha separada para o DataFrame
        for attr in selected_attributes:
            filtered_data.append({
                "Data": date,
                "Jogador": player_name,
                "Atributo": attr,
                "Nota": scores_dict.get(attr, 0)
            })

if not filtered_data:
    st.info("Nenhum dado encontrado com os filtros aplicados.")
    st.stop()

df = pd.DataFrame(filtered_data)

# Agrega os dados se for Periodo Unico
is_single_period = period_type == "Periodo Unico (Medias Agregadas)"
if is_single_period:
    df_plot = df.groupby(["Jogador", "Atributo"])["Nota"].mean().reset_index()
    df_plot["Nota"] = df_plot["Nota"].round(2)
else:
    df_plot = df.sort_values(by="Data")

st.markdown("---")
st.subheader("4. Visualizacao")

viz_options = ["Grafico de Barras", "Grafico de Radar", "Tabela de Dados"]
selected_viz = st.radio("Selecione a forma de exibicao:", viz_options, horizontal=True)

# --- RENDERIZACAO CONDICIONAL ---

if selected_viz == "Tabela de Dados":
    if is_single_period:
        # Transforma a tabela: Atributos viram linhas e Jogadores viram colunas
        df_tabela = df_plot.pivot(index="Atributo", columns="Jogador", values="Nota").reset_index()
        df_tabela.columns.name = None # Limpa o cabecalho visual
        st.dataframe(df_tabela, use_container_width=True, hide_index=True)
    else:
        # Em passagem de tempo, mantem o formato com a data visivel
        st.dataframe(df_plot, use_container_width=True, hide_index=True)

elif selected_viz == "Grafico de Barras":
    if is_single_period:
        # REGRA: Apenas um grafico com todos os atributos lado a lado, separados por jogador
        fig = px.bar(
            df_plot, x="Jogador", y="Nota", color="Atributo", 
            barmode="group", text="Nota",
            title="Medias Agregadas por Jogador"
        )
        fig.update_traces(textposition='outside')
        fig.update_yaxes(range=[0, 10])
        st.plotly_chart(fig, use_container_width=True)
        
    else: # Passagem de tempo
        if len(selected_attributes) == 1:
            # REGRA: 1 Atributo -> Um grafico de colunas, jogadores lado a lado
            fig = px.bar(
                df_plot, x="Data", y="Nota", color="Jogador", 
                barmode="group", text="Nota",
                title=f"Evolucao do Atributo: {selected_attributes[0]}"
            )
            fig.update_traces(textposition='outside')
            fig.update_yaxes(range=[0, 10])
            st.plotly_chart(fig, use_container_width=True)
            
        else:
            # REGRA: >1 Atributo -> Um grafico para cada jogador, atributos lado a lado
            st.markdown("##### Graficos Individuais por Jogador")
            cols = st.columns(len(selected_players))
            
            for i, player in enumerate(selected_players):
                df_player = df_plot[df_plot["Jogador"] == player]
                if not df_player.empty:
                    fig = px.bar(
                        df_player, x="Data", y="Nota", color="Atributo", 
                        barmode="group", title=player
                    )
                    fig.update_yaxes(range=[0, 10])
                    # Desenha o grafico na coluna correspondente
                    with cols[i % len(cols)]: 
                        st.plotly_chart(fig, use_container_width=True)

elif selected_viz == "Grafico de Radar":
    if len(selected_attributes) < 3:
        st.error("O Grafico de Radar exige pelo menos 3 atributos selecionados para ser desenhado.")
    else:
        radar_mode = st.radio("Modo do Radar:", ["Sobreposto", "Lado a Lado"], horizontal=True)
        
        # Para o Radar, precisamos organizar as notas em listas
        radar_series = []
        for player in selected_players:
            df_player = df_plot[df_plot["Jogador"] == player]
            if not df_player.empty:
                # Se for passagem de tempo, pegamos a media geral do periodo para plotar o radar
                if not is_single_period:
                    df_player = df_player.groupby("Atributo")["Nota"].mean().reset_index()
                
                # Garante que as notas entrem na mesma ordem dos atributos selecionados
                scores = []
                for attr in selected_attributes:
                    val = df_player[df_player["Atributo"] == attr]["Nota"]
                    scores.append(val.values[0] if not val.empty else 0)
                    
                radar_series.append({"name": player, "scores": scores})
        
        if radar_mode == "Sobreposto":
            fig = create_radar_chart(
                data_series=radar_series,
                attributes=selected_attributes,
                title="Comparacao Sobreposta"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            # Lado a Lado
            cols = st.columns(len(selected_players))
            for i, series in enumerate(radar_series):
                fig = create_radar_chart(
                    data_series=[series], # Passa apenas um jogador por grafico
                    attributes=selected_attributes,
                    title=f"Radar - {series['name']}"
                )
                with cols[i % len(cols)]:
                    st.plotly_chart(fig, use_container_width=True)