import pandas as pd

# Dados de exemplo
data = {
    'NOMECURSO': ['Engenharia de Software', 'Ciência de Dados', 'Administração', 'Direito', 'Medicina', 'Psicologia'],
    'TOTAL_MATRICULADOS': [120, 80, 150, 200, 90, 110],
    'TOTAL_INSTITUCIONAL': [30, 25, 40, 50, 20, 35]
}

# Criar DataFrame
df = pd.DataFrame(data)

# Salvar em Excel
df.to_excel("dados_bolsistas.xlsx", index=False)

print("Arquivo 'dados_bolsistas.xlsx' criado com sucesso.")