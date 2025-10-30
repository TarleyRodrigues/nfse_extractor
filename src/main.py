"""
Ponto de Entrada Principal da Aplicação NFSe Extractor.

Este script inicia a interface gráfica (GUI).
"""
import sys
from PySide6.QtWidgets import QApplication
from src.gui.main_window import MainWindow


def start_gui():
    """Inicializa e executa a aplicação gráfica."""
    app = QApplication(sys.argv)
    main_window = MainWindow()
    sys.exit(app.exec())


if __name__ == "__main__":
    start_gui()
