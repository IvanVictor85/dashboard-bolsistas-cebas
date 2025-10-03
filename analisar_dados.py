import pandas as pd

try:
    df = pd.read_excel('dados_bolsistas.xlsx')
    print('Colunas disponíveis:')
    for i, col in enumerate(df.columns, 1):
        print(f'{i:2d}. {col}')
    
    print(f'\nTotal de linhas: {len(df)}')
    
    if 'NOMECURSO' in df.columns:
        print(f'Total de cursos únicos: {df["NOMECURSO"].nunique()}')
        print('\nCursos únicos:')
        cursos_unicos = df['NOMECURSO'].dropna().unique()
        for i, curso in enumerate(sorted(cursos_unicos), 1):
            print(f'{i:2d}. {curso}')
    else:
        print('Coluna NOMECURSO não encontrada')
    
    print('\nPrimeiras 3 linhas:')
    print(df.head(3))
    
    # Verificar se existem colunas relacionadas a PROUNI e Filantropia
    print('\nColunas relacionadas a PROUNI:')
    prouni_cols = [col for col in df.columns if 'PROUNI' in col.upper()]
    for col in prouni_cols:
        print(f'  - {col}')
    
    print('\nColunas relacionadas a FILANTROPIA:')
    filantropia_cols = [col for col in df.columns if 'FILANTROPIA' in col.upper()]
    for col in filantropia_cols:
        print(f'  - {col}')
        
except Exception as e:
    print(f'Erro: {e}')