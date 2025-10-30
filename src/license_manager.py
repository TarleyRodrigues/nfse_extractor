"""
Módulo de Gerenciamento de Licença.

Lida com a validação da licença contra a API remota e o armazenamento
local do status da licença.
"""
import requests
import json
import os
from pathlib import Path
from typing import Dict, Any

# O URL da nossa API de licenciamento
API_URL = "http://127.0.0.1:5000/validate"

# Onde salvaremos o arquivo de licença local
LICENSE_FILE = Path(os.path.expanduser("~")) / ".nfse_extractor_license.json"


def validate_license_key(license_key: str) -> Dict[str, Any]:
    """
    Contata a API para validar uma chave de licença.
    """
    try:
        response = requests.post(
            API_URL, json={"license_key": license_key}, timeout=10)
        response.raise_for_status()  # Lança um erro para status 4xx ou 5xx
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"status": "api_error", "message": f"Erro de conexão: {e}"}


def save_local_license(data: Dict[str, Any]):
    """
    Salva os dados da licença localmente em um arquivo JSON.
    """
    try:
        with open(LICENSE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f)
    except IOError as e:
        print(f"Erro ao salvar arquivo de licença: {e}")


def load_local_license() -> Dict[str, Any]:
    """
    Carrega os dados da licença do arquivo local.
    """
    if not LICENSE_FILE.exists():
        return None
    try:
        with open(LICENSE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError):
        return None


def check_license_status() -> str:
    """
    Verificação principal do status da licença.
    Retorna 'valid', 'invalid' ou 'api_error'.
    """
    local_license = load_local_license()
    if not local_license:
        return "invalid"  # Nenhuma licença local encontrada

    # Lógica de validação periódica (simplificada por enquanto)
    # Em um produto real, verificaríamos a data da última validação aqui.

    # Revalida com o servidor
    result = validate_license_key(local_license.get("license_key"))

    if result["status"] == "valid":
        # Atualiza o arquivo local com os dados mais recentes (ex: nova data de expiração)
        save_local_license({
            "license_key": local_license.get("license_key"),
            "status": "valid",
            "expires_on": result.get("expires_on")
        })
        return "valid"
    else:
        # Se a validação online falhou, invalida a licença local
        save_local_license({
            "license_key": local_license.get("license_key"),
            "status": "invalid"
        })
        return "invalid"
