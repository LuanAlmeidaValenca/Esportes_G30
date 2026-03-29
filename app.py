import streamlit as st
from utils.db_manager import init_db

# Configuração da página principal
st.set_page_config(
    page_title="Sports Tracker",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializa o banco de dados e as tabelas (roda apenas uma vez ou se o banco não existir)
init_db()

def main():
    st.title("Sistema de Acompanhamento Esportivo")
    st.markdown("---")
    
    st.markdown("""
    Bem-vindo ao sistema de avaliação e acompanhamento de desempenho esportivo. 
    
    Utilize o menu lateral para navegar entre as funcionalidades:
    
    * **Perfis:** Cadastre, edite ou remova os jogadores do seu grupo.
    * **Esportes:** Defina as modalidades que vocês praticam e os atributos avaliados em cada uma (ex: Chute, Passe, Físico).
    * **Avaliação:** Registre uma nova partida, selecione o esporte e dê as notas para cada jogador.
    * **Comparação:** Visualize gráficos de radar comparando diferentes jogadores ou a evolução de um mesmo jogador ao longo do tempo.
    * **Histórico:** Consulte jogos passados e edite notas, se necessário.
    * **Classificacao:** Veja a tabela de líderes baseada nas médias gerais.
    
    Para começar, sugerimos que você cadastre primeiro os **Esportes** e depois os **Perfis** dos jogadores.
    """)

if __name__ == "__main__":
    main()