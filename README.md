# 📊 Dashboard de Alunos Bolsistas - Sistema de Monitoramento de Bolsas e Conformidade

## 📋 Descrição

Sistema de monitoramento e análise de bolsas de estudo desenvolvido em Streamlit para acompanhamento de conformidade PROUNI e Filantropia. O dashboard oferece três módulos principais: análise geral, conformidade/alertas e projeções futuras.

## 🚀 Funcionalidades

### 📈 Dashboard Principal
- **KPIs Principais**: Total de matriculados, bolsistas institucionais, ProUni e assistencial
- **Análise por Filial**: Distribuição de bolsas por unidade
- **Gráficos Interativos**: Visualizações de distribuição e tendências
- **Filtros Dinâmicos**: Seleção por filial específica ou visão geral

### ⚠️ Conformidade e Alertas
- **Monitoramento de Sobras/Faltas**: Identificação de desequilíbrios nas bolsas
- **Alertas Automáticos**: Notificações para cursos em não conformidade
- **Análise Estatística**: Resumo estatístico dos dados de conformidade
- **Visualizações Específicas**: Gráficos focados em conformidade

### 🔮 Projeção de Conformidade
- **Análise Preditiva**: Projeções baseadas em dados históricos
- **Indicadores-Chave**: Métricas de performance e tendências
- **Análise Detalhada por Curso**: Insights específicos por programa
- **Categorização de Risco**: Classificação de cursos por nível de risco
- **Recomendações Estratégicas**: Sugestões baseadas em análise de dados

## 🛠️ Tecnologias Utilizadas

- **Python 3.8+**
- **Streamlit**: Framework para aplicações web
- **Pandas**: Manipulação e análise de dados
- **Plotly**: Visualizações interativas
- **NumPy**: Computação numérica
- **Openpyxl**: Leitura de arquivos Excel

## 📦 Instalação

1. **Clone o repositório:**
```bash
git clone https://github.com/seu-usuario/dashboard-bolsistas.git
cd dashboard-bolsistas
```

2. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

3. **Execute a aplicação:**
```bash
streamlit run app.py
```

4. **Acesse no navegador:**
```
http://localhost:8501
```

## 📁 Estrutura do Projeto

```
├── app.py                          # Aplicação principal do Streamlit
├── requirements.txt                # Dependências do projeto
├── dados_bolsistas.xlsx            # Base de dados principal
├── logo_sao_camilo.svg            # Logo da instituição
├── .gitignore                     # Arquivos ignorados pelo Git
└── README.md                      # Documentação do projeto
```

## 📊 Fonte dos Dados

### 📋 Dados Principais
- **Arquivo**: `dados_bolsistas.xlsx`
- **Conteúdo**: Dados detalhados de bolsistas por filial e curso
- **Colunas principais**:
  - `CODFILIAL`: Código da Filial
  - `NOMECURSO`: Nome do Curso
  - `PROUNI_BOLSAS`, `PROUNI_VAGAS`, `PROUNI_SOBRA_FALTA`
  - `FILANTROPIA_BOLSAS`, `FILANTROPIA_VAGAS`, `FILANTROPIA_SOBRA_FALTA`

### 📈 Dados de Conformidade
- **Fonte**: Gerados automaticamente a partir de `dados_bolsistas.xlsx`
- **Conteúdo**: Análise de conformidade por curso baseada em dados reais
- **Colunas principais**:
  - `NOMECURSO`: Nome do Curso
  - `PROUNI_SOBRA_FALTA`: Saldo PROUNI
  - `FILANTROPIA_SOBRA_FALTA`: Saldo Filantropia
  - `CODFILIAL`: Código da Filial para análise detalhada

## 🔧 Configuração

### Requisitos do Sistema
- Python 3.8 ou superior
- Navegador web moderno
- Arquivo Excel com dados de bolsistas

### Variáveis de Ambiente
Não são necessárias configurações especiais de ambiente.

## 📱 Como Usar

1. **Inicie a aplicação** executando `streamlit run app.py`
2. **Selecione o tipo de análise** no menu lateral:
   - Dashboard Principal
   - Conformidade e Alertas
   - 🔮 Projeção de Conformidade
3. **Aplique filtros** conforme necessário (por filial)
4. **Explore os dados** através dos gráficos e tabelas interativas

## 🤝 Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 📞 Contato

Para dúvidas ou sugestões, entre em contato através dos canais oficiais da instituição.

## 🔄 Atualizações

### Versão Atual: 1.0.0
- ✅ Dashboard principal com KPIs
- ✅ Módulo de conformidade e alertas
- ✅ Sistema de projeções
- ✅ Filtros por filial
- ✅ Visualizações interativas

---

**Desenvolvido para o Sistema de Monitoramento de Bolsas e Conformidade**