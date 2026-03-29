import streamlit as st
import pandas as pd
import json
import utils.db_manager as db

st.set_page_config(page_title="Esportes", layout="wide")

st.title("Gestão de Esportes")
st.markdown("Lista as modalidades, altera os atributos e as suas explicações.")

# Função de compatibilidade: Lida com dados antigos ou novos
def parse_attributes(attr_str):
    try:
        return json.loads(attr_str)
    except:
        return {a.strip(): "" for a in attr_str.split(",") if a.strip()}

# Item 10: Ordem invertida
tab1, tab2 = st.tabs(["Lista e Edição", "Adicionar Novo Esporte"])

with tab1:
    st.subheader("Esportes Registados")
    sports = db.get_sports()
    
    if not sports:
        st.info("Nenhum esporte registado ainda.")
    else:
        for s_id, s_name, s_attr in sports:
            with st.expander(f"🏅 {s_name}"):
                current_attrs = parse_attributes(s_attr)
                # Cria a tabela de dados
                df_current = pd.DataFrame([{"Atributo": k, "Explicação": v} for k, v in current_attrs.items()])
                
                # Item 7: Editar nome do Esporte
                new_name = st.text_input("Nome do Esporte", value=s_name, key=f"name_{s_id}")
                st.markdown("**Atributos e Explicações:** (Adicione novas linhas abaixo)")
                
                edited_df = st.data_editor(df_current, num_rows="dynamic", key=f"editor_{s_id}", use_container_width=True)
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    if st.button("Guardar Alterações", key=f"save_{s_id}"):
                        new_attrs_dict = {}
                        for _, row in edited_df.iterrows():
                            attr_name = str(row["Atributo"]).strip() if pd.notna(row["Atributo"]) else ""
                            attr_desc = str(row["Explicação"]).strip() if pd.notna(row["Explicação"]) else ""
                            if attr_name:
                                new_attrs_dict[attr_name] = attr_desc
                                
                        if len(new_attrs_dict) == 0:
                            st.warning("O esporte tem de ter pelo menos um atributo.")
                        else:
                            db.update_sport(s_id, new_name, new_attrs_dict)
                            st.success("Esporte atualizado com sucesso!")
                            st.rerun()
                with col2:
                    st.markdown("**Zona de Perigo**")
                    if st.button("Remover Esporte", type="primary", key=f"del_{s_id}"):
                        db.delete_sport(s_id)
                        st.rerun()

with tab2:
    st.subheader("Novo Esporte")
    new_sport_name = st.text_input("Nome do Novo Esporte")
    st.markdown("Escreva os atributos e as explicações (A explicação é opcional).")
    
    # Item 2: Tabela para adicionar múltiplos parâmetros
    df_new = pd.DataFrame([{"Atributo": "", "Explicação": ""}] * 3)
    new_edited_df = st.data_editor(df_new, num_rows="dynamic", key="new_editor", use_container_width=True)
    
    if st.button("Registar Esporte"):
        if not new_sport_name.strip():
            st.warning("Preencha o nome do esporte.")
        else:
            new_attrs_dict = {}
            for _, row in new_edited_df.iterrows():
                attr_name = str(row["Atributo"]).strip() if pd.notna(row["Atributo"]) else ""
                attr_desc = str(row["Explicação"]).strip() if pd.notna(row["Explicação"]) else ""
                if attr_name:
                    new_attrs_dict[attr_name] = attr_desc
            
            if len(new_attrs_dict) == 0:
                st.warning("Preencha pelo menos um atributo na tabela.")
            else:
                success = db.add_sport(new_sport_name.strip(), new_attrs_dict)
                if success:
                    st.success(f"Esporte '{new_sport_name}' registado com sucesso!")
                    st.rerun()
                else:
                    st.error("Já existe um esporte com este nome.")