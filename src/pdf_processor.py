"""
Módulo de Processamento de PDF

Responsável pela lógica central de abrir, ler e extrair dados brutos
de um arquivo PDF de NFSe, utilizando um mapa de coordenadas dinâmico.
"""
import pdfplumber
from typing import Dict, Any

# REMOVEMOS: from .config import FIELD_MAP

# A assinatura da função agora inclui o parâmetro 'field_map'


def extract_data_from_pdf(pdf_path: str, field_map: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extrai dados de um único arquivo PDF de NFSe com base em um mapa de campos.

    Args:
        pdf_path (str): O caminho completo para o arquivo PDF.
        field_map (Dict[str, Any]): O dicionário de layout com os campos e
                                    suas coordenadas.

    Returns:
        Dict[str, Any]: Um dicionário com os dados brutos extraídos.
                        Retorna None em caso de erro.
    """
    extracted_data = {}

    try:
        with pdfplumber.open(pdf_path) as pdf:
            # Itera sobre o mapa de campos RECEBIDO COMO PARÂMETRO
            for field_name, params in field_map.items():
                page_num = params['page']
                # Converte a lista de coordenadas do JSON para uma tupla
                coords = tuple(params['coords'])

                page = pdf.pages[page_num]
                box = page.crop(coords)
                raw_text = box.extract_text()

                extracted_data[field_name] = raw_text.strip(
                ) if raw_text else ""

    except Exception as e:
        print(f"Erro ao processar o arquivo PDF '{pdf_path}': {e}")
        return None

    return extracted_data
