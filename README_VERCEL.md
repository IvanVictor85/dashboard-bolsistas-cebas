# Deploy no Vercel - Dashboard São Camilo

## ⚠️ Importante

Este projeto é uma aplicação **Streamlit** que funciona melhor no **Streamlit Cloud**. O Vercel não suporta nativamente aplicações Streamlit.

## 🚀 Soluções Recomendadas

### 1. Streamlit Cloud (Recomendado)
- Acesse: https://streamlit.io/cloud
- Conecte seu repositório GitHub
- Deploy automático e gratuito
- Suporte nativo para Streamlit

### 2. Heroku
- Suporte nativo para aplicações Python/Streamlit
- Use o `Procfile` já configurado
- Deploy direto do GitHub

### 3. Railway
- Alternativa moderna ao Heroku
- Suporte nativo para Streamlit
- Deploy automático

## 🔧 Configuração Atual do Vercel

O arquivo `index.py` foi criado como uma solução temporária que:
- Redireciona para a versão no Streamlit Cloud
- Fornece informações sobre o projeto
- Mantém o projeto acessível no Vercel

## 📁 Arquivos de Configuração

- `vercel.json` - Configuração do Vercel
- `index.py` - Ponto de entrada Flask para redirecionamento
- `app.py` - Aplicação Streamlit principal
- `requirements.txt` - Dependências Python

## 🛠️ Para Resolver o Erro 404

1. **Commit e push** dos novos arquivos
2. **Redeploy** no Vercel
3. **Considere migrar** para Streamlit Cloud para melhor experiência

## 📊 Funcionalidades do Dashboard

- Dashboard de Alunos Bolsistas
- Análise de Conformidade e Alertas
- Projeção de Necessidades
- Filtros por Filial
- Visualizações interativas com Plotly