import streamlit as st
import pandas as pd
import requests
import plotly.express as px

# --- Configurações da Página ---
st.set_page_config(layout="wide")

# --- Título Principal ---
st.title("📊 Dashboard de Alunos Bolsistas")

# --- Funções de Carregamento de Dados ---

@st.cache_data
def buscar_dados_excel():
    """
    Carrega os dados de um arquivo Excel local.
    Este é o modo de desenvolvimento.
    """
    try:
        df = pd.read_excel("dados_bolsistas.xlsx")
        return df
    except FileNotFoundError:
        st.error("Arquivo 'dados_bolsistas.xlsx' não encontrado. Crie o arquivo ou altere para o modo de produção.")
        return pd.DataFrame()

@st.cache_data
def buscar_dados_api():
    """
    Busca os dados de um endpoint de API REST.
    Este é o modo de produção.
    """
    API_URL = "https://api.example.com/dados_bolsistas"  # Substitua pela sua URL real
    try:
        response = requests.get(API_URL)
        response.raise_for_status()  # Lança um erro para respostas com código de status ruim (4xx ou 5xx)
        data = response.json()
        df = pd.DataFrame(data)
        return df
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao buscar dados da API: {e}")
        return pd.DataFrame()

# --- Carregamento dos Dados ---

# Para usar os dados da API, comente a linha abaixo e descomente a próxima.
df = buscar_dados_excel()
# df = buscar_dados_api()

# --- Renderização do Dashboard ---

if not df.empty:
    # --- KPIs (Metric Cards) ---
    total_matriculados = df['TOTAL_MATRICULADOS'].sum()
    total_bolsistas = df['TOTAL_INSTITUCIONAL'].sum()

    col1, col2 = st.columns(2)
    col1.metric("Total de Alunos Matriculados", f"{total_matriculados:,}".replace(",", "."))
    col2.metric("Total de Bolsistas Institucionais", f"{total_bolsistas:,}".replace(",", "."))

    st.markdown("---")

    # --- Gráfico de Barras Interativo ---
    st.subheader("Total de Alunos Matriculados por Curso")
    fig = px.bar(
        df,
        x='NOMECURSO',
        y='TOTAL_MATRICULADOS',
        title="Matriculados por Curso",
        labels={'NOMECURSO': 'Curso', 'TOTAL_MATRICULADOS': 'Total de Matriculados'},
        text_auto=True
    )
    fig.update_layout(xaxis={'categoryorder':'total descending'})
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # --- Tabela de Dados Completa ---
    st.subheader("Dados Completos")
    st.dataframe(df)
else:
    st.warning("Nenhum dado para exibir. Verifique a fonte de dados.")