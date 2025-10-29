"""
Módulo de Geração de Planilhas Excel

Responsável por receber os dados processados e salvá-los em um arquivo .xlsx
utilizando a biblioteca pandas.
"""
import pandas as pd
from typing import List, Dict, Any

# Importa o diretório de saída do nosso arquivo de configuração
from .config import OUTPUT_DIR


def generate_excel_report(data: List[Dict[str, Any]], filename: str = "relatorio_nfse.xlsx") -> None:
    """
    Gera um relatório Excel a partir de uma lista de dicionários.

    Args:
        data (List[Dict[str, Any]]): A lista de dados extraídos e limpos,
                                     onde cada dicionário representa uma NFSe.
        filename (str, optional): O nome do arquivo Excel a ser gerado.
                                  O padrão é "relatorio_nfse.xlsx".
    """
    if not data:
        print("Nenhum dado para gerar o relatório. O arquivo Excel não será criado.")
        return

    try:
        # Converte a lista de dicionários em um DataFrame do pandas
        # O pandas inteligentemente usa as chaves do dicionário como nomes de coluna
        df = pd.DataFrame(data)

        # Constrói o caminho completo para o arquivo de saída usando pathlib
        output_path = OUTPUT_DIR / filename

        print(f"\nGerando relatório Excel em: {output_path}")

        # Salva o DataFrame no arquivo Excel.
        # index=False é crucial para não salvar o índice do DataFrame (0, 1, 2...)
        # na primeira coluna da planilha.
        df.to_excel(output_path, index=False, engine='openpyxl')

        print("Relatório Excel gerado com sucesso!")

    except Exception as e:
        # Captura de erro para casos como falta de permissão de escrita
        print(f"ERRO: Não foi possível gerar o arquivo Excel. Detalhes: {e}")
