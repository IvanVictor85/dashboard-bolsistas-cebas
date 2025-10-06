import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(
    page_title="Teste Dashboard",
    page_icon="🧪",
    layout="wide"
)

st.title("🧪 Teste de Funcionamento")
st.write("Se você está vendo esta mensagem, o Streamlit está funcionando corretamente!")

# Teste básico de dados
data = {
    'Curso': ['Medicina', 'Enfermagem', 'Fisioterapia'],
    'Alunos': [100, 80, 60]
}

df = pd.DataFrame(data)
st.dataframe(df)

st.success("✅ Teste concluído com sucesso!")