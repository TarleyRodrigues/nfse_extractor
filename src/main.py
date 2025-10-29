"""
Módulo Principal (Ponto de Entrada)

Orquestra o fluxo completo da aplicação:
1. Localiza os arquivos PDF de entrada.
2. Itera sobre cada PDF, chamando o processador para extrair dados brutos.
3. Utiliza o parser para limpar e formatar os dados extraídos.
4. Agrega os dados limpos de todas as notas.
5. Envia os dados agregados para o excel_writer para gerar a planilha.
"""
import os
from typing import List, Dict, Any

# Importa os módulos e configurações necessárias do nosso pacote 'src'
from . import config
from . import pdf_processor
from . import data_parser
from . import excel_writer  # <-- NOVA IMPORTAÇÃO


def main() -> None:
    """Função principal que orquestra o processo de ETL."""
    print("Iniciando o processo de extração de NFSe...")

    pdf_files = [f for f in os.listdir(
        config.PDF_SAMPLES_DIR) if f.endswith('.pdf')]

    if not pdf_files:
        print(
            f"Nenhum arquivo PDF encontrado no diretório: {config.PDF_SAMPLES_DIR}")
        return

    print(f"Encontrados {len(pdf_files)} PDFs para processar.")

    all_nfse_data: List[Dict[str, Any]] = []

    for pdf_file in pdf_files:
        pdf_path = os.path.join(config.PDF_SAMPLES_DIR, pdf_file)
        print(f"\nProcessando arquivo: {pdf_file}")

        raw_data = pdf_processor.extract_data_from_pdf(pdf_path)

        if not raw_data:
            print(
                f"Falha ao extrair dados de {pdf_file}. Pulando para o próximo.")
            continue

        clean_data = {
            "numero_nf": data_parser.parse_number(raw_data.get("numero_nf")),
            "data_emissao": data_parser.parse_date(raw_data.get("data_emissao")),
            "cnpj_prestador": data_parser.parse_cnpj(raw_data.get("cnpj_prestador")),
            "nome_prestador": data_parser.clean_text(raw_data.get("nome_prestador")),
            "cnpj_tomador": data_parser.parse_cnpj(raw_data.get("cnpj_tomador")),
            "nome_tomador": data_parser.clean_text(raw_data.get("nome_tomador")),
            "valor_servico": data_parser.parse_monetary(raw_data.get("valor_servico")),
            "discriminacao": data_parser.clean_text(raw_data.get("discriminacao")),
            "arquivo_origem": pdf_file
        }

        all_nfse_data.append(clean_data)
        print("Dados extraídos e limpos com sucesso.")

    print("\n--- Processamento Concluído ---")

    # --- MUDANÇA PRINCIPAL: De 'print' para 'generate_excel_report' ---
    # O código antigo que imprimia os dados no console foi removido.
    # Agora, chamamos nosso novo módulo para fazer o trabalho final.
    excel_writer.generate_excel_report(all_nfse_data)


if __name__ == "__main__":
    main()
