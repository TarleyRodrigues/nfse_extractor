"""
Módulo de Processamento de PDF

Responsável pela lógica central de abrir, ler e extrair dados brutos
de um arquivo PDF de NFSe, utilizando o mapa de coordenadas definido no config.
"""
import pdfplumber
from typing import Dict, Any

# Importa o mapa de campos do nosso arquivo de configuração
from .config import FIELD_MAP


def extract_data_from_pdf(pdf_path: str) -> Dict[str, Any]:
    """
    Extrai dados de um único arquivo PDF de NFSe com base em coordenadas.

    Args:
        pdf_path (str): O caminho completo para o arquivo PDF.

    Returns:
        Dict[str, Any]: Um dicionário com os dados brutos extraídos, onde as
                        chaves são os nomes dos campos definidos em FIELD_MAP.
                        Retorna None em caso de erro ao abrir o PDF.
    """
    extracted_data = {}

    try:
        with pdfplumber.open(pdf_path) as pdf:
            # Itera sobre o mapa de campos definido no config
            for field_name, params in FIELD_MAP.items():
                page_num = params['page']
                coords = params['coords']

                # Seleciona a página correta
                page = pdf.pages[page_num]

                # "Corta" a região da página definida pelas coordenadas
                # A tupla de coordenadas é desempacotada com o operador *
                box = page.crop(coords)

                # Extrai o texto da região cortada
                raw_text = box.extract_text()

                # Armazena o texto bruto (removendo espaços em branco extras)
                # Se nada for encontrado, armazena uma string vazia para consistência
                extracted_data[field_name] = raw_text.strip(
                ) if raw_text else ""

    except Exception as e:
        # Em um aplicativo comercial, aqui seria um bom lugar para logar o erro
        print(f"Erro ao processar o arquivo PDF '{pdf_path}': {e}")
        return None

    return extracted_data
