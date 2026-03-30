# 🏆 Sistema de Acompanhamento Esportivo

Um sistema web interativo e dinâmico desenvolvido em Python para registrar, avaliar e analisar o desempenho esportivo de um grupo de jogadores. O aplicativo permite criar esportes personalizados, registrar notas por atributos específicos e gerar dashboards e gráficos comparativos em tempo real.

## Antes de prosseguir

Todo o projeto foi desenvolvido utilizando o auxílio de geração de código utilizando inteligência artificial (Gemini Pro), ele não foi projetado para ser utilizado por um alto volume de pessoas, é apenas uma ferramente feita para um grupo amigos que gostam de competir entre si, minha única função no desenvolvimento foi de idealização, descrição de funcionalidades e refino de alguns trechos de código.

## 🌿 Arquitetura e Branches do Projeto

Este repositório possui duas versões do sistema para atender a diferentes necessidades:

* **[Branch `master` (Nuvem / Produção) - VOCÊ ESTÁ AQUI]**: Utiliza o **Turso (libSQL)** como banco de dados remoto e é otimizado para deploy gratuito no **Streamlit Community Cloud**. Ideal se você quer criar um link público para os seus amigos acessarem e adicionarem notas simultaneamente.
* **[Branch `local-sqlite` (Local / Offline)]**: Utiliza o **SQLite** clássico com um arquivo de banco de dados local (`.db`). Ideal se você quer apenas clonar o projeto, estudar o código ou rodar estritamente na sua máquina sem depender de internet ou serviços de terceiros. Mude para a branch `local-sqlite` para ver as instruções específicas.

## 🚀 Funcionalidades

O sistema é dividido em módulos de fácil acesso pelo menu lateral:

* **🏠 App (Início):** Visão geral e boas-vindas ao sistema.
* **👤 Perfis:** Cadastro, edição e remoção de jogadores, com suporte a upload de fotos de perfil (salvas de forma otimizada no banco de dados).
* **🏅 Esportes:** Criação de modalidades esportivas 100% customizáveis. É possível definir quais atributos (ex: Passe, Chute, Velocidade) pertencem a cada esporte e adicionar textos explicativos para ajudar na hora da avaliação.
* **📝 Avaliação:** Interface limpa para registrar o desempenho de um jogador em uma data específica. Utiliza *sliders* de 0 a 10 com dicas interativas (tooltips) baseadas nas explicações dos atributos.
* **📊 Comparação:** Ferramenta avançada de Business Intelligence (BI) para comparar jogadores. Suporta visualização de médias agregadas ou passagem de tempo usando Gráficos de Radar (sobrepostos ou lado a lado), Gráficos de Barras e Tabelas Dinâmicas.
* **⏳ Histórico:** Tabela completa com todos os registros, permitindo filtragem por recência (Últimos 30 dias ou Mês específico) e deleção de entradas incorretas.
* **🏆 Classificação:** Um "Leaderboard" (Ranking) automático que calcula a média de notas dos últimos 30 dias e exibe setas de tendência (⬆️/⬇️) mostrando a evolução em relação ao mês anterior.
* **📈 Dashboard Individual:** Um painel exclusivo para cada jogador, exibindo a sua foto, métricas de crescimento por fundamento e o histórico de evolução em gráficos limpos e intuitivos.

## 🛠️ Tecnologias Utilizadas

Este projeto foi construído utilizando ferramentas modernas focadas em dados e deploy ágil:

* **[Python 3](https://www.python.org/):** Linguagem base do projeto.
* **[Streamlit](https://streamlit.io/):** Framework para a construção da interface web e roteamento das páginas.
* **[Pandas](https://pandas.pydata.org/):** Para manipulação, agregação e estruturação dos dados (criação de DataFrames dinâmicos).
* **[Plotly](https://plotly.com/python/):** Biblioteca principal para a renderização dos gráficos interativos (Radar e Barras).
* **[Turso / libSQL](https://turso.tech/):** Banco de dados relacional (SQLite) hospedado na nuvem, garantindo que os dados não se percam a cada reinício do servidor.
* **[Pillow (PIL)](https://python-pillow.org/):** Processamento e redimensionamento de imagens para conversão em Base64.

## ☁️ Como Configurar e Fazer o Deploy (Turso + Streamlit)

Para ter o seu próprio sistema rodando na nuvem gratuitamente para o seu grupo de amigos, siga os passos abaixo:

### 1. Configurar o Banco de Dados (Turso)
1. Crie uma conta gratuita no [Turso](https://turso.tech/).
2. Crie um novo banco de dados (ex: `sports-tracker`).
3. Copie a **URL do Banco** (formato `libsql://...`) e gere um **Auth Token**. Guarde essas duas informações.

### 2. Preparar o Repositório
1. Faça um *Fork* ou copie este repositório para a sua conta do GitHub.
2. Certifique-se de que o repositório está na branch `master`.

### 3. Deploy no Streamlit Community Cloud
1. Acesse o [Streamlit Share](https://share.streamlit.io/) e faça login com o seu GitHub.
2. Clique em **Create app** e selecione o seu repositório recém-criado.
3. No campo *Main file path*, certifique-se de que está apontando para `app.py` (ou `nome_do_arquivo.py`, se você o renomeou).
4. **⚠️ O Passo Mais Importante:** Antes de clicar em Deploy, clique em **Advanced settings...** (ou vá em Secrets após o deploy) e configure as suas chaves do Turso no formato TOML:
   ```toml
   TURSO_DATABASE_URL = "libsql://seu-banco.turso.io"
   TURSO_AUTH_TOKEN = "seu_token_gigante_aqui"
5. ATENÇÃO, caso seu repositório esteja privado, é necessário dar permissão especial ao Streamlit Community para acessar repositórios privados

## 📁 Estrutura do Projeto

```text
/
├── app.py                  # Arquivo principal e tela de início
├── requirements.txt        # Dependências e bibliotecas do projeto
├── README.md               # Documentação do projeto
├── pages/                  # Telas do sistema (auto-roteadas pelo Streamlit)
│   ├── 1_Perfis.py
│   ├── 2_Esportes.py
│   ├── 3_Avaliacao.py
│   ├── 4_Comparacao.py
│   ├── 5_Historico.py
│   ├── 6_Classificacao.py
│   └── 7_Dashboard.py
└── utils/                  # Scripts utilitários
    ├── db_manager.py       # Lógica de conexão e queries do banco de dados Turso
    └── charts.py           # Funções auxiliares para geração de gráficos complexos (Radar)
