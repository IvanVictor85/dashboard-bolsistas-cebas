# 🚀 Guia de Deploy - Dashboard São Camilo

## 📋 Resumo da Situação

**Problema Identificado**: Streamlit não é compatível com Vercel (que é otimizado para aplicações estáticas/serverless).

**Solução Recomendada**: Deploy no Streamlit Cloud (plataforma oficial).

## 🎯 Opções de Deploy

### 1. 🌟 Streamlit Cloud (RECOMENDADO)

#### Vantagens:
- ✅ Plataforma oficial do Streamlit
- ✅ Deploy gratuito e automático
- ✅ Integração direta com GitHub
- ✅ SSL automático
- ✅ Monitoramento integrado

#### Passos para Deploy:

1. **Preparar o Repositório**
   ```bash
   # Já feito - seu projeto está no GitHub
   git push origin main
   ```

2. **Acessar Streamlit Cloud**
   - Vá para: https://share.streamlit.io/
   - Faça login com GitHub

3. **Criar Nova App**
   - Clique em "New app"
   - Selecione: `IvanVictor85/dashboard-bolsistas-cebas`
   - Branch: `main`
   - Main file: `app.py` (ou `app_optimized.py` para versão otimizada)

4. **Configurar Secrets** (se necessário)
   - No painel da app, vá em "Settings" > "Secrets"
   - Adicione variáveis sensíveis no formato TOML

#### URL Final:
`https://dashboard-bolsistas-cebas-[hash].streamlit.app`

### 2. 🚂 Railway (Alternativa Robusta)

#### Vantagens:
- ✅ Suporte nativo ao Streamlit
- ✅ Deploy automático via GitHub
- ✅ Plano gratuito (500h/mês)
- ✅ Banco de dados integrado

#### Passos para Deploy:

1. **Criar Procfile**
   ```
   web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
   ```

2. **Deploy no Railway**
   - Acesse: https://railway.app/
   - Conecte com GitHub
   - Selecione o repositório
   - Deploy automático

### 3. 🟣 Heroku (Tradicional)

#### Configuração necessária:

1. **Criar Procfile**
   ```
   web: sh setup.sh && streamlit run app.py
   ```

2. **Criar setup.sh**
   ```bash
   mkdir -p ~/.streamlit/
   echo "\\
   [general]\\n\\
   email = \\"your-email@domain.com\\"\\n\\
   " > ~/.streamlit/credentials.toml
   echo "\\
   [server]\\n\\
   headless = true\\n\\
   enableCORS=false\\n\\
   port = $PORT\\n\\
   " > ~/.streamlit/config.toml
   ```

## 🔧 Configurações Implementadas

### Arquivos Criados:

1. **`.streamlit/config.toml`** - Configurações de produção
2. **`.streamlit/secrets.toml`** - Template para variáveis sensíveis
3. **`app_optimized.py`** - Versão otimizada com cache e performance

### Otimizações Implementadas:

- ✅ **Cache inteligente** com TTL configurável
- ✅ **Lazy loading** de dados
- ✅ **Otimização de tipos** de dados
- ✅ **CSS customizado** para melhor UX
- ✅ **Error handling** robusto
- ✅ **Performance monitoring** (modo debug)

## 🔐 Configuração de Secrets

### Para Streamlit Cloud:

```toml
# No painel de Secrets da Streamlit Cloud
[general]
debug_mode = false
use_api = false

[api]
url = "https://sua-api.com/dados"
key = "sua-chave-api"

[database]
host = "seu-host"
username = "seu-usuario"
password = "sua-senha"
```

## 📊 Monitoramento e Analytics

### Métricas Disponíveis:
- Tempo de carregamento
- Número de registros
- Performance de cache
- Erros de API

### Logs:
- Streamlit Cloud: Painel integrado
- Railway: Dashboard de logs
- Heroku: `heroku logs --tail`

## 🚀 Deploy Rápido (Streamlit Cloud)

```bash
# 1. Verificar se está tudo commitado
git status

# 2. Push final
git push origin main

# 3. Acessar Streamlit Cloud
# https://share.streamlit.io/

# 4. Criar app apontando para:
# Repo: IvanVictor85/dashboard-bolsistas-cebas
# Branch: main
# File: app.py
```

## 🔍 Troubleshooting

### Problemas Comuns:

1. **Arquivo não encontrado**
   - Verificar se `dados_bolsistas.xlsx` está no repo
   - Configurar `use_api = true` nos secrets

2. **Dependências**
   - Verificar `requirements.txt`
   - Adicionar versões específicas se necessário

3. **Performance lenta**
   - Usar `app_optimized.py`
   - Configurar cache adequadamente

## 📈 Próximos Passos

1. ✅ Deploy no Streamlit Cloud
2. ⏳ Configurar domínio customizado (opcional)
3. ⏳ Implementar analytics avançados
4. ⏳ Configurar CI/CD automático
5. ⏳ Adicionar testes automatizados

---

**Status**: ✅ Pronto para deploy no Streamlit Cloud
**Tempo estimado**: 5-10 minutos