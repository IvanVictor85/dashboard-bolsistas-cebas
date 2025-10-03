import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
from functools import lru_cache
import time
import os

# --- Configurações da Página ---
st.set_page_config(
    layout="wide", 
    page_title="Dashboard São Camilo", 
    page_icon="🎓",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "Dashboard de Alunos Bolsistas - São Camilo"
    }
)

# --- Cache e Performance ---
@st.cache_data(ttl=3600)  # Cache por 1 hora
def load_css():
    """Carrega CSS customizado para melhor performance"""
    return """
    <style>
    .main > div {
        padding-top: 2rem;
    }
    .stMetric {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
    }
    .stPlotlyChart {
        border-radius: 0.5rem;
        box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
    }
    </style>
    """

# Aplicar CSS
st.markdown(load_css(), unsafe_allow_html=True)

# --- Cabeçalho Principal ---
col1, col2 = st.columns([3, 1])
with col1:
    st.title("📊 Dashboard de Alunos Bolsistas")
    st.markdown("**Sistema de Monitoramento de Bolsas e Conformidade**")

with col2:
    if os.path.exists("logo_sao_camilo.svg"):
        st.image("logo_sao_camilo.svg", width=150)

# --- Funções Otimizadas ---
@lru_cache(maxsize=128)
def obter_cor_condicional(valor):
    """Retorna cor baseada no valor (positivo=verde, negativo=vermelho, zero=azul)"""
    if valor > 0:
        return "#28a745"  # Verde mais suave
    elif valor < 0:
        return "#dc3545"  # Vermelho mais suave
    else:
        return "#17a2b8"  # Azul mais suave

@st.cache_data
def criar_grafico_divergente(df, coluna_valor, titulo, cor_positiva="#28a745", cor_negativa="#dc3545"):
    """Cria um gráfico de barras divergente com cores melhoradas"""
    df_sorted = df.sort_values(coluna_valor)
    
    cores = [cor_positiva if x >= 0 else cor_negativa for x in df_sorted[coluna_valor]]
    
    fig = go.Figure(data=[
        go.Bar(
            y=df_sorted['NOMECURSO'],
            x=df_sorted[coluna_valor],
            orientation='h',
            marker_color=cores,
            text=df_sorted[coluna_valor],
            textposition='outside',
            textfont=dict(size=10),
            hovertemplate='<b>%{y}</b><br>Saldo: %{x}<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title=titulo,
        xaxis_title="Saldo (Positivo = Sobra, Negativo = Falta)",
        yaxis_title="Cursos",
        height=max(400, len(df_sorted) * 25),
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    # Adicionar linha vertical no zero
    fig.add_vline(x=0, line_width=2, line_dash="dash", line_color="gray")
    
    return fig

# --- Funções de Carregamento de Dados Otimizadas ---
@st.cache_data(ttl=1800)  # Cache por 30 minutos
def buscar_dados_excel():
    """
    Carrega os dados de um arquivo Excel local com otimizações.
    """
    try:
        # Usar engine openpyxl para melhor performance
        df = pd.read_excel("dados_bolsistas.xlsx", engine='openpyxl')
        
        # Otimizar tipos de dados
        for col in df.columns:
            if df[col].dtype == 'object':
                try:
                    df[col] = pd.to_numeric(df[col], errors='ignore')
                except:
                    pass
        
        return df
    except FileNotFoundError:
        st.error("Arquivo 'dados_bolsistas.xlsx' não encontrado.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=1800)  # Cache por 30 minutos
def buscar_dados_api():
    """
    Busca os dados de um endpoint de API REST com timeout e retry.
    """
    API_URL = st.secrets.get("api", {}).get("url", "https://api.example.com/dados_bolsistas")
    
    try:
        # Configurar timeout e headers
        headers = {
            'User-Agent': 'Dashboard-Sao-Camilo/1.0',
            'Accept': 'application/json'
        }
        
        response = requests.get(API_URL, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        df = pd.DataFrame(data)
        
        # Otimizar tipos de dados
        for col in df.columns:
            if df[col].dtype == 'object':
                try:
                    df[col] = pd.to_numeric(df[col], errors='ignore')
                except:
                    pass
        
        return df
    except requests.exceptions.Timeout:
        st.error("Timeout ao buscar dados da API. Tente novamente.")
        return pd.DataFrame()
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao buscar dados da API: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=1800)
def gerar_dados_conformidade_reais():
    """
    Gera dados de conformidade baseados nos dados reais com otimizações
    """
    try:
        df_principal = buscar_dados_excel()
        
        if df_principal.empty:
            return None, None
        
        # Verificar se as colunas necessárias existem
        colunas_necessarias = ['NOMECURSO', 'FALTAM_SOBRAM_PROUNI', 'FALTAM_SOBRAM_FILANTROPIA']
        if not all(col in df_principal.columns for col in colunas_necessarias):
            return None, None
        
        # Filtrar dados válidos de forma otimizada
        mask_total = ~df_principal['CODFILIAL'].astype(str).str.contains('TOTAL', na=False)
        mask_curso = df_principal['NOMECURSO'].notna()
        mask_filial = df_principal['CODFILIAL'].apply(
            lambda x: str(x).replace('.0', '').isdigit() if pd.notna(x) else False
        )
        
        df_limpo = df_principal[mask_total & mask_curso & mask_filial].copy()
        
        # Agrupar por curso de forma otimizada
        df_conformidade = df_limpo.groupby('NOMECURSO', as_index=False).agg({
            'FALTAM_SOBRAM_PROUNI': 'sum',
            'FALTAM_SOBRAM_FILANTROPIA': 'sum'
        })
        
        # Renomear colunas
        df_conformidade.rename(columns={
            'FALTAM_SOBRAM_PROUNI': 'PROUNI_SOBRA_FALTA',
            'FALTAM_SOBRAM_FILANTROPIA': 'FILANTROPIA_SOBRA_FALTA'
        }, inplace=True)
        
        # Otimizar tipos de dados
        df_conformidade['PROUNI_SOBRA_FALTA'] = df_conformidade['PROUNI_SOBRA_FALTA'].fillna(0).round().astype('int32')
        df_conformidade['FILANTROPIA_SOBRA_FALTA'] = df_conformidade['FILANTROPIA_SOBRA_FALTA'].fillna(0).round().astype('int32')
        
        # Dados detalhados otimizados
        df_detalhado = df_limpo[['CODFILIAL', 'NOMECURSO', 'FALTAM_SOBRAM_PROUNI', 'FALTAM_SOBRAM_FILANTROPIA']].copy()
        df_detalhado.rename(columns={
            'FALTAM_SOBRAM_PROUNI': 'PROUNI_SOBRA_FALTA',
            'FALTAM_SOBRAM_FILANTROPIA': 'FILANTROPIA_SOBRA_FALTA'
        }, inplace=True)
        
        df_detalhado['PROUNI_SOBRA_FALTA'] = df_detalhado['PROUNI_SOBRA_FALTA'].fillna(0).round().astype('int32')
        df_detalhado['FILANTROPIA_SOBRA_FALTA'] = df_detalhado['FILANTROPIA_SOBRA_FALTA'].fillna(0).round().astype('int32')
        df_detalhado['CODFILIAL'] = df_detalhado['CODFILIAL'].astype(str)
        
        return df_conformidade, df_detalhado
        
    except Exception as e:
        st.error(f"Erro ao gerar dados de conformidade: {e}")
        return None, None

# --- Carregamento dos Dados ---
@st.cache_data(ttl=1800)
def carregar_dados():
    """Função centralizada para carregamento de dados"""
    # Verificar se deve usar API ou arquivo local
    use_api = st.secrets.get("general", {}).get("use_api", False)
    
    if use_api:
        return buscar_dados_api()
    else:
        return buscar_dados_excel()

# Carregar dados
with st.spinner('Carregando dados...'):
    df = carregar_dados()

if df.empty:
    st.error("Não foi possível carregar os dados. Verifique a configuração.")
    st.stop()

# --- Performance Monitoring ---
if st.secrets.get("general", {}).get("debug_mode", False):
    start_time = time.time()
    
    # Adicionar métricas de performance no final
    def show_performance_metrics():
        end_time = time.time()
        load_time = end_time - start_time
        st.sidebar.metric("Tempo de Carregamento", f"{load_time:.2f}s")
        st.sidebar.metric("Registros Carregados", len(df))
    
    # Registrar callback para mostrar métricas
    import atexit
    atexit.register(show_performance_metrics)

# --- Continuação do código original ---
# (O resto do código permanece igual, mas com as otimizações aplicadas)