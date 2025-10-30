"""
API de Licenciamento Simples com Flask.

Este é um protótipo de servidor de licenciamento. Em um ambiente de produção,
ele seria conectado a um banco de dados real (como PostgreSQL ou MySQL).
"""
from flask import Flask, request, jsonify
import datetime

# --- Nosso Banco de Dados Falso (em memória) ---
# Em produção, isso viria de um banco de dados real.
# Chave: a chave de licença
# Valor: um dicionário com o status e a data de expiração.
LICENSES_DB = {
    "TRIAL-12345-ABCDE": {
        "status": "active",
        "expires_on": "2099-12-31"  # Uma licença de teste que nunca expira
    },
    "EXPIRED-67890-FGHIJ": {
        "status": "active",
        "expires_on": "2020-01-01"  # Uma licença que já expirou
    },
    "REVOKED-11223-KLMNO": {
        "status": "revoked",  # Uma licença que foi revogada manualmente
        "expires_on": "2099-12-31"
    }
}

app = Flask(__name__)


@app.route('/validate', methods=['POST'])
def validate_license():
    """
    Endpoint para validar uma chave de licença.
    Espera um JSON no corpo da requisição: {"license_key": "SUA-CHAVE-AQUI"}
    """
    data = request.get_json()
    if not data or 'license_key' not in data:
        return jsonify({"status": "error", "message": "Requisição inválida."}), 400

    license_key = data['license_key']

    # Busca a licença no nosso "banco de dados"
    license_info = LICENSES_DB.get(license_key)

    if not license_info:
        return jsonify({"status": "invalid", "message": "Chave de licença não encontrada."})

    # Verifica se a licença foi revogada
    if license_info["status"] == "revoked":
        return jsonify({"status": "revoked", "message": "Esta licença foi revogada."})

    # Verifica a data de expiração
    try:
        expires_on = datetime.datetime.strptime(
            license_info["expires_on"], "%Y-%m-%d").date()
        if expires_on < datetime.date.today():
            return jsonify({
                "status": "expired",
                "message": "Sua licença expirou.",
                "expires_on": str(expires_on)
            })
    except ValueError:
        return jsonify({"status": "error", "message": "Formato de data inválido no servidor."}), 500

    # Se tudo estiver ok, a licença é válida
    return jsonify({
        "status": "valid",
        "message": "Licença ativa.",
        "expires_on": license_info["expires_on"]
    })


if __name__ == '__main__':
    # Roda o servidor de desenvolvimento.
    # O host='0.0.0.0' permite que ele seja acessível na sua rede local.
    app.run(host='0.0.0.0', port=5000, debug=True)
