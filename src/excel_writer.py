"""
Módulo de Geração de Planilhas Excel
"""
import pandas as pd
from typing import List, Dict, Any

# A importação do config não é mais necessária aqui
# from .config import OUTPUT_DIR

# A assinatura da função agora espera o caminho completo


def generate_excel_report(data: List[Dict[str, Any]], output_path: str) -> None:
    """
    Gera um relatório Excel a partir de uma lista de dicionários.

    Args:
        data (List[Dict[str, Any]]): A lista de dados processados.
        output_path (str): O caminho completo onde o arquivo Excel será salvo.
    """
    if not data:
        print("Nenhum dado para gerar o relatório. O arquivo Excel não será criado.")
        return

    try:
        df = pd.DataFrame(data)

        # A variável output_path já é o caminho completo, não precisamos mais construí-lo
        print(f"\nGerando relatório Excel em: {output_path}")

        df.to_excel(output_path, index=False, engine='openpyxl')

        print("Relatório Excel gerado com sucesso!")

    except Exception as e:
        print(f"ERRO: Não foi possível gerar o arquivo Excel. Detalhes: {e}")
