import streamlit as st
import pandas as pd
import json
import utils.db_manager as db

st.set_page_config(page_title="Historico", layout="wide")

st.title("Historico de Partidas")
st.markdown("Visualize, edite ou exclua avaliacoes passadas.")

sports = db.get_sports()
if not sports:
    st.warning("Nenhum esporte cadastrado.")
    st.stop()

# Filtro por esporte
sport_dict = {s[1]: {"id": s[0], "attributes": s[2]} for s in sports}
selected_sport_name = st.selectbox("Filtrar por Esporte", list(sport_dict.keys()))

sport_info = sport_dict[selected_sport_name]
sport_id = sport_info["id"]
try:
    attributes_list = list(json.loads(sport_info["attributes"]).keys())
except:
    attributes_list = [attr.strip() for attr in sport_info["attributes"].split(",") if attr.strip()]

# Busca avaliacoes do esporte selecionado
evaluations = db.get_evaluations(sport_id=sport_id)

if not evaluations:
    st.info(f"Nenhum historico encontrado para {selected_sport_name}.")
    st.stop()

# Prepara os dados para exibir em uma tabela interativa (DataFrame)
table_data = []
eval_dict = {} # Para facilitar a busca na hora de editar

for eval_data in evaluations:
    eval_id, date, player_name, sport_name, scores_json, p_id, s_id = eval_data
    scores_dict = json.loads(scores_json)
    
    # Monta a linha da tabela
    row = {"ID": eval_id, "Data": date, "Jogador": player_name}
    row.update(scores_dict) # Adiciona as notas como colunas
    table_data.append(row)
    
    eval_dict[eval_id] = {"date": date, "player": player_name, "scores": scores_dict}

st.subheader("Registros Salvos")
df = pd.DataFrame(table_data)
st.dataframe(df, use_container_width=True, hide_index=True)

st.markdown("---")
st.subheader("Editar ou Excluir Registro")

# Seleciona o ID do registro que deseja alterar
selected_id = st.selectbox("Selecione o ID da avaliacao que deseja modificar:", [row["ID"] for row in table_data])

if selected_id:
    current_data = eval_dict[selected_id]
    st.write(f"**Editando:** {current_data['player']} - {current_data['date']}")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        with st.form(f"form_edit_{selected_id}"):
            st.markdown("**Alterar Notas:**")
            new_scores = {}
            for attr in attributes_list:
                # O valor padrao do slider sera a nota que ja estava salva
                current_score = current_data["scores"].get(attr, 5)
                new_scores[attr] = st.slider(attr, min_value=0, max_value=10, value=current_score, step=1)
                
            btn_update = st.form_submit_button("Atualizar Notas")
            
            if btn_update:
                db.update_evaluation(selected_id, new_scores)
                st.success("Avaliacao atualizada com sucesso! Atualize a pagina.")
                st.rerun()
                
    with col2:
        st.markdown("**Zona de Perigo:**")
        if st.button("Excluir esta Avaliacao", type="primary"):
            db.delete_evaluation(selected_id)
            st.success("Avaliacao excluida! Atualize a pagina.")
            st.rerun()