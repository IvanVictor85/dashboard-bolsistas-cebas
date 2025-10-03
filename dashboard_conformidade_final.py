"""
Dashboard de Conformidade e Alertas - Centro Universitário São Camilo
Sistema de Monitoramento de Bolsas PROUNI e Filantropia

Autor: Sistema de Gestão Acadêmica
Data: 2024
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import os

# ===== CONFIGURAÇÃO DA PÁGINA =====
st.set_page_config(
    page_title="Dashboard Conformidade - São Camilo",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== PALETA DE CORES INSTITUCIONAL =====
AZUL_PRINCIPAL = '#2E86AB'  # Azul mais suave
AZUL_ESCURO = '#0F3460'     # Para títulos principais
LARANJA_DESTAQUE = '#F18F01'  # Laranja mais vibrante
VERMELHO_ALERTA = '#C73E1D'   # Vermelho mais suave
VERDE_POSITIVO = '#4CAF50'    # Verde material design
BRANCO = '#FFFFFF'
CINZA_CLARO = '#F5F7FA'       # Cinza mais claro
CINZA_MEDIO = '#E8EEF5'       # Para contraste suave

# ===== FUNÇÕES DE CARREGAMENTO DE DADOS =====
@st.cache_data
def carregar_dados():
    """
    Carrega os dados do arquivo Excel com cache para otimização de performance
    """
    try:
        df = pd.read_excel('dados_bolsistas.xlsx')
        return df
    except FileNotFoundError:
        st.error("❌ Arquivo 'dados_bolsistas.xlsx' não encontrado!")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {str(e)}")
        return pd.DataFrame()

def aplicar_projecao(df, simular=False):
    """
    Aplica projeção considerando formandos se a simulação estiver ativada
    """
    if not simular or df.empty:
        return df
    
    df_projecao = df.copy()
    
    # Simular redução por formandos (10% PROUNI, 15% Filantropia)
    if 'TOTAL_PROUNI' in df_projecao.columns:
        df_projecao['TOTAL_PROUNI'] = df_projecao['TOTAL_PROUNI'] * 0.9
    
    if 'TOTAL_INSTITUCIONAL' in df_projecao.columns:
        df_projecao['TOTAL_INSTITUCIONAL'] = df_projecao['TOTAL_INSTITUCIONAL'] * 0.85
    
    return df_projecao

def calcular_saldos_conformidade(df):
    """
    Calcula os saldos de conformidade para PROUNI e Filantropia
    """
    if df.empty:
        return pd.DataFrame()
    
    # Simular colunas de saldo (adapte conforme sua estrutura real)
    df_saldos = df.copy()
    
    # Se não existirem as colunas de saldo, criar simulação baseada nos dados existentes
    if 'PROUNI_SOBRA_FALTA' not in df_saldos.columns:
        if 'TOTAL_PROUNI' in df_saldos.columns:
            # Simular saldos baseados nos totais (exemplo: meta vs realizado)
            # Tratar valores NaN antes da conversão
            valores_prouni = df_saldos['TOTAL_PROUNI'].fillna(0) * 0.1 - 50
            df_saldos['PROUNI_SOBRA_FALTA'] = valores_prouni.round().astype(int)
        else:
            df_saldos['PROUNI_SOBRA_FALTA'] = 0
    
    if 'FILANTROPIA_SOBRA_FALTA' not in df_saldos.columns:
        if 'TOTAL_INSTITUCIONAL' in df_saldos.columns:
            # Simular saldos baseados nos totais
            # Tratar valores NaN antes da conversão
            valores_filantropia = df_saldos['TOTAL_INSTITUCIONAL'].fillna(0) * 0.05 - 30
            df_saldos['FILANTROPIA_SOBRA_FALTA'] = valores_filantropia.round().astype(int)
        else:
            df_saldos['FILANTROPIA_SOBRA_FALTA'] = 0
    
    # Garantir que não há valores NaN nas colunas de saldo
    df_saldos['PROUNI_SOBRA_FALTA'] = df_saldos['PROUNI_SOBRA_FALTA'].fillna(0).astype(int)
    df_saldos['FILANTROPIA_SOBRA_FALTA'] = df_saldos['FILANTROPIA_SOBRA_FALTA'].fillna(0).astype(int)
    
    return df_saldos

# ===== FUNÇÕES DE VISUALIZAÇÃO =====
def criar_kpi_colorido(titulo, valor, cor_fundo):
    """
    Cria um KPI com cor de fundo personalizada
    """
    return f"""
    <div style="
        background-color: {cor_fundo};
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    ">
        <h3 style="color: {BRANCO}; margin: 0; font-size: 1.1rem;">{titulo}</h3>
        <h1 style="color: {BRANCO}; margin: 0.5rem 0; font-size: 2.5rem;">{valor:+d}</h1>
    </div>
    """

def criar_grafico_divergente(df, coluna_saldo, titulo, cor_positiva=AZUL_PRINCIPAL, cor_negativa=VERMELHO_ALERTA):
    """
    Cria gráfico de barras divergente com cores personalizadas
    """
    if df.empty or coluna_saldo not in df.columns:
        return go.Figure()
    
    df_sorted = df.sort_values(coluna_saldo)
    
    # Definir cores baseadas no valor
    cores = [cor_positiva if x >= 0 else cor_negativa for x in df_sorted[coluna_saldo]]
    
    fig = go.Figure(data=[
        go.Bar(
            y=df_sorted['NOMECURSO'] if 'NOMECURSO' in df_sorted.columns else df_sorted.index,
            x=df_sorted[coluna_saldo],
            orientation='h',
            marker_color=cores,
            text=df_sorted[coluna_saldo],
            textposition='outside',
            textfont=dict(size=11, color=AZUL_PRINCIPAL),
            hovertemplate='<b>%{y}</b><br>' +
                         f'{titulo}: %{{x}}<br>' +
                         'Total Matriculados: %{customdata}<br>' +
                         '<extra></extra>',
            customdata=df_sorted['TOTAL_MATRICULADOS'] if 'TOTAL_MATRICULADOS' in df_sorted.columns else [0]*len(df_sorted)
        )
    ])
    
    fig.update_layout(
        title={
            'text': titulo,
            'x': 0.5,
            'font': {'size': 16, 'color': AZUL_PRINCIPAL}
        },
        xaxis_title="Saldo (Positivo = Sobra, Negativo = Falta)",
        yaxis_title="Cursos",
        height=max(400, len(df_sorted) * 30),
        showlegend=False,
        plot_bgcolor=CINZA_CLARO,
        paper_bgcolor=BRANCO,
        font=dict(color=AZUL_PRINCIPAL)
    )
    
    # Linha vertical no zero
    fig.add_vline(x=0, line_width=2, line_dash="dash", line_color=AZUL_PRINCIPAL)
    
    return fig

def aplicar_estilo_tabela(df, colunas_saldo):
    """
    Aplica estilo colorido às colunas de saldo na tabela
    """
    def colorir_saldo(val):
        if pd.isna(val):
            return ''
        if val > 0:
            return f'background-color: {VERDE_POSITIVO}; color: {BRANCO}; font-weight: bold;'
        elif val < 0:
            return f'background-color: {VERMELHO_ALERTA}; color: {BRANCO}; font-weight: bold;'
        else:
            return f'background-color: {AZUL_PRINCIPAL}; color: {BRANCO}; font-weight: bold;'
    
    styled_df = df.style
    for coluna in colunas_saldo:
        if coluna in df.columns:
            styled_df = styled_df.applymap(colorir_saldo, subset=[coluna])
    
    return styled_df

# ===== SIDEBAR COM LOGO E CONTROLES =====
st.sidebar.markdown(f"""
<div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, {AZUL_PRINCIPAL} 0%, {AZUL_ESCURO} 100%); border-radius: 15px; margin-bottom: 1.5rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
    <h2 style="color: {BRANCO}; margin: 0; font-size: 1.4rem; font-weight: 600;">🎓 São Camilo</h2>
    <p style="color: {LARANJA_DESTAQUE}; margin: 0.5rem 0 0 0; font-size: 0.9rem; font-weight: 500;">Dashboard de Conformidade</p>
</div>
""", unsafe_allow_html=True)

# Tentar carregar logo
try:
    if os.path.exists('logo.png'):
        logo = Image.open('logo.png')
        st.sidebar.image(logo, width=200)
    else:
        st.sidebar.info("📁 Coloque o arquivo 'logo.png' na pasta do projeto para exibir o logo institucional")
except Exception as e:
    st.sidebar.warning(f"⚠️ Erro ao carregar logo: {str(e)}")

# Título dos controles
st.sidebar.markdown(f"""
<h3 style="color: {AZUL_ESCURO}; border-bottom: 2px solid {LARANJA_DESTAQUE}; padding-bottom: 0.5rem; margin-top: 1rem;">
📊 Controles do Dashboard
</h3>
""", unsafe_allow_html=True)

# ===== CARREGAMENTO E FILTRAGEM DE DADOS =====
df_original = carregar_dados()

if not df_original.empty:
    # Menu de Seleção de Filial
    opcoes_filial = ["Todas as Filiais", "4 - São Paulo", "7 - Espírito Santo"]
    filial_selecionada = st.sidebar.selectbox(
        "🏢 Selecione a Filial:",
        opcoes_filial,
        help="Filtre os dados por filial específica"
    )
    
    # Aplicar filtro de filial
    if filial_selecionada == "Todas as Filiais":
        df_filtrado = df_original.copy()
        st.sidebar.success("✅ Exibindo todas as filiais")
    else:
        codigo_filial = int(filial_selecionada.split(" - ")[0])
        if 'FILIAL' in df_original.columns:
            df_filtrado = df_original[df_original['FILIAL'] == codigo_filial].copy()
        elif 'CODFILIAL' in df_original.columns:
            df_filtrado = df_original[df_original['CODFILIAL'] == codigo_filial].copy()
        else:
            df_filtrado = df_original.copy()
            st.sidebar.warning("⚠️ Coluna FILIAL não encontrada, exibindo todos os dados")
        
        st.sidebar.success(f"✅ Filtro aplicado: {filial_selecionada}")
    
    # Checkbox de simulação
    simular_projecao = st.sidebar.checkbox(
        "🔮 Simular Projeção para o Próximo Semestre (com formandos)",
        help="Considera 10% de formandos PROUNI e 15% de Filantropia"
    )
    
    if simular_projecao:
        st.sidebar.info("📈 Projeção ativada: -10% PROUNI, -15% Filantropia")
    
    # Aplicar projeção se necessário
    df_final = aplicar_projecao(df_filtrado, simular_projecao)
    
    # Calcular saldos de conformidade
    df_conformidade = calcular_saldos_conformidade(df_final)
    
    # ===== CABEÇALHO PRINCIPAL =====
    st.markdown(f"""
    <div style="text-align: center; padding: 2.5rem; background: linear-gradient(135deg, {AZUL_ESCURO} 0%, {AZUL_PRINCIPAL} 50%, {LARANJA_DESTAQUE} 100%); border-radius: 20px; margin-bottom: 2rem; box-shadow: 0 8px 16px rgba(0,0,0,0.1);">
        <h1 style="color: {BRANCO}; margin: 0; font-size: 2.5rem; font-weight: 700; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">🚨 Dashboard de Conformidade e Alertas</h1>
        <p style="color: {BRANCO}; margin: 0.5rem 0 0 0; font-size: 1.2rem; font-weight: 400; opacity: 0.95;">Sistema de Monitoramento de Bolsas PROUNI e Filantropia</p>
    </div>
    """, unsafe_allow_html=True)
    
    # ===== ABAS PRINCIPAIS =====
    tab1, tab2 = st.tabs(["📊 Visão Geral", "📋 Dados Detalhados"])
    
    with tab1:
        # ===== KPIs DE ALERTA =====
        st.markdown(f"<h2 style='color: {AZUL_ESCURO}; margin-bottom: 1.5rem;'>🚨 Indicadores de Conformidade</h2>", unsafe_allow_html=True)
        
        if not df_conformidade.empty:
            # Calcular KPIs
            saldo_prouni = df_conformidade['PROUNI_SOBRA_FALTA'].sum()
            saldo_filantropia = df_conformidade['FILANTROPIA_SOBRA_FALTA'].sum()
            cursos_deficit = len(df_conformidade[
                (df_conformidade['PROUNI_SOBRA_FALTA'] < 0) | 
                (df_conformidade['FILANTROPIA_SOBRA_FALTA'] < 0)
            ])
            
            # Exibir KPIs
            col1, col2, col3 = st.columns(3)
            
            with col1:
                cor_prouni = VERDE_POSITIVO if saldo_prouni >= 0 else VERMELHO_ALERTA
                st.markdown(criar_kpi_colorido("Saldo Geral PROUNI", saldo_prouni, cor_prouni), unsafe_allow_html=True)
            
            with col2:
                cor_filantropia = VERDE_POSITIVO if saldo_filantropia >= 0 else VERMELHO_ALERTA
                st.markdown(criar_kpi_colorido("Saldo Geral Filantropia", saldo_filantropia, cor_filantropia), unsafe_allow_html=True)
            
            with col3:
                cor_deficit = VERMELHO_ALERTA if cursos_deficit > 0 else VERDE_POSITIVO
                st.markdown(criar_kpi_colorido("Cursos em Déficit", cursos_deficit, cor_deficit), unsafe_allow_html=True)
            
            st.markdown("---")
            
            # ===== GRÁFICOS DIVERGENTES =====
            st.markdown(f"<h2 style='color: {AZUL_ESCURO}; margin-top: 2rem; margin-bottom: 1.5rem;'>📈 Análise por Curso</h2>", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_prouni = criar_grafico_divergente(
                    df_conformidade, 
                    'PROUNI_SOBRA_FALTA', 
                    "📊 Saldo PROUNI por Curso"
                )
                st.plotly_chart(fig_prouni, use_container_width=True)
            
            with col2:
                fig_filantropia = criar_grafico_divergente(
                    df_conformidade, 
                    'FILANTROPIA_SOBRA_FALTA', 
                    "📊 Saldo Filantropia por Curso"
                )
                st.plotly_chart(fig_filantropia, use_container_width=True)
        
        else:
            st.warning("⚠️ Não há dados de conformidade para exibir.")
    
    with tab2:
        # ===== TABELA DE ALERTAS =====
        st.markdown(f"<h2 style='color: {AZUL_ESCURO}; margin-bottom: 1.5rem;'>📋 Tabela Detalhada de Conformidade</h2>", unsafe_allow_html=True)
        
        if not df_conformidade.empty:
            # Preparar dados para exibição
            colunas_exibir = ['NOMECURSO', 'PROUNI_SOBRA_FALTA', 'FILANTROPIA_SOBRA_FALTA']
            if 'TOTAL_MATRICULADOS' in df_conformidade.columns:
                colunas_exibir.insert(1, 'TOTAL_MATRICULADOS')
            
            df_tabela = df_conformidade[colunas_exibir].copy()
            
            # Renomear colunas para exibição
            df_tabela.columns = [
                'Curso',
                'Total Matriculados' if 'TOTAL_MATRICULADOS' in colunas_exibir else None,
                'Saldo PROUNI',
                'Saldo Filantropia'
            ]
            df_tabela = df_tabela.dropna(axis=1)
            
            # Aplicar estilo
            colunas_saldo = ['Saldo PROUNI', 'Saldo Filantropia']
            df_styled = aplicar_estilo_tabela(df_tabela, colunas_saldo)
            
            # Exibir tabela
            st.dataframe(df_styled, use_container_width=True)
            
            # ===== RESUMO ESTATÍSTICO =====
            st.markdown("---")
            st.markdown(f"<h3 style='color: {AZUL_ESCURO}; margin-top: 2rem; margin-bottom: 1.5rem;'>📈 Resumo Estatístico</h3>", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                <div style="background-color: {CINZA_CLARO}; padding: 1.5rem; border-radius: 15px; border-left: 5px solid {AZUL_PRINCIPAL}; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h4 style="color: {AZUL_ESCURO}; margin-top: 0; font-weight: 600;">📊 PROUNI</h4>
                    <p style="color: {AZUL_ESCURO}; margin: 0.5rem 0;"><strong>Sobra Total:</strong> {df_conformidade[df_conformidade['PROUNI_SOBRA_FALTA'] > 0]['PROUNI_SOBRA_FALTA'].sum()}</p>
                    <p style="color: {AZUL_ESCURO}; margin: 0.5rem 0;"><strong>Falta Total:</strong> {abs(df_conformidade[df_conformidade['PROUNI_SOBRA_FALTA'] < 0]['PROUNI_SOBRA_FALTA'].sum())}</p>
                    <p style="color: {AZUL_ESCURO}; margin: 0.5rem 0;"><strong>Cursos com Sobra:</strong> {len(df_conformidade[df_conformidade['PROUNI_SOBRA_FALTA'] > 0])}</p>
                    <p style="color: {AZUL_ESCURO}; margin: 0.5rem 0;"><strong>Cursos com Falta:</strong> {len(df_conformidade[df_conformidade['PROUNI_SOBRA_FALTA'] < 0])}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div style="background-color: {CINZA_CLARO}; padding: 1.5rem; border-radius: 15px; border-left: 5px solid {LARANJA_DESTAQUE}; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h4 style="color: {AZUL_ESCURO}; margin-top: 0; font-weight: 600;">📊 Filantropia</h4>
                    <p style="color: {AZUL_ESCURO}; margin: 0.5rem 0;"><strong>Sobra Total:</strong> {df_conformidade[df_conformidade['FILANTROPIA_SOBRA_FALTA'] > 0]['FILANTROPIA_SOBRA_FALTA'].sum()}</p>
                    <p style="color: {AZUL_ESCURO}; margin: 0.5rem 0;"><strong>Falta Total:</strong> {abs(df_conformidade[df_conformidade['FILANTROPIA_SOBRA_FALTA'] < 0]['FILANTROPIA_SOBRA_FALTA'].sum())}</p>
                    <p style="color: {AZUL_ESCURO}; margin: 0.5rem 0;"><strong>Cursos com Sobra:</strong> {len(df_conformidade[df_conformidade['FILANTROPIA_SOBRA_FALTA'] > 0])}</p>
                    <p style="color: {AZUL_ESCURO}; margin: 0.5rem 0;"><strong>Cursos com Falta:</strong> {len(df_conformidade[df_conformidade['FILANTROPIA_SOBRA_FALTA'] < 0])}</p>
                </div>
                """, unsafe_allow_html=True)
        
        else:
            st.warning("⚠️ Não há dados detalhados para exibir.")

else:
    # ===== ESTADO SEM DADOS =====
    st.markdown(f"""
    <div style="text-align: center; padding: 3rem; background-color: {CINZA_CLARO}; border-radius: 15px;">
        <h2 style="color: {VERMELHO_ALERTA};">❌ Dados não encontrados</h2>
        <p style="color: {AZUL_PRINCIPAL}; font-size: 1.1rem;">
            Certifique-se de que o arquivo <strong>'dados_bolsistas.xlsx'</strong> está na pasta do projeto.
        </p>
    </div>
    """, unsafe_allow_html=True)

# ===== RODAPÉ =====
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; padding: 1.5rem; color: {AZUL_ESCURO}; font-size: 0.9rem; background-color: {CINZA_CLARO}; border-radius: 10px; margin-top: 2rem;">
    <p style="margin: 0.5rem 0; font-weight: 600;">🎓 <strong>Centro Universitário São Camilo</strong> | Dashboard de Conformidade e Alertas</p>
    <p style="margin: 0.5rem 0; opacity: 0.8;">Sistema de Monitoramento de Bolsas PROUNI e Filantropia</p>
</div>
""", unsafe_allow_html=True)