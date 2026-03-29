import streamlit as st
import utils.db_manager as db

st.set_page_config(page_title="Perfis", layout="wide")

st.title("Gestão de Perfis")
st.markdown("Lista, edita ou adiciona jogadores ao teu grupo.")

# Item 8: Ordem invertida
tab1, tab2 = st.tabs(["Lista e Edição", "Adicionar Novo Jogador"])

with tab1:
    st.subheader("Jogadores Registados")
    players = db.get_players()
    
    if not players:
        st.info("Nenhum jogador registado ainda.")
    else:
        for p_id, p_name in players:
            # Item 7: Edição através de um expander
            with st.expander(f"👤 {p_name}"):
                col1, col2 = st.columns([3, 1])
                with col1:
                    new_name = st.text_input("Editar Nome:", value=p_name, key=f"edit_p_{p_id}")
                    if st.button("Guardar Nome", key=f"save_p_{p_id}"):
                        if new_name.strip() != "" and new_name != p_name:
                            db.update_player(p_id, new_name.strip())
                            st.success("Nome atualizado com sucesso!")
                            st.rerun()
                with col2:
                    st.markdown("**Zona de Perigo**")
                    if st.button("Remover", type="primary", key=f"del_p_{p_id}"):
                        db.delete_player(p_id)
                        st.success("Jogador removido!")
                        st.rerun()

with tab2:
    st.subheader("Novo Jogador")
    with st.form("form_add_player", clear_on_submit=True):
        new_name = st.text_input("Nome do Jogador")
        submitted = st.form_submit_button("Registar Jogador")
        
        if submitted:
            if new_name.strip() == "":
                st.warning("O nome não pode estar vazio.")
            else:
                success = db.add_player(new_name.strip())
                if success:
                    st.success(f"Jogador '{new_name}' registado com sucesso!")
                    st.rerun()
                else:
                    st.error("Já existe um jogador com este nome.")