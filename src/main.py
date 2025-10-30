import sys
from PySide6.QtWidgets import QApplication, QMessageBox
from src.gui.main_window import MainWindow
from src.gui.activation_window import ActivationWindow
from src import license_manager


def start_gui():
    app = QApplication(sys.argv)

    # --- LÓGICA DE VERIFICAÇÃO DE LICENÇA ---
    status = license_manager.check_license_status()

    if status == "valid":
        main_window = MainWindow()
        sys.exit(app.exec())
    else:
        # Mostra a janela de ativação
        activation_dialog = ActivationWindow()
        # Se o usuário ativar com sucesso (dialog.exec() retorna 1)
        if activation_dialog.exec():
            # Fecha a janela de ativação e inicia a principal
            main_window = MainWindow()
            sys.exit(app.exec())
        else:
            # Se o usuário fechar a janela de ativação, o programa encerra
            sys.exit(0)


if __name__ == "__main__":
    start_gui()
