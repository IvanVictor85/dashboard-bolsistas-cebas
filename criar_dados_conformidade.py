import pandas as pd
import numpy as np

# Criar dados de exemplo para o dashboard de conformidade
def criar_dados_exemplo():
    """
    Cria um arquivo Excel com dados de exemplo para testar o dashboard de conformidade.
    """
    
    # Lista de cursos de exemplo
    cursos = [
        "Administração",
        "Direito", 
        "Engenharia Civil",
        "Medicina",
        "Enfermagem",
        "Psicologia",
        "Ciência da Computação",
        "Arquitetura e Urbanismo",
        "Fisioterapia",
        "Nutrição",
        "Pedagogia",
        "Contabilidade",
        "Marketing",
        "Engenharia de Produção",
        "Biomedicina"
    ]
    
    # Gerar dados aleatórios para simular superávit e déficit
    np.random.seed(42)  # Para resultados reproduzíveis
    
    dados = []
    for curso in cursos:
        # Simular saldos de PROUNI (pode ser positivo, negativo ou zero)
        prouni_saldo = np.random.randint(-15, 20)
        
        # Simular saldos de Filantropia (pode ser positivo, negativo ou zero)
        filantropia_saldo = np.random.randint(-10, 25)
        
        dados.append({
            'NOMECURSO': curso,
            'PROUNI_SOBRA_FALTA': prouni_saldo,
            'FILANTROPIA_SOBRA_FALTA': filantropia_saldo
        })
    
    # Criar DataFrame
    df = pd.DataFrame(dados)
    
    # Salvar como Excel
    df.to_excel('dados_conformidade_exemplo.xlsx', index=False)
    print("Arquivo 'dados_conformidade_exemplo.xlsx' criado com sucesso!")
    print("\nPrimeiras 5 linhas:")
    print(df.head())
    print(f"\nTotal de cursos: {len(df)}")
    print(f"Saldo geral PROUNI: {df['PROUNI_SOBRA_FALTA'].sum()}")
    print(f"Saldo geral Filantropia: {df['FILANTROPIA_SOBRA_FALTA'].sum()}")

if __name__ == "__main__":
    criar_dados_exemplo()