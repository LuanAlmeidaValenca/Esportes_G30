import streamlit as st
import base64
from PIL import Image
import io
import utils.db_manager as db

st.set_page_config(page_title="Perfis", layout="wide")

def process_image(uploaded_file):
    if uploaded_file is None:
        return None
    img = Image.open(uploaded_file)
    # Redimensiona para uma miniatura para nao pesar o banco de dados
    img.thumbnail((200, 200))
    if img.mode in ("RGBA", "P"): 
        img = img.convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=80)
    return base64.b64encode(buf.getvalue()).decode()

st.title("Gestao de Perfis")
st.markdown("Lista, edita ou adiciona jogadores ao teu grupo.")

tab1, tab2 = st.tabs(["Lista e Edicao", "Adicionar Novo Jogador"])

with tab1:
    st.subheader("Jogadores Registados")
    players = db.get_players()
    
    if not players:
        st.info("Nenhum jogador registado ainda.")
    else:
        for player in players:
            p_id, p_name, p_photo = player
            with st.expander(f"{p_name}"):
                col_img, col_info, col_del = st.columns([1, 3, 1])
                
                with col_img:
                    if p_photo:
                        st.image(f"data:image/jpeg;base64,{p_photo}", width=120)
                    else:
                        st.image("https://via.placeholder.com/150?text=Sem+Foto", width=120)
                        
                with col_info:
                    new_name = st.text_input("Editar Nome:", value=p_name, key=f"edit_n_{p_id}")
                    new_photo = st.file_uploader("Alterar Foto", type=["png", "jpg", "jpeg"], key=f"edit_f_{p_id}")
                    
                    if st.button("Guardar Alteracoes", key=f"save_p_{p_id}"):
                        photo_str = p_photo
                        if new_photo:
                            photo_str = process_image(new_photo)
                            
                        if new_name.strip() != "":
                            db.update_player(p_id, new_name.strip(), photo_str)
                            st.success("Perfil atualizado!")
                            st.rerun()
                            
                with col_del:
                    st.markdown("**Zona de Perigo**")
                    if st.button("Remover", type="primary", key=f"del_p_{p_id}"):
                        db.delete_player(p_id)
                        st.success("Jogador removido!")
                        st.rerun()

with tab2:
    st.subheader("Novo Jogador")
    with st.form("form_add_player", clear_on_submit=True):
        new_name = st.text_input("Nome do Jogador")
        new_photo = st.file_uploader("Foto de Perfil (Opcional)", type=["png", "jpg", "jpeg"])
        submitted = st.form_submit_button("Registar Jogador")
        
        if submitted:
            if new_name.strip() == "":
                st.warning("O nome nao pode estar vazio.")
            else:
                photo_str = process_image(new_photo) if new_photo else None
                success = db.add_player(new_name.strip(), photo_str)
                if success:
                    st.success(f"Jogador '{new_name}' registado com sucesso!")
                    st.rerun()
                else:
                    st.error("Ja existe um jogador com este nome.")