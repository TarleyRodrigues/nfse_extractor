"""
Ferramenta de Depuração de Layout (Versão 2.1 - Compatível)

Ajusta a sintaxe de desenho para ser compatível com diferentes versões do pdfplumber,
passando os atributos de estilo (cor, espessura) via dicionários.
"""
import pdfplumber
import sys
from pathlib import Path


def debug_pdf_layout(pdf_path: Path, page_number: int):
    """
    Gera uma imagem de uma página de PDF com caixas de depuração.
    """
    print(f"Processando '{pdf_path.name}', página {page_number + 1}...")
    try:
        with pdfplumber.open(pdf_path) as pdf:
            if not (0 <= page_number < len(pdf.pages)):
                print(
                    f"ERRO: Página inválida. O PDF tem {len(pdf.pages)} páginas.")
                return

            page = pdf.pages[page_number]
            im = page.to_image(resolution=150)

            # --- SINTAXE DE DESENHO CORRIGIDA ---
            # Define o estilo do retângulo (contorno vermelho)
            rect_style = {
                "stroke": "red",         # Cor do contorno
                "stroke_width": 1,       # Espessura do contorno
            }
            # Define o estilo da linha (linha azul)
            line_style = {
                "stroke": "blue",
                "stroke_width": 2,
            }

            # Desenha os retângulos e linhas usando a sintaxe compatível
            im.draw_rects(page.extract_words(), **rect_style)
            im.draw_lines(page.lines, **line_style)

            # Para depuração: imprime todas as palavras e suas coordenadas no terminal
            print("\n--- Coordenadas de Todas as Palavras Encontradas ---")
            for word in page.extract_words():
                # Arredonda os valores para facilitar a leitura
                x0, top, x1, bottom = round(word["x0"], 2), round(
                    word["top"], 2), round(word["x1"], 2), round(word["bottom"], 2)
                print(
                    f"Texto: '{word['text']}' -> Coords: (x0: {x0}, top: {top}, x1: {x1}, bottom: {bottom})")

            # Salva a imagem resultante
            output_image_path = f"debug_page_{page_number + 1}.png"
            im.save(output_image_path, format="PNG")

            print("-" * 50)
            print(
                f"SUCESSO! Imagem de depuração salva em: '{output_image_path}'")
            print(
                "Abra a imagem e use a lista de coordenadas impressa acima para encontrar os valores exatos.")
            print("-" * 50)

    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('Uso: python tools/debug_layout.py "caminho/para/seu.pdf" <numero_pagina>')
        sys.exit(1)

    pdf_file = Path(sys.argv[1])
    page_num = int(sys.argv[2]) - 1

    if not pdf_file.exists():
        print(f"ERRO: Arquivo PDF não encontrado em '{pdf_file}'")
        sys.exit(1)

    debug_pdf_layout(pdf_file, page_num)
