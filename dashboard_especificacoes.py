import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import os

# ===== VARIÁVEIS DE CORES =====
AZUL_PRINCIPAL = '#00205B'
VERMELHO_ALERTA = '#D9534F'
VERDE_SUCESSO = '#5CB85C'
AZUL_CLARO = '#E3F2FD'
CINZA_CLARO = '#F5F5F5'
LARANJA_DESTAQUE = '#FF9800'

# ===== CONFIGURAÇÃO DA PÁGINA =====
st.set_page_config(
    page_title="Dashboard de Conformidade e Alertas",
    page_icon="⚠️",
    layout="wide"
)

# ===== FUNÇÃO DE CARREGAMENTO DE DADOS =====
@st.cache_data
def load_data():
    """
    Carrega e processa os dados de conformidade.
    """
    try:
        # Tentar carregar o arquivo principal
        if os.path.exists('dados_conformidade_exemplo.xlsx'):
            df = pd.read_excel('dados_conformidade_exemplo.xlsx')
        elif os.path.exists('dados_bolsistas.xlsx'):
            df = pd.read_excel('dados_bolsistas.xlsx')
        else:
            # Criar dados de exemplo se não houver arquivo
            df = pd.DataFrame({
                'NOMECURSO': [
                    'Medicina', 'Enfermagem', 'Fisioterapia', 'Psicologia', 
                    'Nutrição', 'Farmácia', 'Odontologia', 'Biomedicina'
                ],
                'FILIAL': [4, 4, 7, 4, 7, 4, 7, 4],
                'PROUNI_SOBRA_FALTA': [15, -8, 22, -5, 18, -12, 25, 10],
                'FILANTROPIA_SOBRA_FALTA': [-3, 12, -7, 20, -15, 8, -2, 14],
                'TOTAL_PROUNI': [100, 80, 120, 90, 110, 85, 130, 95],
                'TOTAL_FILANTROPIA': [50, 60, 70, 80, 65, 75, 85, 70]
            })
        
        # Garantir que as colunas necessárias existam
        required_columns = ['NOMECURSO', 'PROUNI_SOBRA_FALTA', 'FILANTROPIA_SOBRA_FALTA']
        for col in required_columns:
            if col not in df.columns:
                df[col] = 0
        
        # Adicionar coluna FILIAL se não existir
        if 'FILIAL' not in df.columns:
            df['FILIAL'] = 4  # Padrão São Paulo
        
        # Converter colunas numéricas
        numeric_columns = ['PROUNI_SOBRA_FALTA', 'FILANTROPIA_SOBRA_FALTA', 'FILIAL']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        
        # Remover linhas com nomes de curso vazios
        df = df.dropna(subset=['NOMECURSO'])
        df = df[df['NOMECURSO'].str.strip() != '']
        
        return df
        
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        # Retornar DataFrame vazio em caso de erro
        return pd.DataFrame(columns=['NOMECURSO', 'FILIAL', 'PROUNI_SOBRA_FALTA', 'FILANTROPIA_SOBRA_FALTA'])

# ===== CARREGAMENTO DOS DADOS =====
df_original = load_data()

# ===== MENU LATERAL (SIDEBAR) =====
st.sidebar.title("🎓 Dashboard de Conformidade")

# Logo no topo do sidebar
try:
    if os.path.exists('logo.png'):
        logo = Image.open('logo.png')
        st.sidebar.image(logo, width=200)
    else:
        st.sidebar.info("📁 Coloque o arquivo 'logo.png' na pasta do projeto")
except Exception as e:
    st.sidebar.warning(f"⚠️ Erro ao carregar logo: {str(e)}")

# Selectbox para seleção de Filial
opcoes_filial = ["Todas as Filiais", "4 - São Paulo", "7 - Espírito Santo"]
filial_selecionada = st.sidebar.selectbox(
    "🏢 Selecione a Filial:",
    opcoes_filial
)

# Checkbox para simulação de projeção
simulacao_projecao = st.sidebar.checkbox(
    "📊 Simulação de Projeção",
    help="Ativar cálculos de projeção baseados em tendências"
)

# ===== LÓGICA DE FILTRAGEM DE DADOS =====
# Filtrar DataFrame principal com base na seleção da Filial
if filial_selecionada == "Todas as Filiais":
    df_filtrado = df_original.copy()
else:
    codigo_filial = int(filial_selecionada.split(" - ")[0])
    df_filtrado = df_original[df_original['FILIAL'] == codigo_filial].copy()

# Se simulação de projeção for marcada, calcular novas colunas
if simulacao_projecao:
    # Calcular projeções (exemplo: 10% de crescimento)
    df_filtrado['PROUNI_PROJECAO'] = (df_filtrado['PROUNI_SOBRA_FALTA'] * 1.1).round().astype(int)
    df_filtrado['FILANTROPIA_PROJECAO'] = (df_filtrado['FILANTROPIA_SOBRA_FALTA'] * 1.1).round().astype(int)
    
    # Usar projeções para visualizações
    df_display = df_filtrado.copy()
    df_display['PROUNI_SOBRA_FALTA'] = df_display['PROUNI_PROJECAO']
    df_display['FILANTROPIA_SOBRA_FALTA'] = df_display['FILANTROPIA_PROJECAO']
else:
    # Usar dados originais
    df_display = df_filtrado.copy()

# ===== TÍTULO PRINCIPAL =====
st.title("⚠️ Dashboard de Conformidade e Alertas")
st.markdown("### Monitoramento de Superávit e Déficit de Vagas - PROUNI e Filantropia")

# ===== LAYOUT PRINCIPAL COM TABS =====
if not df_display.empty:
    tab1, tab2 = st.tabs(["📊 Visão Geral", "📄 Dados Detalhados"])
    
    # ===== ABA: VISÃO GERAL =====
    with tab1:
        # KPIs usando st.columns(3) e st.metric()
        st.subheader("📈 Indicadores Principais")
        
        col1, col2, col3 = st.columns(3)
        
        # Calcular métricas
        saldo_prouni = df_display['PROUNI_SOBRA_FALTA'].sum()
        saldo_filantropia = df_display['FILANTROPIA_SOBRA_FALTA'].sum()
        cursos_deficit = len(df_display[(df_display['PROUNI_SOBRA_FALTA'] < 0) | (df_display['FILANTROPIA_SOBRA_FALTA'] < 0)])
        
        with col1:
            st.metric(
                label="Saldo Geral PROUNI",
                value=f"{saldo_prouni:+}",
                delta=f"{abs(saldo_prouni)} vagas" if saldo_prouni != 0 else None
            )
        
        with col2:
            st.metric(
                label="Saldo Geral Filantropia", 
                value=f"{saldo_filantropia:+}",
                delta=f"{abs(saldo_filantropia)} vagas" if saldo_filantropia != 0 else None
            )
        
        with col3:
            st.metric(
                label="Cursos em Déficit",
                value=cursos_deficit,
                delta=f"{cursos_deficit}/{len(df_display)} cursos" if len(df_display) > 0 else None
            )
        
        st.markdown("---")
        
        # ===== GRÁFICOS DE BARRAS DIVERGENTES =====
        st.subheader("📊 Análise de Superávit e Déficit por Curso")
        
        # Gráfico PROUNI
        st.markdown("#### PROUNI - Saldo de Vagas por Curso")
        
        # Criar coluna Status para PROUNI
        df_prouni = df_display.copy()
        df_prouni['Status'] = df_prouni['PROUNI_SOBRA_FALTA'].apply(
            lambda x: 'Superávit' if x >= 0 else 'Déficit'
        )
        
        # Criar gráfico de barras horizontal com color='Status'
        fig_prouni = px.bar(
            df_prouni,
            x='PROUNI_SOBRA_FALTA',
            y='NOMECURSO',
            orientation='h',
            color='Status',
            color_discrete_map={
                'Superávit': AZUL_PRINCIPAL,
                'Déficit': VERMELHO_ALERTA
            },
            title='Saldo de Vagas PROUNI por Curso',
            labels={
                'PROUNI_SOBRA_FALTA': 'Saldo de Vagas',
                'NOMECURSO': 'Curso'
            }
        )
        
        fig_prouni.update_layout(
            height=400,
            showlegend=True,
            xaxis_title="Saldo de Vagas",
            yaxis_title="Curso"
        )
        
        st.plotly_chart(fig_prouni, use_container_width=True)
        
        # Gráfico Filantropia
        st.markdown("#### Filantropia - Saldo de Vagas por Curso")
        
        # Criar coluna Status para Filantropia
        df_filantropia = df_display.copy()
        df_filantropia['Status'] = df_filantropia['FILANTROPIA_SOBRA_FALTA'].apply(
            lambda x: 'Superávit' if x >= 0 else 'Déficit'
        )
        
        # Criar gráfico de barras horizontal com color='Status'
        fig_filantropia = px.bar(
            df_filantropia,
            x='FILANTROPIA_SOBRA_FALTA',
            y='NOMECURSO',
            orientation='h',
            color='Status',
            color_discrete_map={
                'Superávit': AZUL_PRINCIPAL,
                'Déficit': VERMELHO_ALERTA
            },
            title='Saldo de Vagas Filantropia por Curso',
            labels={
                'FILANTROPIA_SOBRA_FALTA': 'Saldo de Vagas',
                'NOMECURSO': 'Curso'
            }
        )
        
        fig_filantropia.update_layout(
            height=400,
            showlegend=True,
            xaxis_title="Saldo de Vagas",
            yaxis_title="Curso"
        )
        
        st.plotly_chart(fig_filantropia, use_container_width=True)
    
    # ===== ABA: DADOS DETALHADOS =====
    with tab2:
        st.subheader("📋 Tabela Detalhada de Conformidade")
        
        # Função de estilo separada
        def aplicar_estilo_background(val):
            """
            Retorna a cor de fundo baseada no valor da célula.
            """
            if pd.isna(val) or val == 0:
                return ''
            elif val < 0:
                return f'background-color: {VERMELHO_ALERTA}'
            else:
                return f'background-color: {VERDE_SUCESSO}'
        
        # Preparar dados para exibição
        colunas_exibicao = ['NOMECURSO', 'PROUNI_SOBRA_FALTA', 'FILANTROPIA_SOBRA_FALTA']
        if simulacao_projecao:
            colunas_exibicao.extend(['PROUNI_PROJECAO', 'FILANTROPIA_PROJECAO'])
        
        df_tabela = df_display[colunas_exibicao].copy()
        
        # Aplicar estilo usando applymap
        df_styled = df_tabela.style.applymap(
            aplicar_estilo_background,
            subset=['PROUNI_SOBRA_FALTA', 'FILANTROPIA_SOBRA_FALTA']
        )
        
        # Formatação dos valores
        format_dict = {
            'PROUNI_SOBRA_FALTA': '{:+.0f}',
            'FILANTROPIA_SOBRA_FALTA': '{:+.0f}'
        }
        
        if simulacao_projecao:
            format_dict.update({
                'PROUNI_PROJECAO': '{:+.0f}',
                'FILANTROPIA_PROJECAO': '{:+.0f}'
            })
        
        df_styled = df_styled.format(format_dict)
        
        # Exibir tabela usando st.dataframe()
        st.dataframe(
            df_styled,
            use_container_width=True,
            height=400
        )
        
        # Informações adicionais
        st.markdown("---")
        st.subheader("📊 Resumo Estatístico")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**PROUNI:**")
            st.write(f"• Total de registros: {len(df_display)}")
            st.write(f"• Cursos em superávit: {len(df_display[df_display['PROUNI_SOBRA_FALTA'] > 0])}")
            st.write(f"• Cursos em déficit: {len(df_display[df_display['PROUNI_SOBRA_FALTA'] < 0])}")
            st.write(f"• Saldo total: {df_display['PROUNI_SOBRA_FALTA'].sum():+}")
        
        with col2:
            st.markdown("**Filantropia:**")
            st.write(f"• Total de registros: {len(df_display)}")
            st.write(f"• Cursos em superávit: {len(df_display[df_display['FILANTROPIA_SOBRA_FALTA'] > 0])}")
            st.write(f"• Cursos em déficit: {len(df_display[df_display['FILANTROPIA_SOBRA_FALTA'] < 0])}")
            st.write(f"• Saldo total: {df_display['FILANTROPIA_SOBRA_FALTA'].sum():+}")

else:
    st.error("❌ Nenhum dado encontrado para exibir.")
    st.info("""
    **Instruções:**
    1. Coloque o arquivo Excel na pasta do projeto
    2. Certifique-se de que o arquivo contém as colunas: NOMECURSO, PROUNI_SOBRA_FALTA, FILANTROPIA_SOBRA_FALTA
    3. Clique em 'Atualizar' no menu lateral
    """)

# ===== RODAPÉ =====
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; font-size: 0.8em;'>"
    "Dashboard de Conformidade e Alertas | Monitoramento de Vagas PROUNI e Filantropia"
    "</div>",
    unsafe_allow_html=True
)