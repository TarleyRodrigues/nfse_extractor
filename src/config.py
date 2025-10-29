"""
Módulo de Configuração

Centraliza todas as configurações do projeto, como mapeamento de campos,
coordenadas de extração e caminhos de diretórios.
"""
from pathlib import Path

# --- Caminhos do Projeto ---
# Define o caminho base do projeto de forma robusta
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"
PDF_SAMPLES_DIR = BASE_DIR / "pdf_samples"

# Garante que os diretórios de saída e de amostras existam
OUTPUT_DIR.mkdir(exist_ok=True)
PDF_SAMPLES_DIR.mkdir(exist_ok=True)


# --- Mapeamento de Campos da NFSe ---
# Dicionário que serve como "mapa" para a extração de dados do PDF.
# Chave: Nome do campo (será o cabeçalho no Excel).
# Valor: Dicionário com os parâmetros para extração.
#   - 'page': O número da página (começando em 0).
#   - 'coords': A tupla (x0, top, x1, bottom) que define a "caixa" (bounding box)
#               onde o dado está localizado na página.

FIELD_MAP = {
    "numero_nf": {
        "page": 0,
        "coords": (470, 58, 560, 72)  # Exemplo: canto superior direito
    },
    "data_emissao": {
        "page": 0,
        "coords": (470, 80, 560, 92)  # Exemplo: logo abaixo do número da NF
    },
    "cnpj_prestador": {
        "page": 0,
        "coords": (20, 180, 170, 200)  # Exemplo: seção "Prestador de Serviços"
    },
    "nome_prestador": {
        "page": 0,
        "coords": (20, 160, 400, 180)  # Exemplo: abaixo do CNPJ do prestador
    },
    "cnpj_tomador": {
        "page": 0,
        "coords": (20, 280, 170, 300)  # Exemplo: seção "Tomador de Serviços"
    },
    "nome_tomador": {
        "page": 0,
        "coords": (20, 260, 400, 280)  # Exemplo: abaixo do CNPJ do tomador
    },
    "valor_servico": {
        "page": 0,
        # Exemplo: no rodapé da seção de valores
        "coords": (450, 615, 565, 630)
    },
    "discriminacao": {
        "page": 0,
        "coords": (20, 400, 570, 550)  # Exemplo: campo grande de descrição
    }
}
