"""
Módulo de Limpeza e Formatação de Dados (Parser)

Contém funções especializadas para limpar, formatar e validar os dados brutos
extraídos do PDF. Cada função utiliza expressões regulares (Regex) para
isolar a informação útil.
"""
import re
from typing import Optional


def parse_cnpj(raw_text: str) -> Optional[str]:
    """
    Localiza e limpa um número de CNPJ/CPF do texto.
    Retorna apenas os dígitos.

    Exemplo: 'CNPJ: 12.345.678/0001-99' -> '12345678000199'
    """
    if not raw_text:
        return None
    # Regex para encontrar 14 dígitos com ou sem formatação
    match = re.search(r'\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}', raw_text)
    if match:
        # Remove todos os caracteres não numéricos
        return re.sub(r'\D', '', match.group(0))
    return None


def parse_monetary(raw_text: str) -> Optional[float]:
    """
    Converte um valor monetário em formato de string para float.
    Lida com 'R$', pontos de milhar e vírgula decimal.

    Exemplo: 'R$ 1.234,56' -> 1234.56
    """
    if not raw_text:
        return None
    # Remove 'R$', espaços e o ponto de milhar. Troca vírgula por ponto.
    cleaned_text = raw_text.replace(
        'R$', '').strip().replace('.', '').replace(',', '.')

    # Tenta converter para float
    try:
        return float(cleaned_text)
    except (ValueError, TypeError):
        return None


def parse_date(raw_text: str) -> Optional[str]:
    """
    Localiza e formata uma data no padrão DD/MM/AAAA.

    Exemplo: 'Emitida em: 01/01/2024' -> '01/01/2024'
    """
    if not raw_text:
        return None
    # Regex para encontrar datas no formato dd/mm/aaaa
    match = re.search(r'(\d{2}/\d{2}/\d{4})', raw_text)
    if match:
        return match.group(1)
    return None


def parse_number(raw_text: str) -> Optional[int]:
    """
    Extrai o primeiro número inteiro encontrado no texto.

    Exemplo: 'Número da Nota: 000123' -> 123
    """
    if not raw_text:
        return None
    match = re.search(r'\d+', raw_text)
    if match:
        return int(match.group(0))
    return None


def clean_text(raw_text: str) -> str:
    """
    Limpeza genérica de texto: remove quebras de linha excessivas e espaços.
    Útil para campos como 'nome' ou 'discriminação'.
    """
    if not raw_text:
        return ""
    # Substitui múltiplas quebras de linha e espaços por um único espaço
    return re.sub(r'\s+', ' ', raw_text).strip()
