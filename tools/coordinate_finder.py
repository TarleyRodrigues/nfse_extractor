"""
Ferramenta Auxiliar para Localização de Coordenadas (Versão 4.1 - Corrigida).

Corrige um typo na constante de conversão de cores do OpenCV (COLOR_RGB2BGR).
"""
import cv2
import pdfplumber
import numpy as np
import sys
from pathlib import Path

# --- Variáveis de Configuração ---
RESOLUTION = 200
points = []
image_display = None


def mouse_callback(event, x, y, flags, param):
    """Função de callback para eventos do mouse."""
    global points, image_display

    if event == cv2.EVENT_LBUTTONDOWN:
        points.append((x, y))
        cv2.circle(image_display, (x, y), 5, (0, 0, 255), -1)

        if len(points) == 2:
            cv2.rectangle(image_display, points[0], points[1], (0, 255, 0), 2)

            conversion_factor = 72 / RESOLUTION
            pdf_points = [
                (p[0] * conversion_factor, p[1] * conversion_factor) for p in points
            ]

            x0 = min(pdf_points[0][0], pdf_points[1][0])
            top = min(pdf_points[0][1], pdf_points[1][1])
            x1 = max(pdf_points[0][0], pdf_points[1][0])
            bottom = max(pdf_points[0][1], pdf_points[1][1])

            print("\n--- Coordenadas Finais (em Pontos de PDF) ---")
            print(
                f"Copie e cole no seu JSON: [{x0:.2f}, {top:.2f}, {x1:.2f}, {bottom:.2f}]")

            points = []

        cv2.imshow("PDF Page", image_display)


def main():
    global image_display

    if len(sys.argv) != 3:
        print(
            'Uso: python tools/coordinate_finder.py "caminho/para/seu.pdf" <numero_pagina>')
        return

    pdf_path = Path(sys.argv[1])
    page_number = int(sys.argv[2]) - 1

    if not pdf_path.exists():
        print(f"ERRO: PDF não encontrado em '{pdf_path}'")
        return

    try:
        with pdfplumber.open(pdf_path) as pdf:
            if not (0 <= page_number < len(pdf.pages)):
                print(f"ERRO: Página inválida.")
                return

            page = pdf.pages[page_number]
            pil_image = page.to_image(resolution=RESOLUTION).original

            # --- LINHA CORRIGIDA ---
            # Usando '2' no lugar de '_'
            image_display = cv2.cvtColor(
                np.array(pil_image), cv2.COLOR_RGB2BGR)

        cv2.namedWindow("PDF Page")
        cv2.setMouseCallback("PDF Page", mouse_callback)
        print("Janela aberta. Clique para selecionar a área. Pressione 'q' para sair.")

        while True:
            cv2.imshow("PDF Page", image_display)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cv2.destroyAllWindows()

    except Exception as e:
        print(f"Ocorreu um erro: {e}")


if __name__ == "__main__":
    main()
