# Extrator de Notas Fiscais de Serviço (NFSe) - Prefeitura de São Paulo

Este projeto é uma ferramenta de automação (ETL) desenvolvida em Python para extrair dados de Notas Fiscais de Serviço Eletrônicas (NFSe) da Prefeitura de São Paulo em formato PDF e consolidá-los em uma planilha Excel (.xlsx).

## Visão Geral

O objetivo principal é eliminar a digitação manual de dados, economizando tempo e reduzindo erros. O fluxo de trabalho é simples:

1.  **Entrada:** PDFs de NFSe são colocados em uma pasta de entrada.
2.  **Processamento:** A aplicação lê cada PDF, identifica e extrai campos-chave usando uma combinação de análise de layout (coordenadas) e reconhecimento de texto.
3.  **Saída:** Os dados extraídos de todos os PDFs são salvos de forma estruturada em um único arquivo Excel na pasta `output/`.

## Stack de Tecnologia

*   **Linguagem:** Python 3.10+
*   **Extração de PDF (Layout):** `pdfplumber`
*   **Extração de PDF (OCR):** `pytesseract` com `OpenCV`
*   **Manipulação de Dados:** `pandas`
*   **Geração de Excel:** `openpyxl`
*   **Ambiente:** `venv`

## Estrutura do Projeto
nfse_extractor/
├── .git/
├── .gitignore
├── .venv/
├── src/
│ ├── init.py
│ ├── main.py
│ ├── pdf_processor.py
│ ├── data_parser.py
│ ├── excel_writer.py
│ └── config.py
├── tests/
├── output/
├── pdf_samples/
├── requirements.txt
└── README.md