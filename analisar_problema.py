import pandas as pd
import numpy as np

# Carregar dados
df = pd.read_excel('dados_bolsistas.xlsx')

print('=== ANÁLISE DOS DADOS ===')
print(f'Total de linhas: {len(df)}')
print(f'Total de colunas: {len(df.columns)}')
print()

print('=== VALORES ÚNICOS DE CODFILIAL ===')
print(df['CODFILIAL'].value_counts())
print()

print('=== DADOS ORIGINAIS (primeiras 10 linhas) ===')
print(df[['CODFILIAL', 'NOMECURSO', 'TOTAL_MATRICULADOS']].head(10))
print()

print('=== DADOS FILTRADOS (sem TOTAL) ===')
df_sem_total = df[~df['CODFILIAL'].astype(str).str.contains('TOTAL', na=False)]
print(f'Linhas após filtrar TOTAL: {len(df_sem_total)}')
print(df_sem_total[['CODFILIAL', 'NOMECURSO', 'TOTAL_MATRICULADOS']])
print()

print('=== VERIFICANDO DADOS NULOS ===')
print(f'Valores nulos em CODFILIAL: {df["CODFILIAL"].isnull().sum()}')
print(f'Valores nulos em NOMECURSO: {df["NOMECURSO"].isnull().sum()}')
print()

print('=== TIPOS DE DADOS ===')
print(df.dtypes)
print()

print('=== TODOS OS DADOS COMPLETOS ===')
print(df)