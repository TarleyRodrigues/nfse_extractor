"""
Ferramenta Auxiliar para Localização de Coordenadas em PDFs (Versão 2.0).

Esta versão redimensiona a página do PDF para caber confortavelmente na tela,
enquanto recalcula os cliques do mouse para fornecer as coordenadas precisas
correspondentes ao PDF original de alta resolução.
"""
import cv2
import pdfplumber
import numpy as np
import sys
from pathlib import Path

# Variáveis globais para armazenar pontos e a proporção de redimensionamento
points = []
resize_ratio = 1.0
image_clone = None


def mouse_callback(event, x, y, flags, param):
    """Função de callback para eventos do mouse."""
    global points, image_clone, resize_ratio

    if event == cv2.EVENT_LBUTTONDOWN:
        # Armazena as coordenadas do clique na imagem redimensionada
        points.append((x, y))

        # Desenha na imagem de exibição (a cópia redimensionada)
        cv2.circle(image_clone, (x, y), 5, (0, 0, 255), -1)
        cv2.imshow("PDF Page", image_clone)

        if len(points) == 2:
            cv2.rectangle(image_clone, points[0], points[1], (0, 255, 0), 2)
            cv2.imshow("PDF Page", image_clone)

            # --- CONVERSÃO DAS COORDENADAS ---
            # Converte as coordenadas do clique (da imagem pequena) de volta
            # para as coordenadas da imagem original (grande).
            original_points = [
                (int(p[0] / resize_ratio), int(p[1] / resize_ratio)) for p in points]

            x0 = min(original_points[0][0], original_points[1][0])
            top = min(original_points[0][1], original_points[1][1])
            x1 = max(original_points[0][0], original_points[1][0])
            bottom = max(original_points[0][1], original_points[1][1])

            print("\n--- Coordenadas Encontradas (tamanho original)! ---")
            print(
                f"Copie e cole no seu arquivo JSON: [{x0}, {top}, {x1}, {bottom}]")

            points = []


def get_screen_resolution():
    """Tenta obter a resolução da tela de forma simples (pode não funcionar em todos os sistemas)."""
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        return root.winfo_screenwidth(), root.winfo_screenheight()
    except Exception:
        # Retorna um valor padrão seguro se o tkinter não estiver disponível
        return 1920, 1080


def main():
    global image_clone, resize_ratio

    if len(sys.argv) != 3:
        print(
            'Uso: python tools/coordinate_finder.py "caminho/para/seu.pdf" <numero_pagina>')
        return

    pdf_path = Path(sys.argv[1])
    try:
        page_number = int(sys.argv[2])
    except ValueError:
        print("ERRO: O número da página deve ser um inteiro.")
        return

    if not pdf_path.exists():
        print(f"ERRO: Arquivo PDF não encontrado em '{pdf_path}'")
        return

    print("Abrindo PDF... Pressione 'q' na janela da imagem para sair.")

    try:
        with pdfplumber.open(pdf_path) as pdf:
            if not (0 < page_number <= len(pdf.pages)):
                print(
                    f"ERRO: Número de página inválido. O PDF tem {len(pdf.pages)} páginas.")
                return

            page = pdf.pages[page_number - 1]
            pil_image = page.to_image(resolution=200).original
            image_original = cv2.cvtColor(
                np.array(pil_image), cv2.COLOR_RGB2BGR)

        # --- LÓGICA DE REDIMENSIONAMENTO ---
        screen_w, screen_h = get_screen_resolution()
        max_h = int(screen_h * 0.9)  # Usa 90% da altura da tela

        original_h, original_w = image_original.shape[:2]

        # Calcula a proporção apenas se a imagem for maior que a tela
        if original_h > max_h:
            resize_ratio = max_h / original_h
            new_w = int(original_w * resize_ratio)
            new_h = int(original_h * resize_ratio)

            # Redimensiona a imagem para exibição
            image_display = cv2.resize(
                image_original, (new_w, new_h), interpolation=cv2.INTER_AREA)
        else:
            image_display = image_original
            resize_ratio = 1.0  # Nenhuma alteração

        image_clone = image_display.copy()

        cv2.namedWindow("PDF Page")
        cv2.setMouseCallback("PDF Page", mouse_callback)

        while True:
            cv2.imshow("PDF Page", image_clone)
            key = cv2.waitKey(1) & 0xFF

            if key == ord('q'):
                break
            elif key == ord('r'):
                print("\nSeleção resetada. Escolha dois novos pontos.")
                image_clone = image_display.copy()  # Reseta para a imagem redimensionada
                points = []

        cv2.destroyAllWindows()

    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")


if __name__ == "__main__":
    main()
