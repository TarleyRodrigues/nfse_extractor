"""
Controller da Janela Principal da Aplicação.

Responsável por carregar a interface do usuário (View), conectar os sinais
(eventos de clique) aos slots (funções de lógica) e interagir com o
Model (lógica de negócios de extração).
"""
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # Carrega a interface do arquivo .ui
        ui_file_path = "src/gui/ui/main_window.ui"
        ui_file = QFile(ui_file_path)
        ui_file.open(QFile.ReadOnly)

        loader = QUiLoader()
        self.window = loader.load(ui_file)
        ui_file.close()

        # Conecta os sinais aos slots (eventos -> funções)
        self.window.btn_select_pdfs.clicked.connect(self.select_pdfs)

        # Exibe a janela
        self.window.show()

    def select_pdfs(self):
        """
        Abre uma caixa de diálogo para o usuário selecionar múltiplos arquivos PDF.
        """
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Selecionar arquivos PDF",
            "",  # Diretório inicial
            "Arquivos PDF (*.pdf)"
        )

        if file_paths:
            # Limpa a lista atual e adiciona os novos arquivos selecionados
            self.window.list_widget_files.clear()
            self.window.list_widget_files.addItems(file_paths)
            print(f"Arquivos selecionados: {file_paths}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    sys.exit(app.exec())
