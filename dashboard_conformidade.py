import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configuração da página
st.set_page_config(
    page_title="Dashboard de Conformidade e Alertas",
    page_icon="⚠️",
    layout="wide"
)

# Título principal
st.title("⚠️ Dashboard de Conformidade e Alertas")
st.markdown("### Monitoramento de Superávit e Déficit de Vagas - PROUNI e Filantropia")

# --- Função de Carregamento de Dados ---
@st.cache_data
def carregar_dados_conformidade():
    """
    Carrega os dados de conformidade de um arquivo Excel local.
    Retorna um DataFrame com as colunas necessárias para análise.
    """
    try:
        # Tentar primeiro o arquivo de exemplo, depois o arquivo principal
        try:
            df = pd.read_excel("dados_conformidade_exemplo.xlsx")
        except FileNotFoundError:
            df = pd.read_excel("dados_bolsistas.xlsx")
        
        # Verificar se as colunas necessárias existem
        colunas_necessarias = ['NOMECURSO', 'PROUNI_SOBRA_FALTA', 'FILANTROPIA_SOBRA_FALTA']
        colunas_faltantes = [col for col in colunas_necessarias if col not in df.columns]
        
        if colunas_faltantes:
            st.error(f"Colunas faltantes no arquivo: {', '.join(colunas_faltantes)}")
            return pd.DataFrame()
        
        # Limpar dados e converter para numérico
        df['PROUNI_SOBRA_FALTA'] = pd.to_numeric(df['PROUNI_SOBRA_FALTA'], errors='coerce').fillna(0)
        df['FILANTROPIA_SOBRA_FALTA'] = pd.to_numeric(df['FILANTROPIA_SOBRA_FALTA'], errors='coerce').fillna(0)
        
        # Remover linhas com nomes de curso vazios
        df = df.dropna(subset=['NOMECURSO'])
        
        return df
        
    except FileNotFoundError:
        st.error("Arquivo 'dados_bolsistas.xlsx' não encontrado. Verifique se o arquivo existe no diretório.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        return pd.DataFrame()

# --- Função para definir cores condicionais ---
def obter_cor_condicional(valor):
    """
    Retorna a cor baseada no valor:
    - Vermelho claro para valores < 0
    - Verde claro para valores > 0
    - Neutro para valores = 0
    """
    if valor < 0:
        return "#ffebee"  # Vermelho claro
    elif valor > 0:
        return "#e8f5e8"  # Verde claro
    else:
        return "#f5f5f5"  # Neutro

# --- Função para criar gráfico de barras divergente ---
def criar_grafico_divergente(df, coluna, titulo, cor_positiva="#2E8B57", cor_negativa="#DC143C"):
    """
    Cria um gráfico de barras divergente horizontal.
    """
    # Filtrar apenas valores diferentes de zero para melhor visualização
    df_filtrado = df[df[coluna] != 0].copy()
    
    if df_filtrado.empty:
        st.info(f"Todos os cursos estão em equilíbrio para {titulo}")
        return None
    
    # Ordenar por valor para melhor visualização
    df_filtrado = df_filtrado.sort_values(coluna)
    
    # Definir cores baseadas no valor
    cores = [cor_negativa if x < 0 else cor_positiva for x in df_filtrado[coluna]]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=df_filtrado['NOMECURSO'],
        x=df_filtrado[coluna],
        orientation='h',
        marker_color=cores,
        text=df_filtrado[coluna],
        textposition='outside',
        texttemplate='%{text}',
        hovertemplate='<b>%{y}</b><br>Saldo: %{x}<extra></extra>'
    ))
    
    fig.update_layout(
        title=titulo,
        xaxis_title="Saldo de Vagas",
        yaxis_title="Cursos",
        height=max(400, len(df_filtrado) * 25),
        showlegend=False,
        xaxis=dict(zeroline=True, zerolinewidth=2, zerolinecolor='black'),
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    return fig

# --- Carregamento dos Dados ---
df_original = carregar_dados_conformidade()

# ===== SIDEBAR COM LOGO E CONTROLES =====
st.sidebar.markdown("""
<div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #2E86AB 0%, #0F3460 100%); border-radius: 15px; margin-bottom: 1.5rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
    <h2 style="color: white; margin: 0; font-size: 1.4rem; font-weight: 600;">🎓 São Camilo</h2>
    <p style="color: #F18F01; margin: 0.5rem 0 0 0; font-size: 0.9rem; font-weight: 500;">Dashboard de Conformidade</p>
</div>
""", unsafe_allow_html=True)

# Tentar carregar logo
try:
    import os
    from PIL import Image
    if os.path.exists('logo.png'):
        logo = Image.open('logo.png')
        st.sidebar.image(logo, width=200)
    else:
        st.sidebar.info("📁 Coloque o arquivo 'logo.png' na pasta do projeto para exibir o logo institucional")
except Exception as e:
    st.sidebar.warning(f"⚠️ Erro ao carregar logo: {str(e)}")

# Título dos controles
st.sidebar.markdown("""
<h3 style="color: #0F3460; border-bottom: 2px solid #F18F01; padding-bottom: 0.5rem; margin-top: 1rem;">
📊 Controles do Dashboard
</h3>
""", unsafe_allow_html=True)

# Botão para atualizar dados
if st.sidebar.button("🔄 Atualizar Dados"):
    st.cache_data.clear()
    st.rerun()

# Menu de Seleção de Filial
if not df_original.empty:
    opcoes_filial = ["Todas as Filiais", "4 - São Paulo", "7 - Espírito Santo"]
    filial_selecionada = st.sidebar.selectbox(
        "🏢 Selecione a Filial:",
        opcoes_filial,
        help="Filtre os dados por filial específica"
    )
    
    # Aplicar filtro de filial
    if filial_selecionada == "Todas as Filiais":
        df = df_original.copy()
        st.sidebar.success("✅ Exibindo todas as filiais")
    else:
        codigo_filial = int(filial_selecionada.split(" - ")[0])
        if 'FILIAL' in df_original.columns:
            df = df_original[df_original['FILIAL'] == codigo_filial].copy()
        elif 'CODFILIAL' in df_original.columns:
            df = df_original[df_original['CODFILIAL'] == codigo_filial].copy()
        else:
            df = df_original.copy()
            st.sidebar.warning("⚠️ Coluna FILIAL não encontrada, exibindo todos os dados")
        
        st.sidebar.success(f"✅ Filtro aplicado: {filial_selecionada}")
    
    # Filtro por Curso
    if 'NOMECURSO' in df.columns:
        cursos_disponiveis = ["Todos os Cursos"] + sorted(df['NOMECURSO'].dropna().unique().tolist())
        curso_selecionado = st.sidebar.selectbox(
            "📚 Selecione o Curso:",
            cursos_disponiveis,
            help="Filtre os dados por curso específico"
        )
        
        if curso_selecionado != "Todos os Cursos":
            df = df[df['NOMECURSO'] == curso_selecionado].copy()
            st.sidebar.success(f"✅ Curso selecionado: {curso_selecionado}")
    
    # Filtros por Situação
    st.sidebar.markdown("---")
    st.sidebar.markdown("**🎯 Filtros por Situação:**")
    
    mostrar_apenas_deficit = st.sidebar.checkbox(
        "⚠️ Apenas cursos em déficit",
        help="Mostrar apenas cursos com saldo negativo"
    )
    
    if mostrar_apenas_deficit:
        df = df[(df['PROUNI_SOBRA_FALTA'] < 0) | (df['FILANTROPIA_SOBRA_FALTA'] < 0)].copy()
        st.sidebar.warning(f"⚠️ Mostrando apenas {len(df)} cursos em déficit")
    
    # Opções de Visualização
    st.sidebar.markdown("---")
    st.sidebar.markdown("**📊 Opções de Visualização:**")
    
    mostrar_tabela_detalhada = st.sidebar.checkbox(
        "📋 Mostrar tabela detalhada",
        value=True,
        help="Exibir tabela com todos os dados"
    )
    
    mostrar_graficos_divergentes = st.sidebar.checkbox(
        "📈 Mostrar gráficos divergentes",
        value=True,
        help="Exibir gráficos de barras divergentes"
    )
    
    # Informações do Dataset
    st.sidebar.markdown("---")
    st.sidebar.markdown("**📊 Informações do Dataset:**")
    st.sidebar.info(f"""
    **Total de registros:** {len(df)}
    **Cursos únicos:** {df['NOMECURSO'].nunique() if 'NOMECURSO' in df.columns else 'N/A'}
    **Última atualização:** {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M')}
    """)
    
else:
    df = df_original
    mostrar_tabela_detalhada = True
    mostrar_graficos_divergentes = True

# Verificar se há dados para processar
if not df.empty:
    
    # --- KPIs de Alerta no Topo ---
    st.subheader("🚨 Indicadores de Alerta")
    
    # Calcular métricas
    saldo_geral_prouni = df['PROUNI_SOBRA_FALTA'].sum()
    saldo_geral_filantropia = df['FILANTROPIA_SOBRA_FALTA'].sum()
    cursos_deficit = len(df[(df['PROUNI_SOBRA_FALTA'] < 0) | (df['FILANTROPIA_SOBRA_FALTA'] < 0)])
    
    # Criar colunas para os KPIs
    col1, col2, col3 = st.columns(3)
    
    # KPI 1: Saldo Geral PROUNI
    with col1:
        cor_fundo_prouni = obter_cor_condicional(saldo_geral_prouni)
        st.markdown(f"""
        <div style="background-color: {cor_fundo_prouni}; padding: 20px; border-radius: 10px; text-align: center;">
            <h3 style="margin: 0; color: #333;">Saldo Geral PROUNI</h3>
            <h1 style="margin: 10px 0; color: #333;">{saldo_geral_prouni:+}</h1>
        </div>
        """, unsafe_allow_html=True)
    
    # KPI 2: Saldo Geral Filantropia
    with col2:
        cor_fundo_filantropia = obter_cor_condicional(saldo_geral_filantropia)
        st.markdown(f"""
        <div style="background-color: {cor_fundo_filantropia}; padding: 20px; border-radius: 10px; text-align: center;">
            <h3 style="margin: 0; color: #333;">Saldo Geral Filantropia</h3>
            <h1 style="margin: 10px 0; color: #333;">{saldo_geral_filantropia:+}</h1>
        </div>
        """, unsafe_allow_html=True)
    
    # KPI 3: Cursos em Déficit
    with col3:
        cor_fundo_deficit = "#ffebee" if cursos_deficit > 0 else "#e8f5e8"
        st.markdown(f"""
        <div style="background-color: {cor_fundo_deficit}; padding: 20px; border-radius: 10px; text-align: center;">
            <h3 style="margin: 0; color: #333;">Cursos em Déficit</h3>
            <h1 style="margin: 10px 0; color: #333;">{cursos_deficit}</h1>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # --- Gráficos de Barras Divergentes ---
    if mostrar_graficos_divergentes:
        st.subheader("📊 Análise de Superávit e Déficit por Curso")
        
        # Gráfico PROUNI
        st.markdown("#### PROUNI - Saldo de Vagas por Curso")
        fig_prouni = criar_grafico_divergente(
            df, 
            'PROUNI_SOBRA_FALTA', 
            'Saldo de Vagas PROUNI por Curso',
            cor_positiva="#1f77b4",  # Azul
            cor_negativa="#d62728"   # Vermelho
        )
        
        if fig_prouni:
            st.plotly_chart(fig_prouni, use_container_width=True)
        
        # Gráfico Filantropia
        st.markdown("#### Filantropia - Saldo de Vagas por Curso")
        fig_filantropia = criar_grafico_divergente(
            df, 
            'FILANTROPIA_SOBRA_FALTA', 
            'Saldo de Vagas Filantropia por Curso',
            cor_positiva="#2ca02c",  # Verde
            cor_negativa="#d62728"   # Vermelho
        )
        
        if fig_filantropia:
            st.plotly_chart(fig_filantropia, use_container_width=True)
    
    st.markdown("---")
    
    # --- Tabela de Alertas Detalhada ---
    if mostrar_tabela_detalhada:
        st.subheader("📋 Tabela Detalhada de Conformidade")
        
        # Preparar dados para exibição
        df_exibicao = df[['NOMECURSO', 'PROUNI_SOBRA_FALTA', 'FILANTROPIA_SOBRA_FALTA']].copy()
        
        # Função para aplicar estilo às células
        def aplicar_estilo_celulas(val):
            """
            Aplica cor de fundo baseada no valor da célula.
            """
            if pd.isna(val) or val == 0:
                return ''
            elif val < 0:
                return 'background-color: #ffebee'  # Vermelho claro
            else:
                return 'background-color: #e8f5e8'  # Verde claro
        
        # Aplicar estilo apenas às colunas numéricas
        df_styled = df_exibicao.style.applymap(
            aplicar_estilo_celulas, 
            subset=['PROUNI_SOBRA_FALTA', 'FILANTROPIA_SOBRA_FALTA']
        )
        
        # Renomear colunas para exibição
        df_styled = df_styled.format({
            'PROUNI_SOBRA_FALTA': '{:+.0f}',
            'FILANTROPIA_SOBRA_FALTA': '{:+.0f}'
        })
        
        # Exibir tabela
        st.dataframe(
            df_styled,
            column_config={
                "NOMECURSO": "Nome do Curso",
                "PROUNI_SOBRA_FALTA": "Saldo PROUNI",
                "FILANTROPIA_SOBRA_FALTA": "Saldo Filantropia"
            },
            use_container_width=True,
            height=400
        )
    
    # --- Resumo Estatístico ---
    st.markdown("---")
    st.subheader("📈 Resumo Estatístico")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**PROUNI:**")
        st.write(f"• Cursos em superávit: {len(df[df['PROUNI_SOBRA_FALTA'] > 0])}")
        st.write(f"• Cursos em déficit: {len(df[df['PROUNI_SOBRA_FALTA'] < 0])}")
        st.write(f"• Cursos em equilíbrio: {len(df[df['PROUNI_SOBRA_FALTA'] == 0])}")
        st.write(f"• Maior superávit: {df['PROUNI_SOBRA_FALTA'].max()}")
        st.write(f"• Maior déficit: {df['PROUNI_SOBRA_FALTA'].min()}")
    
    with col2:
        st.markdown("**Filantropia:**")
        st.write(f"• Cursos em superávit: {len(df[df['FILANTROPIA_SOBRA_FALTA'] > 0])}")
        st.write(f"• Cursos em déficit: {len(df[df['FILANTROPIA_SOBRA_FALTA'] < 0])}")
        st.write(f"• Cursos em equilíbrio: {len(df[df['FILANTROPIA_SOBRA_FALTA'] == 0])}")
        st.write(f"• Maior superávit: {df['FILANTROPIA_SOBRA_FALTA'].max()}")
        st.write(f"• Maior déficit: {df['FILANTROPIA_SOBRA_FALTA'].min()}")

else:
    # Mensagem quando não há dados
    st.warning("⚠️ Nenhum dado disponível para análise. Verifique o arquivo 'dados_bolsistas.xlsx' e suas colunas.")
    st.info("""
    **Colunas necessárias no arquivo Excel:**
    - NOMECURSO
    - PROUNI_SOBRA_FALTA
    - FILANTROPIA_SOBRA_FALTA
    """)

# --- Rodapé ---
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.8em;">
    Dashboard de Conformidade e Alertas | Monitoramento de Vagas PROUNI e Filantropia
</div>
""", unsafe_allow_html=True)