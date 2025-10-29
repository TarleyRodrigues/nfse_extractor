"""
Módulo Principal (Ponto de Entrada) - Refatorado para Layouts Dinâmicos
"""

from . import excel_writer
from . import data_parser
from . import pdf_processor
from . import config
from typing import List, Dict, Any
import os
print("--- SCRIPT main.py EXECUTANDO ---")


def main() -> None:
    """Função principal que orquestra o processo de ETL."""
    print("Iniciando o processo de extração de NFSe...")

    # 1. Carregar o layout desejado
    try:
        layout_name = "prefeitura_sp"
        print(f"Carregando layout: '{layout_name}'")
        layout_map = config.load_layout(layout_name)
        print(f"DEBUG: Layout carregado com sucesso: {layout_map}")
    except Exception as e:
        # --- MUDANÇA IMPORTANTE ---
        # Imprime o erro detalhado antes de encerrar.
        print(f"ERRO CRÍTICO ao carregar o layout: {e}")
        # Adiciona o traceback para vermos a origem do erro
        import traceback
        traceback.print_exc()
        return

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

        # 2. Passar o layout carregado para o processador
        raw_data = pdf_processor.extract_data_from_pdf(pdf_path, layout_map)

        if not raw_data:
            print(
                f"Falha ao extrair dados de {pdf_file}. Pulando para o próximo.")
            continue

        # 3. Tornar a limpeza de dados mais dinâmica
        clean_data = {"arquivo_origem": pdf_file}
        for field, raw_value in raw_data.items():
            parser_function_name = f"parse_{field}" if "cnpj" in field or "valor" in field or "data" in field or "numero" in field else "clean_text"
            parser_function = getattr(
                data_parser, parser_function_name, data_parser.clean_text)
            clean_data[field] = parser_function(raw_value)

        all_nfse_data.append(clean_data)
        print("Dados extraídos e limpos com sucesso.")

    print("\n--- Processamento Concluído ---")
    excel_writer.generate_excel_report(all_nfse_data)


if __name__ == "__main__":
    main()
