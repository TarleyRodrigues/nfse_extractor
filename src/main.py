"""
Módulo Principal (Ponto de Entrada com CLI)

Orquestra o fluxo da aplicação e aceita argumentos de linha de comando
para definir o layout, diretório de entrada e arquivo de saída.
"""
import os
import argparse  # <-- Importa a biblioteca para parsing de argumentos
from typing import List, Dict, Any

from . import config
from . import pdf_processor
from . import data_parser
from . import excel_writer


def main() -> None:
    """Função principal que orquestra o processo de ETL."""

    # --- CONFIGURAÇÃO DA CLI COM ARGPARSE ---
    parser = argparse.ArgumentParser(
        description="Extrai dados de NFSe em PDF e gera um relatório em Excel."
    )
    parser.add_argument(
        "-l", "--layout",
        type=str,
        required=True,
        help="Nome do arquivo de layout (sem a extensão .json) a ser usado. Ex: 'prefeitura_sp'."
    )
    parser.add_argument(
        "-i", "--input-dir",
        type=str,
        default=str(config.PDF_SAMPLES_DIR),
        help=f"Caminho para o diretório com os PDFs. Padrão: '{config.PDF_SAMPLES_DIR}'"
    )
    parser.add_argument(
        "-o", "--output-file",
        type=str,
        default="relatorio_nfse.xlsx",
        help="Nome do arquivo Excel de saída a ser salvo na pasta 'output'. Padrão: 'relatorio_nfse.xlsx'"
    )

    args = parser.parse_args()

    # --- FIM DA CONFIGURAÇÃO DA CLI ---

    print("Iniciando o processo de extração de NFSe...")

    try:
        print(f"Carregando layout: '{args.layout}'")
        layout_map = config.load_layout(args.layout)
    except Exception as e:
        print(f"ERRO CRÍTICO ao carregar o layout: {e}")
        return

    # Valida se o diretório de entrada existe
    if not os.path.isdir(args.input_dir):
        print(
            f"ERRO: O diretório de entrada especificado não existe: '{args.input_dir}'")
        return

    pdf_files = [f for f in os.listdir(
        args.input_dir) if f.lower().endswith('.pdf')]

    if not pdf_files:
        print(f"Nenhum arquivo PDF encontrado no diretório: {args.input_dir}")
        return

    print(
        f"Encontrados {len(pdf_files)} PDFs para processar em '{args.input_dir}'.")

    all_nfse_data: List[Dict[str, Any]] = []

    for pdf_file in pdf_files:
        pdf_path = os.path.join(args.input_dir, pdf_file)
        print(f"\nProcessando arquivo: {pdf_file}")

        raw_data = pdf_processor.extract_data_from_pdf(pdf_path, layout_map)

        if not raw_data:
            print(
                f"Falha ao extrair dados de {pdf_file}. Pulando para o próximo.")
            continue

        # Esta lógica de limpeza dinâmica pode ser aprimorada no futuro
        clean_data = {"arquivo_origem": pdf_file}
        for field, raw_value in raw_data.items():
            parser_function_name = f"parse_{field}"
            # Usa um valor padrão 'clean_text' se um parser específico não for encontrado
            parser_function = getattr(
                data_parser, parser_function_name, data_parser.clean_text)
            clean_data[field] = parser_function(raw_value)

        all_nfse_data.append(clean_data)
        print("Dados extraídos e limpos com sucesso.")

    print("\n--- Processamento Concluído ---")
    excel_writer.generate_excel_report(
        all_nfse_data, filename=args.output_file)


if __name__ == "__main__":
    main()
