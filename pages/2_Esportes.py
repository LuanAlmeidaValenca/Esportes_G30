import streamlit as st
import utils.db_manager as db

st.set_page_config(page_title="Esportes", layout="wide")

st.title("Gerenciamento de Esportes")
st.markdown("Cadastre as modalidades e defina os atributos que serao avaliados em cada uma.")

tab1, tab2 = st.tabs(["Adicionar Esporte", "Lista e Remocao"])

with tab1:
    st.subheader("Novo Esporte")
    with st.form("form_add_sport", clear_on_submit=True):
        sport_name = st.text_input("Nome do Esporte (ex: Futebol, Volei)")
        attributes_input = st.text_input("Atributos (separe por virgula, ex: Passe, Chute, Fisico, Defesa)")
        
        submitted = st.form_submit_button("Cadastrar")
        
        if submitted:
            if sport_name.strip() == "" or attributes_input.strip() == "":
                st.warning("Preencha todos os campos.")
            else:
                # Limpa os espacos em branco de cada atributo
                attr_list = [attr.strip() for attr in attributes_input.split(",") if attr.strip()]
                
                if len(attr_list) < 3:
                    st.warning("E recomendavel ter pelo menos 3 atributos para gerar um grafico de radar decente.")
                else:
                    success = db.add_sport(sport_name.strip(), attr_list)
                    if success:
                        st.success(f"Esporte '{sport_name}' cadastrado com sucesso!")
                    else:
                        st.error("Ja existe um esporte com este nome.")

with tab2:
    st.subheader("Esportes Cadastrados")
    sports = db.get_sports()
    
    if not sports:
        st.info("Nenhum esporte cadastrado ainda.")
    else:
        for s_id, s_name, s_attr in sports:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"**{s_name}** | Atributos: {s_attr}")
            with col2:
                if st.button("Remover", key=f"del_sport_{s_id}"):
                    db.delete_sport(s_id)
                    st.success("Esporte removido. Atualize a pagina para ver as mudancas.")
                    st.rerun()