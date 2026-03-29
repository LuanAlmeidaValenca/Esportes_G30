import streamlit as st
import utils.db_manager as db

st.set_page_config(page_title="Perfis", layout="wide")

st.title("Gerenciamento de Perfis")
st.markdown("Adicione, visualize ou remova os jogadores do seu grupo.")

# Criando abas para organizar a tela
tab1, tab2 = st.tabs(["Adicionar Jogador", "Lista e Remocao"])

with tab1:
    st.subheader("Novo Jogador")
    with st.form("form_add_player", clear_on_submit=True):
        new_name = st.text_input("Nome do Jogador")
        submitted = st.form_submit_button("Cadastrar")
        
        if submitted:
            if new_name.strip() == "":
                st.warning("O nome nao pode estar vazio.")
            else:
                success = db.add_player(new_name.strip())
                if success:
                    st.success(f"Jogador '{new_name}' cadastrado com sucesso!")
                else:
                    st.error("Ja existe um jogador com este nome.")

with tab2:
    st.subheader("Jogadores Cadastrados")
    players = db.get_players()
    
    if not players:
        st.info("Nenhum jogador cadastrado ainda.")
    else:
        # Exibindo como uma lista simples
        for p_id, p_name in players:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**ID:** {p_id} | **Nome:** {p_name}")
            with col2:
                # Botão de deletar com chave única baseada no ID
                if st.button("Remover", key=f"del_player_{p_id}"):
                    db.delete_player(p_id)
                    st.success("Jogador removido. Atualize a pagina para ver as mudancas.")
                    st.rerun()