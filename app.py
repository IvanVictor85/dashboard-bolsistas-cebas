import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go

# --- Configurações da Página ---
st.set_page_config(layout="wide", page_title="Dashboard São Camilo", page_icon="🎓")

# Cabeçalho Principal
st.title("📊 Dashboard de Alunos Bolsistas")
st.markdown("**Sistema de Monitoramento de Bolsas e Conformidade**")

# Função para obter cor condicional melhorada
def obter_cor_condicional(valor):
    """Retorna cor baseada no valor (positivo=verde, negativo=vermelho, zero=azul)"""
    if valor > 0:
        return "#28a745"  # Verde mais suave
    elif valor < 0:
        return "#dc3545"  # Vermelho mais suave
    else:
        return "#17a2b8"  # Azul mais suave

# Função para criar gráfico divergente melhorado
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
            textfont=dict(size=10)
        )
    ])
    
    fig.update_layout(
        title=titulo,
        xaxis_title="Saldo (Positivo = Sobra, Negativo = Falta)",
        yaxis_title="Cursos",
        height=max(400, len(df_sorted) * 25),
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    # Adicionar linha vertical no zero
    fig.add_vline(x=0, line_width=2, line_dash="dash", line_color="gray")
    
    return fig

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

@st.cache_data
def gerar_dados_conformidade_reais():
    """
    Gera dados de conformidade baseados nos dados reais do arquivo principal
    """
    try:
        df_principal = pd.read_excel('dados_bolsistas.xlsx')
        
        # Verificar se as colunas necessárias existem
        colunas_necessarias = ['NOMECURSO', 'FALTAM_SOBRAM_PROUNI', 'FALTAM_SOBRAM_FILANTROPIA']
        if not all(col in df_principal.columns for col in colunas_necessarias):
            return None
        
        # Filtrar dados válidos (remover totais e linhas vazias)
        df_limpo = df_principal[~df_principal['CODFILIAL'].astype(str).str.contains('TOTAL', na=False)]
        df_limpo = df_limpo.dropna(subset=['NOMECURSO'])
        
        # Filtrar apenas linhas com CODFILIAL numérico válido
        df_limpo = df_limpo[df_limpo['CODFILIAL'].apply(lambda x: str(x).replace('.0', '').isdigit() if pd.notna(x) else False)]
        
        # Agrupar por curso (somar dados de todas as filiais)
        df_conformidade = df_limpo.groupby('NOMECURSO').agg({
            'FALTAM_SOBRAM_PROUNI': 'sum',
            'FALTAM_SOBRAM_FILANTROPIA': 'sum'
        }).reset_index()
        
        # Renomear colunas para manter compatibilidade
        df_conformidade = df_conformidade.rename(columns={
            'FALTAM_SOBRAM_PROUNI': 'PROUNI_SOBRA_FALTA',
            'FALTAM_SOBRAM_FILANTROPIA': 'FILANTROPIA_SOBRA_FALTA'
        })
        
        # Converter para inteiros para remover casas decimais desnecessárias
        df_conformidade['PROUNI_SOBRA_FALTA'] = df_conformidade['PROUNI_SOBRA_FALTA'].fillna(0).round().astype(int)
        df_conformidade['FILANTROPIA_SOBRA_FALTA'] = df_conformidade['FILANTROPIA_SOBRA_FALTA'].fillna(0).round().astype(int)
        
        # Adicionar informações de filial se necessário
        df_detalhado = df_limpo[['CODFILIAL', 'NOMECURSO', 'FALTAM_SOBRAM_PROUNI', 'FALTAM_SOBRAM_FILANTROPIA']].copy()
        df_detalhado = df_detalhado.rename(columns={
            'FALTAM_SOBRAM_PROUNI': 'PROUNI_SOBRA_FALTA',
            'FALTAM_SOBRAM_FILANTROPIA': 'FILANTROPIA_SOBRA_FALTA'
        })
        
        # Converter para inteiros e garantir que CODFILIAL seja string para evitar problemas de conversão Arrow
        df_detalhado['PROUNI_SOBRA_FALTA'] = df_detalhado['PROUNI_SOBRA_FALTA'].fillna(0).round().astype(int)
        df_detalhado['FILANTROPIA_SOBRA_FALTA'] = df_detalhado['FILANTROPIA_SOBRA_FALTA'].fillna(0).round().astype(int)
        df_detalhado['CODFILIAL'] = df_detalhado['CODFILIAL'].astype(str)
        
        return df_conformidade, df_detalhado
        
    except Exception as e:
        st.error(f"Erro ao gerar dados de conformidade: {e}")
        return None

# --- Carregamento dos Dados ---

# Para usar os dados da API, comente a linha abaixo e descomente a próxima.
df = buscar_dados_excel()
# df = buscar_dados_api()

# --- Sidebar ---
# Logo na Sidebar
try:
    st.sidebar.image('logo.png', width=200)
    st.sidebar.markdown("---")
except:
    st.sidebar.markdown("**Centro Universitário São Camilo**")
    st.sidebar.markdown("---")

st.sidebar.header("🔍 Filtros")

# Botão para atualizar dados
if st.sidebar.button("🔄 Atualizar Dados"):
    st.cache_data.clear()
    st.rerun()

# Menu de Análises
st.sidebar.markdown("---")
st.sidebar.header("📊 Tipo de Análise")

# Adicionar destaque para a seção de projeção
st.sidebar.info("💡 **Dica:** Para ver a análise de formandos, selecione 'Projeção de Conformidade'")

tipo_analise = st.sidebar.selectbox(
    "Selecione o tipo de análise:",
    ["Dashboard Principal", "Conformidade e Alertas", "🔮 Projeção de Conformidade"],
    help="A Projeção de Conformidade mostra análise detalhada de formandos e impacto nas bolsas"
)

# Filtro por Filial
if not df.empty:
    # Preparar opções de filial
    filiais_disponiveis = df['CODFILIAL'].dropna().unique()
    filiais_opcoes = ['Todas as Filiais']
    
    # Mapear códigos para nomes
    mapeamento_filiais = {
        4: 'Filial 4 - São Paulo',
        7: 'Filial 7 - Espírito Santo'
    }
    
    # Usar set para evitar duplicatas
    codigos_processados = set()
    
    for filial in filiais_disponiveis:
        # Extrair apenas o código numérico, ignorando "Total"
        codigo_str = str(filial).replace(' Total', '')
        if codigo_str.isdigit():
            codigo_filial = int(codigo_str)
            # Só adicionar se não foi processado ainda
            if codigo_filial not in codigos_processados and codigo_filial in mapeamento_filiais:
                filiais_opcoes.append(mapeamento_filiais[codigo_filial])
                codigos_processados.add(codigo_filial)
    
    # Widget de seleção de filial
    filial_selecionada = st.sidebar.selectbox(
        "Selecione a Filial:",
        filiais_opcoes
    )
    
    # Aplicar filtro nos dados
    if filial_selecionada != 'Todas as Filiais':
        # Extrair código da filial selecionada
        if 'São Paulo' in filial_selecionada:
            codigo_filtro = 4
        elif 'Espírito Santo' in filial_selecionada:
            codigo_filtro = 7
        
        # Filtrar dados (incluir dados da filial específica e dados gerais sem filial)
        # Excluir linhas de total
        df_filtrado = df[
            ((df['CODFILIAL'] == codigo_filtro) | (df['CODFILIAL'].isna())) &
            (~df['CODFILIAL'].astype(str).str.endswith(' Total'))
        ]
        
        # Mostrar informação do filtro aplicado
        st.sidebar.success(f"Filtro aplicado: {filial_selecionada}")
    else:
        # Para "Todas as Filiais", também excluir linhas de total
        df_filtrado = df[~df['CODFILIAL'].astype(str).str.endswith(' Total')]
        st.sidebar.info("Mostrando dados de todas as filiais")
else:
    df_filtrado = df

# --- Renderização do Dashboard ---

if not df_filtrado.empty:
    if tipo_analise == "Dashboard Principal":
        # --- KPIs Principais ---
        st.subheader("📈 Indicadores Principais")
        total_matriculados = df_filtrado['TOTAL_MATRICULADOS'].fillna(0).sum()
        total_bolsistas = df_filtrado['TOTAL_INSTITUCIONAL'].fillna(0).sum()
        total_prouni = df_filtrado['TOTAL_PROUNI'].fillna(0).sum()
        total_assistencial = df_filtrado['TOTAL_ASSISTENCIAL_100'].fillna(0).sum() + df_filtrado['TOTAL_ASSISTENCIAL_50'].fillna(0).sum()

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total de Alunos Matriculados", f"{int(total_matriculados):,}".replace(",", "."))
        col2.metric("Total de Bolsistas Institucionais", f"{int(total_bolsistas):,}".replace(",", "."))
        col3.metric("Total ProUni", f"{int(total_prouni):,}".replace(",", "."))
        col4.metric("Total Assistencial", f"{int(total_assistencial):,}".replace(",", "."))

        st.markdown("---")

        # --- Gráfico de Barras ---
        st.subheader("Total de Alunos Matriculados por Curso")
        
        # Criar DataFrame limpo apenas com as colunas necessárias
        df_grafico = df_filtrado[['NOMECURSO', 'TOTAL_MATRICULADOS']].copy()
        df_grafico = df_grafico.fillna(0)
        
        # Gráfico super simples - SEM texto nas barras
        fig = px.bar(
            df_grafico,
            x='NOMECURSO',
            y='TOTAL_MATRICULADOS',
            title="Total de Alunos Matriculados por Curso"
        )
        
        # Adicionar texto manualmente apenas acima das barras
        fig.update_traces(
            text=df_grafico['TOTAL_MATRICULADOS'],
            textposition='outside',
            textfont=dict(size=12, color='white')
        )
        
        fig.update_layout(
            xaxis={'categoryorder':'total descending'},
            xaxis_tickangle=-45,
            # CORREÇÃO: Aumentar margem inferior para dar espaço aos nomes dos cursos
            margin=dict(l=20, r=20, t=50, b=150)  # l=left, r=right, t=top, b=bottom
        )
        
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # --- Gráfico de Pizza ---
        st.subheader("Distribuição de Bolsas por Tipo")
        
        # Preparar dados para o gráfico de pizza
        bolsas_data = {
            'Tipo de Bolsa': ['Institucional', 'ProUni', 'Assistencial 100%', 'Assistencial 50%'],
            'Quantidade': [
                df_filtrado['TOTAL_INSTITUCIONAL'].fillna(0).sum(),
                df_filtrado['TOTAL_PROUNI'].fillna(0).sum(),
                df_filtrado['TOTAL_ASSISTENCIAL_100'].fillna(0).sum(),
                df_filtrado['TOTAL_ASSISTENCIAL_50'].fillna(0).sum()
            ]
        }
        
        df_bolsas = pd.DataFrame(bolsas_data)
        
        fig_bolsas = px.pie(
            df_bolsas,
            values='Quantidade',
            names='Tipo de Bolsa',
            title="Distribuição de Bolsas por Tipo"
        )
        st.plotly_chart(fig_bolsas, use_container_width=True)

        st.markdown("---")

        # --- Gráfico Comparativo de Bolsas por Curso ---
        st.subheader("Comparativo de Bolsas por Curso")
        
        # Selecionar apenas as colunas de bolsas para o gráfico
        colunas_bolsas = ['NOMECURSO', 'TOTAL_INSTITUCIONAL', 'TOTAL_PROUNI', 'TOTAL_ASSISTENCIAL_100', 'TOTAL_ASSISTENCIAL_50']
        df_bolsas_temp = df_filtrado[colunas_bolsas].copy()
        
        # Preencher valores nulos com 0
        for col in ['TOTAL_INSTITUCIONAL', 'TOTAL_PROUNI', 'TOTAL_ASSISTENCIAL_100', 'TOTAL_ASSISTENCIAL_50']:
            df_bolsas_temp[col] = df_bolsas_temp[col].fillna(0)
        
        df_melted = df_bolsas_temp.melt(
            id_vars=['NOMECURSO'], 
            var_name='Tipo_Bolsa', 
            value_name='Quantidade'
        )
        
        # Renomear para nomes mais amigáveis
        df_melted['Tipo_Bolsa'] = df_melted['Tipo_Bolsa'].replace({
            'TOTAL_INSTITUCIONAL': 'Institucional',
            'TOTAL_PROUNI': 'ProUni',
            'TOTAL_ASSISTENCIAL_100': 'Assistencial 100%',
            'TOTAL_ASSISTENCIAL_50': 'Assistencial 50%'
        })
        
        fig_comparativo = px.bar(
            df_melted,
            x='NOMECURSO',
            y='Quantidade',
            color='Tipo_Bolsa',
            title="Distribuição de Bolsas por Curso e Tipo",
            labels={'NOMECURSO': 'Curso', 'Quantidade': 'Número de Bolsas'},
            barmode='group'
        )
        fig_comparativo.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_comparativo, use_container_width=True)

        st.markdown("---")

        # --- Tabela de Dados Completos ---
        st.subheader("Dados Completos")
        
        # Criar DataFrame com totalizadores por filial
        df_com_totais = pd.DataFrame()
        
        # Obter filiais únicas (excluindo totais existentes)
        df_dados_limpos = df_filtrado[~df_filtrado['CODFILIAL'].astype(str).str.endswith(' Total')]
        filiais_unicas = sorted(df_dados_limpos['CODFILIAL'].dropna().astype(str).unique())
        
        # Colunas numéricas para totalização
        colunas_numericas = ['TOTAL_MATRICULADOS', 'ALUNOS_PAGANTES', 'FORMANDOS_NAO_CEBAS', 
                           'TOTAL_INSTITUCIONAL', 'TOTAL_ASSISTENCIAL_100', 'TOTAL_ASSISTENCIAL_50', 
                           'FORMANDOS_ASSISTENCIAL', 'TOTAL_PROUNI']
        
        # Converter colunas numéricas para inteiros nos dados originais
        df_dados_limpos_copy = df_dados_limpos.copy()
        
        # Converter CODFILIAL para string para evitar problemas de tipo ao adicionar totais
        df_dados_limpos_copy['CODFILIAL'] = df_dados_limpos_copy['CODFILIAL'].astype(str)
        
        # Converter TODAS as colunas numéricas para inteiros (exceto CODFILIAL e NOMECURSO)
        for col in df_dados_limpos_copy.columns:
            if col not in ['CODFILIAL', 'NOMECURSO'] and df_dados_limpos_copy[col].dtype in ['float64', 'float32']:
                try:
                    df_dados_limpos_copy[col] = df_dados_limpos_copy[col].fillna(0).astype(int)
                except:
                    pass
        
        for filial in filiais_unicas:
            # Adicionar cursos da filial (agora ambos são strings)
            cursos_filial = df_dados_limpos_copy[df_dados_limpos_copy['CODFILIAL'] == filial].copy()
            df_com_totais = pd.concat([df_com_totais, cursos_filial], ignore_index=True)
            
            # Calcular total da filial
            total_filial = {}
            total_filial['CODFILIAL'] = f"TOTAL_{filial}"
            
            # Definir nome baseado na filial
            if filial == '4':
                total_filial['NOMECURSO'] = "📊 TOTAL SP"
            elif filial == '7':
                total_filial['NOMECURSO'] = "📊 TOTAL SC"
            else:
                total_filial['NOMECURSO'] = f"📊 TOTAL FILIAL {filial}"
            
            # Calcular totais para todas as colunas numéricas
            for col in cursos_filial.columns:
                if cursos_filial[col].dtype in ['int64', 'float64', 'float32']:
                    valor = cursos_filial[col].fillna(0).sum()
                    total_filial[col] = int(valor)
                elif col not in ['CODFILIAL', 'NOMECURSO']:
                    total_filial[col] = ""
            
            # Preencher outras colunas com valores vazios
            for col in df_dados_limpos_copy.columns:
                if col not in total_filial:
                    total_filial[col] = ""
            
            # Adicionar linha de total da filial
            df_com_totais = pd.concat([df_com_totais, pd.DataFrame([total_filial])], ignore_index=True)
        
        # Calcular total geral
        total_geral = {}
        total_geral['CODFILIAL'] = "TOTAL_GERAL"
        total_geral['NOMECURSO'] = "🎯 TOTAL GERAL"
        
        # Calcular totais gerais para todas as colunas numéricas
        for col in df_dados_limpos_copy.columns:
            if col not in ['CODFILIAL', 'NOMECURSO'] and df_dados_limpos_copy[col].dtype in ['int64', 'float64', 'float32']:
                valor = df_dados_limpos_copy[col].fillna(0).sum()
                total_geral[col] = int(valor)
            elif col not in ['CODFILIAL', 'NOMECURSO']:
                total_geral[col] = ""
        
        # Preencher outras colunas com valores vazios
        for col in df_dados_limpos_copy.columns:
            if col not in total_geral:
                total_geral[col] = ""
        
        # Adicionar linha de total geral
        df_com_totais = pd.concat([df_com_totais, pd.DataFrame([total_geral])], ignore_index=True)
        
        # Aplicar estilo condicional com cores mais visíveis
        def aplicar_estilo_totais(row):
            if 'TOTAL SP' in str(row['NOMECURSO']) or 'TOTAL SC' in str(row['NOMECURSO']):
                return ['background-color: #bbdefb; font-weight: bold; border-top: 2px solid #1976d2; color: #000000;'] * len(row)
            elif 'TOTAL GERAL' in str(row['NOMECURSO']):
                return ['background-color: #c8e6c9; font-weight: bold; border-top: 3px solid #388e3c; border-bottom: 3px solid #388e3c; color: #000000;'] * len(row)
            else:
                return [''] * len(row)
        
        # Exibir tabela de dados completos
        st.dataframe(
            df_com_totais.style.apply(aplicar_estilo_totais, axis=1),
            use_container_width=True
        )
        
    elif tipo_analise == "Conformidade e Alertas":
        st.header("🚨 Conformidade e Alertas")
        st.markdown("**Análise de conformidade baseada nos dados reais de bolsistas**")
        
        dados_conformidade = gerar_dados_conformidade_reais()

        if dados_conformidade is not None:
            df_conformidade, df_detalhado = dados_conformidade
            st.success("✅ Dados de conformidade gerados com base nos dados reais!")
        else:
            # Fallback para dados de exemplo
            try:
                df_conformidade = pd.read_excel('dados_conformidade_exemplo.xlsx')
                df_detalhado = df_conformidade.copy()
                st.warning("⚠️ Usando dados de exemplo. Verifique se o arquivo 'dados_bolsistas.xlsx' está disponível.")
            except FileNotFoundError:
                st.error("❌ Nenhum arquivo de dados encontrado. Verifique se 'dados_bolsistas.xlsx' ou 'dados_conformidade_exemplo.xlsx' estão disponíveis.")
                st.stop()
        
        # Aplicar filtro por filial selecionada se não for "Todas as Filiais"
        if filial_selecionada != 'Todas as Filiais':
            # Determinar código da filial
            if 'São Paulo' in filial_selecionada:
                codigo_filtro = '4'
            elif 'Espírito Santo' in filial_selecionada:
                codigo_filtro = '7'
            
            # Filtrar dados detalhados por filial
            if 'CODFILIAL' in df_detalhado.columns:
                df_detalhado = df_detalhado[df_detalhado['CODFILIAL'] == codigo_filtro]
                
                # Recalcular dados de conformidade agregados para a filial selecionada
                df_conformidade = df_detalhado.groupby('NOMECURSO').agg({
                    'PROUNI_SOBRA_FALTA': 'sum',
                    'FILANTROPIA_SOBRA_FALTA': 'sum'
                }).reset_index()
                
                # Converter para inteiros
                df_conformidade['PROUNI_SOBRA_FALTA'] = df_conformidade['PROUNI_SOBRA_FALTA'].fillna(0).round().astype(int)
                df_conformidade['FILANTROPIA_SOBRA_FALTA'] = df_conformidade['FILANTROPIA_SOBRA_FALTA'].fillna(0).round().astype(int)
                
                st.info(f"📍 Dados filtrados para: {filial_selecionada}")
            else:
                st.warning("⚠️ Dados de filial não disponíveis para filtro")
        
        # Adicionar colunas de conformidade "Atende" e "Não Atende"
        df_conformidade['PROUNI_Atende'] = df_conformidade['PROUNI_SOBRA_FALTA'].apply(lambda x: 'Atende' if x >= 0 else 'Não Atende')
        df_conformidade['FILANTROPIA_Atende'] = df_conformidade['FILANTROPIA_SOBRA_FALTA'].apply(lambda x: 'Atende' if x >= 0 else 'Não Atende')
            
        # --- KPIs de Alertas ---
        st.subheader("🚨 Indicadores de Conformidade")
        
        saldo_prouni = df_conformidade['PROUNI_SOBRA_FALTA'].sum()
        saldo_filantropia = df_conformidade['FILANTROPIA_SOBRA_FALTA'].sum()
        cursos_deficit = len(df_conformidade[
            (df_conformidade['PROUNI_SOBRA_FALTA'] < 0) | 
            (df_conformidade['FILANTROPIA_SOBRA_FALTA'] < 0)
        ])
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            cor_prouni = obter_cor_condicional(saldo_prouni)
            st.markdown(f"""
            <div style="background-color: {cor_prouni}; padding: 1rem; border-radius: 0.5rem; text-align: center;">
                <h3 style="color: white; margin: 0;">Saldo Geral PROUNI</h3>
                <h2 style="color: white; margin: 0;">{int(saldo_prouni):+d}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            cor_filantropia = obter_cor_condicional(saldo_filantropia)
            st.markdown(f"""
            <div style="background-color: {cor_filantropia}; padding: 1rem; border-radius: 0.5rem; text-align: center;">
                <h3 style="color: white; margin: 0;">Saldo Geral Filantropia</h3>
                <h2 style="color: white; margin: 0;">{int(saldo_filantropia):+d}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            cor_deficit = "#dc3545" if cursos_deficit > 0 else "#28a745"
            st.markdown(f"""
            <div style="background-color: {cor_deficit}; padding: 1rem; border-radius: 0.5rem; text-align: center;">
                <h3 style="color: white; margin: 0;">Cursos em Déficit</h3>
                <h2 style="color: white; margin: 0;">{cursos_deficit}</h2>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # --- Gráficos Divergentes ---
        col1, col2 = st.columns(2)
        
        with col1:
            fig_prouni = criar_grafico_divergente(
                df_conformidade, 
                'PROUNI_SOBRA_FALTA', 
                "📊 Análise PROUNI por Curso"
            )
            st.plotly_chart(fig_prouni, use_container_width=True)
        
        with col2:
            fig_filantropia = criar_grafico_divergente(
                df_conformidade, 
                'FILANTROPIA_SOBRA_FALTA', 
                "📊 Análise Filantropia por Curso"
            )
            st.plotly_chart(fig_filantropia, use_container_width=True)

        st.markdown("---")

        # --- Tabela Detalhada com Estilização ---
        st.subheader("📋 Tabela Detalhada de Conformidade")
        
        def aplicar_estilo_conformidade(val):
            if pd.isna(val):
                return ''
            if val > 0:
                return 'background-color: #d4edda; color: #155724'  # Verde claro
            elif val < 0:
                return 'background-color: #f8d7da; color: #721c24'  # Vermelho claro
            else:
                return 'background-color: #d1ecf1; color: #0c5460'  # Azul claro
        
        def aplicar_estilo_atende(val):
            if val == 'Atende':
                return 'background-color: #d4edda; color: #155724; font-weight: bold'  # Verde
            elif val == 'Não Atende':
                return 'background-color: #f8d7da; color: #721c24; font-weight: bold'  # Vermelho
            else:
                return ''
        
        # Verificar se df_detalhado existe e tem a coluna CODFILIAL
        if 'df_detalhado' in locals() and df_detalhado is not None and 'CODFILIAL' in df_detalhado.columns and not df_detalhado.empty:
            # Usar dados detalhados com informações de filial
            df_display = df_detalhado.copy()
            
            # Adicionar colunas de conformidade aos dados detalhados
            df_display['PROUNI_Atende'] = df_display['PROUNI_SOBRA_FALTA'].apply(lambda x: 'Atende' if x >= 0 else 'Não Atende')
            df_display['FILANTROPIA_Atende'] = df_display['FILANTROPIA_SOBRA_FALTA'].apply(lambda x: 'Atende' if x >= 0 else 'Não Atende')
            
            filiais_unicas = sorted(df_display['CODFILIAL'].dropna().astype(str).unique())
            
            # Criar lista para dados reorganizados
            dados_reorganizados = []
            
            # Para cada filial, adicionar seus cursos + total da filial
            for filial in filiais_unicas:
                # Adicionar todos os cursos da filial
                df_filial = df_display[df_display['CODFILIAL'] == filial]
                dados_reorganizados.extend(df_filial.to_dict('records'))
                
                # Calcular e adicionar total da filial
                total_prouni = int(df_filial['PROUNI_SOBRA_FALTA'].sum())
                total_filantropia = int(df_filial['FILANTROPIA_SOBRA_FALTA'].sum())
                
                linha_total_filial = {
                    'CODFILIAL': f'TOTAL_{filial}',
                    'NOMECURSO': f'📊 TOTAL FILIAL {filial}',
                    'PROUNI_SOBRA_FALTA': total_prouni,
                    'FILANTROPIA_SOBRA_FALTA': total_filantropia,
                    'PROUNI_Atende': 'Atende' if total_prouni >= 0 else 'Não Atende',
                    'FILANTROPIA_Atende': 'Atende' if total_filantropia >= 0 else 'Não Atende'
                }
                # Adicionar outras colunas se existirem
                for col in df_display.columns:
                    if col not in linha_total_filial:
                        linha_total_filial[col] = ''
                
                dados_reorganizados.append(linha_total_filial)
            
            # Adicionar total geral no final se houver mais de uma filial
            if len(filiais_unicas) > 1:
                total_geral_prouni = int(df_display['PROUNI_SOBRA_FALTA'].sum())
                total_geral_filantropia = int(df_display['FILANTROPIA_SOBRA_FALTA'].sum())
                
                linha_total_geral = {
                    'CODFILIAL': 'GERAL',
                    'NOMECURSO': '🎯 TOTAL GERAL',
                    'PROUNI_SOBRA_FALTA': total_geral_prouni,
                    'FILANTROPIA_SOBRA_FALTA': total_geral_filantropia,
                    'PROUNI_Atende': 'Atende' if total_geral_prouni >= 0 else 'Não Atende',
                    'FILANTROPIA_Atende': 'Atende' if total_geral_filantropia >= 0 else 'Não Atende'
                }
                # Adicionar outras colunas se existirem
                for col in df_display.columns:
                    if col not in linha_total_geral:
                        linha_total_geral[col] = ''
                
                dados_reorganizados.append(linha_total_geral)
            
            # Criar DataFrame final reorganizado
            df_final = pd.DataFrame(dados_reorganizados)
            
            # Definir ordem padrão das colunas
            colunas_ordenadas = ['NOMECURSO', 'PROUNI_SOBRA_FALTA', 'PROUNI_Atende', 'FILANTROPIA_SOBRA_FALTA', 'FILANTROPIA_Atende']
            
            # Verificar quais colunas existem no DataFrame
            colunas_existentes = [col for col in colunas_ordenadas if col in df_final.columns]
            
            # Adicionar outras colunas que possam existir (como CODFILIAL) no final
            outras_colunas = [col for col in df_final.columns if col not in colunas_ordenadas]
            
            # Reorganizar DataFrame com a ordem desejada
            df_final = df_final[colunas_existentes + outras_colunas]
            
            # Aplicar estilo especial para linhas de total
            def aplicar_estilo_linha(row):
                styles = [''] * len(row)
                
                # Verificar se é linha de total
                if 'TOTAL GERAL' in str(row['NOMECURSO']):
                    styles = ['background-color: #343a40; color: white; font-weight: bold'] * len(row)
                elif 'TOTAL FILIAL' in str(row['NOMECURSO']):
                    styles = ['background-color: #6c757d; color: white; font-weight: bold'] * len(row)
                else:
                    # Aplicar estilo normal para valores numéricos
                    for i, (col_name, val) in enumerate(row.items()):
                        if col_name in ['PROUNI_SOBRA_FALTA', 'FILANTROPIA_SOBRA_FALTA'] and pd.notna(val):
                            if val > 0:
                                styles[i] = 'background-color: #d4edda; color: #155724'
                            elif val < 0:
                                styles[i] = 'background-color: #f8d7da; color: #721c24'
                            else:
                                styles[i] = 'background-color: #d1ecf1; color: #0c5460'
                        elif col_name in ['PROUNI_Atende', 'FILANTROPIA_Atende']:
                            if val == 'Atende':
                                styles[i] = 'background-color: #d4edda; color: #155724; font-weight: bold'
                            elif val == 'Não Atende':
                                styles[i] = 'background-color: #f8d7da; color: #721c24; font-weight: bold'
                
                return styles
            
            # Aplicar estilo à tabela final
            df_styled = df_final.style.apply(aplicar_estilo_linha, axis=1)
            
        else:
            # Caso não tenha dados detalhados ou estejam vazios, usar dados de conformidade agregados
            if not df_conformidade.empty:
                # Reorganizar colunas para melhor visualização
                colunas_ordenadas = ['NOMECURSO', 'PROUNI_SOBRA_FALTA', 'PROUNI_Atende', 'FILANTROPIA_SOBRA_FALTA', 'FILANTROPIA_Atende']
                df_display = df_conformidade[colunas_ordenadas].copy()
                
                # Aplicar estilo
                df_styled = df_display.style.map(
                    aplicar_estilo_conformidade, 
                    subset=['PROUNI_SOBRA_FALTA', 'FILANTROPIA_SOBRA_FALTA']
                ).map(
                    aplicar_estilo_atende,
                    subset=['PROUNI_Atende', 'FILANTROPIA_Atende']
                )
            else:
                st.error("❌ Nenhum dado de conformidade disponível para exibição")
                df_styled = None
        
        # Exibir a tabela estilizada
        if df_styled is not None:
            st.dataframe(df_styled, use_container_width=True)
        else:
            st.warning("⚠️ Tabela não pode ser exibida - dados indisponíveis")

        # --- Resumo Estatístico ---
        st.markdown("---")
        st.subheader("📈 Resumo Estatístico")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**PROUNI:**")
            st.write(f"• Sobra Total: {df_conformidade[df_conformidade['PROUNI_SOBRA_FALTA'] > 0]['PROUNI_SOBRA_FALTA'].sum():.0f}")
            st.write(f"• Falta Total: {abs(df_conformidade[df_conformidade['PROUNI_SOBRA_FALTA'] < 0]['PROUNI_SOBRA_FALTA'].sum()):.0f}")
            st.write(f"• Cursos com Sobra: {len(df_conformidade[df_conformidade['PROUNI_SOBRA_FALTA'] > 0])}")
            st.write(f"• Cursos com Falta: {len(df_conformidade[df_conformidade['PROUNI_SOBRA_FALTA'] < 0])}")
        
        with col2:
            st.write("**Filantropia:**")
            st.write(f"• Sobra Total: {df_conformidade[df_conformidade['FILANTROPIA_SOBRA_FALTA'] > 0]['FILANTROPIA_SOBRA_FALTA'].sum():.0f}")
            st.write(f"• Falta Total: {abs(df_conformidade[df_conformidade['FILANTROPIA_SOBRA_FALTA'] < 0]['FILANTROPIA_SOBRA_FALTA'].sum()):.0f}")
            st.write(f"• Cursos com Sobra: {len(df_conformidade[df_conformidade['FILANTROPIA_SOBRA_FALTA'] > 0])}")
            st.write(f"• Cursos com Falta: {len(df_conformidade[df_conformidade['FILANTROPIA_SOBRA_FALTA'] < 0])}")
    
    elif "Projeção de Conformidade" in tipo_analise:
        st.header("🔮 Projeção de Conformidade - Análise de Formandos")
        st.markdown("**Análise preditiva baseada no número de formandos para o próximo período**")
        
        # Verificar se temos as colunas necessárias para projeção (usar dados originais)
        colunas_projecao = ['NOMECURSO', 'FORMANDOS_NAO_CEBAS', 'FORMANDOS_ASSISTENCIAL', 
                           'TOTAL_INSTITUCIONAL', 'TOTAL_ASSISTENCIAL_100', 'TOTAL_ASSISTENCIAL_50', 'TOTAL_PROUNI']
        
        colunas_disponiveis = [col for col in colunas_projecao if col in df.columns]
        
        if len(colunas_disponiveis) >= 3:  # Pelo menos curso, formandos e uma coluna de bolsas
            st.success("✅ Dados suficientes para análise de projeção!")
            
            # Preparar dados para projeção (aplicar filtros se necessário)
            if filial_selecionada != 'Todas as Filiais':
                # Aplicar o mesmo filtro usado em outras seções
                if 'São Paulo' in filial_selecionada:
                    codigo_filtro = 4
                elif 'Espírito Santo' in filial_selecionada:
                    codigo_filtro = 7
                
                df_projecao = df[
                    ((df['CODFILIAL'] == codigo_filtro) | (df['CODFILIAL'].isna())) &
                    (~df['CODFILIAL'].astype(str).str.contains('TOTAL', na=False))
                ].copy()
            else:
                df_projecao = df[~df['CODFILIAL'].astype(str).str.contains('TOTAL', na=False)].copy()
            
            # Calcular total de formandos (CEBAS + Assistencial)
            df_projecao['TOTAL_FORMANDOS'] = (
                df_projecao['FORMANDOS_NAO_CEBAS'].fillna(0) + 
                df_projecao['FORMANDOS_ASSISTENCIAL'].fillna(0)
            )
            
            # Calcular total de bolsas atuais
            df_projecao['TOTAL_BOLSAS_ATUAIS'] = (
                df_projecao['TOTAL_INSTITUCIONAL'].fillna(0) +
                df_projecao['TOTAL_ASSISTENCIAL_100'].fillna(0) +
                df_projecao['TOTAL_ASSISTENCIAL_50'].fillna(0) +
                df_projecao['TOTAL_PROUNI'].fillna(0)
            )
            
            # --- INDICADORES PRINCIPAIS DE PROJEÇÃO ---
            st.subheader("📊 Indicadores de Impacto - Próximo Período")
            
            total_formandos = df_projecao['TOTAL_FORMANDOS'].sum()
            total_bolsas_perdidas = df_projecao['FORMANDOS_ASSISTENCIAL'].fillna(0).sum()
            total_bolsas_atuais = df_projecao['TOTAL_BOLSAS_ATUAIS'].sum()
            percentual_impacto = (total_bolsas_perdidas / total_bolsas_atuais * 100) if total_bolsas_atuais > 0 else 0
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Total de Formandos", 
                    f"{int(total_formandos):,}".replace(",", "."),
                    help="Total de alunos que se formarão no próximo período"
                )
            
            with col2:
                st.metric(
                    "Bolsas que serão Perdidas", 
                    f"{int(total_bolsas_perdidas):,}".replace(",", "."),
                    delta=f"-{percentual_impacto:.1f}%",
                    delta_color="inverse",
                    help="Bolsas assistenciais que serão perdidas com as formaturas"
                )
            
            with col3:
                st.metric(
                    "Bolsas Atuais", 
                    f"{int(total_bolsas_atuais):,}".replace(",", "."),
                    help="Total atual de bolsas em vigor"
                )
            
            with col4:
                deficit_projetado = total_bolsas_perdidas
                st.metric(
                    "Déficit Projetado", 
                    f"{int(deficit_projetado):,}".replace(",", "."),
                    delta="Crítico" if deficit_projetado > total_bolsas_atuais * 0.1 else "Moderado",
                    delta_color="inverse" if deficit_projetado > total_bolsas_atuais * 0.1 else "normal",
                    help="Estimativa do déficit de conformidade"
                )
            
            st.markdown("---")
            
            # --- ANÁLISE POR CURSO ---
            st.subheader("📋 Análise Detalhada por Curso")
            
            # Criar DataFrame de análise
            df_analise = df_projecao[df_projecao['TOTAL_FORMANDOS'] > 0].copy()
            
            if not df_analise.empty:
                # Calcular métricas por curso
                df_analise['BOLSAS_PERDIDAS'] = df_analise['FORMANDOS_ASSISTENCIAL'].fillna(0)
                df_analise['PERCENTUAL_IMPACTO'] = (
                    df_analise['BOLSAS_PERDIDAS'] / df_analise['TOTAL_BOLSAS_ATUAIS'] * 100
                ).fillna(0)
                df_analise['STATUS_RISCO'] = df_analise['PERCENTUAL_IMPACTO'].apply(
                    lambda x: "🔴 Alto" if x > 20 else "🟡 Médio" if x > 10 else "🟢 Baixo"
                )
                
                # Selecionar colunas para exibição
                colunas_exibir = ['NOMECURSO', 'TOTAL_FORMANDOS', 'BOLSAS_PERDIDAS', 
                                'TOTAL_BOLSAS_ATUAIS', 'PERCENTUAL_IMPACTO', 'STATUS_RISCO']
                
                df_exibir = df_analise[colunas_exibir].copy()
                df_exibir.columns = ['Curso', 'Total Formandos', 'Bolsas Perdidas', 
                                   'Bolsas Atuais', 'Impacto (%)', 'Nível de Risco']
                
                # Ordenar por impacto (maior primeiro)
                df_exibir = df_exibir.sort_values('Impacto (%)', ascending=False)
                
                # Aplicar formatação
                df_exibir['Impacto (%)'] = df_exibir['Impacto (%)'].round(1)
                
                st.dataframe(df_exibir, use_container_width=True)
                
                st.markdown("---")
                
                # --- GRÁFICOS DE ANÁLISE ---
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("📊 Impacto por Curso")
                    fig_impacto = px.bar(
                        df_exibir.head(10),
                        x='Impacto (%)',
                        y='Curso',
                        orientation='h',
                        title="Top 10 Cursos com Maior Impacto (%)",
                        color='Impacto (%)',
                        color_continuous_scale='Reds'
                    )
                    fig_impacto.update_layout(height=400)
                    st.plotly_chart(fig_impacto, use_container_width=True)
                
                with col2:
                    st.subheader("🎯 Bolsas em Risco")
                    fig_bolsas = px.bar(
                        df_exibir.head(10),
                        x='Bolsas Perdidas',
                        y='Curso',
                        orientation='h',
                        title="Top 10 Cursos - Bolsas Perdidas",
                        color='Bolsas Perdidas',
                        color_continuous_scale='Oranges'
                    )
                    fig_bolsas.update_layout(height=400)
                    st.plotly_chart(fig_bolsas, use_container_width=True)
                
                st.markdown("---")
                
                # --- ANÁLISE DE TENDÊNCIAS ---
                st.subheader("📈 Análise de Tendências e Recomendações")
                
                # Calcular estatísticas
                cursos_alto_risco = len(df_analise[df_analise['PERCENTUAL_IMPACTO'] > 20])
                cursos_medio_risco = len(df_analise[(df_analise['PERCENTUAL_IMPACTO'] > 10) & (df_analise['PERCENTUAL_IMPACTO'] <= 20)])
                cursos_baixo_risco = len(df_analise[df_analise['PERCENTUAL_IMPACTO'] <= 10])
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f"""
                    <div style="background-color: #ffebee; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #f44336;">
                        <h4 style="color: #c62828; margin: 0;">🔴 Alto Risco</h4>
                        <h2 style="color: #c62828; margin: 0;">{cursos_alto_risco}</h2>
                        <p style="margin: 0; color: #666;">Cursos com impacto > 20%</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div style="background-color: #fff8e1; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #ff9800;">
                        <h4 style="color: #ef6c00; margin: 0;">🟡 Médio Risco</h4>
                        <h2 style="color: #ef6c00; margin: 0;">{cursos_medio_risco}</h2>
                        <p style="margin: 0; color: #666;">Cursos com impacto 10-20%</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <div style="background-color: #e8f5e8; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #4caf50;">
                        <h4 style="color: #2e7d32; margin: 0;">🟢 Baixo Risco</h4>
                        <h2 style="color: #2e7d32; margin: 0;">{cursos_baixo_risco}</h2>
                        <p style="margin: 0; color: #666;">Cursos com impacto ≤ 10%</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("---")
                
                # --- RECOMENDAÇÕES ESTRATÉGICAS ---
                st.subheader("💡 Recomendações Estratégicas")
                
                if cursos_alto_risco > 0:
                    st.error(f"""
                    **🚨 AÇÃO URGENTE NECESSÁRIA:**
                    - {cursos_alto_risco} curso(s) com alto risco de não conformidade
                    - Priorizar captação de novos bolsistas assistenciais
                    - Revisar critérios de concessão de bolsas
                    """)
                
                if cursos_medio_risco > 0:
                    st.warning(f"""
                    **⚠️ MONITORAMENTO NECESSÁRIO:**
                    - {cursos_medio_risco} curso(s) com risco moderado
                    - Implementar estratégias preventivas
                    - Acompanhar evolução mensal
                    """)
                
                if cursos_baixo_risco > 0:
                    st.success(f"""
                    **✅ SITUAÇÃO CONTROLADA:**
                    - {cursos_baixo_risco} curso(s) com baixo risco
                    - Manter estratégias atuais
                    - Considerar redistribuição de recursos
                    """)
                
                # Projeção de necessidades
                st.markdown("---")
                st.subheader("🎯 Projeção de Necessidades")
                
                necessidade_bolsas = total_bolsas_perdidas
                
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"""
                    **📊 Necessidades Projetadas:**
                    - **Novas bolsas necessárias:** {int(necessidade_bolsas):,}
                    """.replace(",", "."))
                
                with col2:
                    st.info(f"""
                    **⏰ Cronograma Sugerido:**
                    - **Início da captação:** 3 meses antes
                    - **Processo seletivo:** 2 meses antes
                    - **Implementação:** 1 mês antes das formaturas
                    """)
            
            else:
                st.warning("⚠️ Nenhum curso com formandos identificado nos dados atuais.")
        
        else:
            st.error("❌ Dados insuficientes para análise de projeção.")
            st.info(f"""
            **Colunas necessárias para análise:** {len(colunas_disponiveis)}/{len(colunas_projecao)} disponíveis
            
            **Status das colunas:**
            """)
            
            # Mostrar status detalhado das colunas
            for col in colunas_projecao:
                status = "✅" if col in df.columns else "❌"
                st.write(f"{status} {col}")
            
            st.warning("⚠️ **Debug Info:** Se você está vendo esta mensagem, pode haver um problema no código. Contate o suporte técnico.")

else:
    st.warning("Nenhum dado para exibir. Verifique a fonte de dados.")

# --- Documentação da Fonte dos Dados (sempre visível) ---
st.markdown("---")
st.subheader("📄 Fonte dos Dados")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **📊 Dados Principais:**
    - **Arquivo:** `dados_bolsistas.xlsx`
    - **Conteúdo:** Dados detalhados de bolsistas por filial e curso
    - **Colunas principais:**
      - CODFILIAL (Código da Filial)
      - NOMECURSO (Nome do Curso)
      - PROUNI_BOLSAS, PROUNI_VAGAS, PROUNI_SOBRA_FALTA
      - FILANTROPIA_BOLSAS, FILANTROPIA_VAGAS, FILANTROPIA_SOBRA_FALTA
    """)

with col2:
    st.markdown("""
    **📋 Dados de Conformidade:**
    - **Fonte:** Gerados automaticamente a partir de `dados_bolsistas.xlsx`
    - **Conteúdo:** Análise de conformidade por curso baseada em dados reais
      - **Colunas principais:**
        - NOMECURSO (Nome do Curso)
        - PROUNI_SOBRA_FALTA (Saldo PROUNI - baseado em FALTAM_SOBRAM_PROUNI)
        - FILANTROPIA_SOBRA_FALTA (Saldo Filantropia - baseado em FALTAM_SOBRAM_FILANTROPIA)
        - CODFILIAL (Código da Filial para análise detalhada)
      """)

st.info("💡 **Nota:** Os dados são carregados automaticamente dos arquivos Excel. Em caso de erro, verifique se os arquivos estão no diretório correto e possuem as colunas necessárias.")