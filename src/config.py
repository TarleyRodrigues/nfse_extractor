"""
Módulo de Configuração

Centraliza todas as configurações do projeto, como mapeamento de campos,
coordenadas de extração e caminhos de diretórios.
"""
import json
from pathlib import Path
from typing import Dict, Any

# --- Caminhos do Projeto ---
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"
PDF_SAMPLES_DIR = BASE_DIR / "pdf_samples"
LAYOUTS_DIR = BASE_DIR / "layouts"  # <-- Caminho para os arquivos de layout

# Garante que os diretórios existam
OUTPUT_DIR.mkdir(exist_ok=True)
PDF_SAMPLES_DIR.mkdir(exist_ok=True)
LAYOUTS_DIR.mkdir(exist_ok=True)


def load_layout(layout_name: str) -> Dict[str, Any]:
    """
    Carrega um mapa de campos (layout) de um arquivo JSON.

    Args:
        layout_name (str): O nome do arquivo de layout (sem a extensão .json).

    Returns:
        Dict[str, Any]: O dicionário contendo o mapa de campos.
                        Lança uma exceção se o arquivo não for encontrado ou for inválido.
    """
    layout_path = LAYOUTS_DIR / f"{layout_name}.json"
    try:
        with open(layout_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"ERRO: Arquivo de layout '{layout_path}' não encontrado.")
        raise
    except json.JSONDecodeError:
        print(
            f"ERRO: O arquivo de layout '{layout_path}' não é um JSON válido.")
        raise
