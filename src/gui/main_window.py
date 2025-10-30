"""
Controller da Janela Principal da Aplicação.

Responsável por carregar a interface do usuário (View), conectar os sinais
(eventos de clique) aos slots (funções de lógica) e interagir com o
Model (lógica de negócios de extração).
"""
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog
from PySide6.QtCore import QFile, QThread, Signal
from PySide6.QtUiTools import QUiLoader
from src import config, pdf_processor, data_parser, excel_writer
import os


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        ui_file_path = "src/gui/ui/main_window.ui"
        ui_file = QFile(ui_file_path)
        ui_file.open(QFile.ReadOnly)

        loader = QUiLoader()
        self.window = loader.load(ui_file)
        ui_file.close()

        self.pdf_files = []  # Armazena os caminhos dos PDFs selecionados
        self.output_file_path = ""  # <-- 1. Adicionar nova variável de instância

        # Conecta os sinais aos slots
        self.window.btn_select_pdfs.clicked.connect(self.select_pdfs)
        self.window.btn_process_files.clicked.connect(self.process_files)
        self.window.btn_select_output.clicked.connect(self.select_output_file)

        self.populate_layouts_combobox()
        self.update_ui_state()

        self.window.show()

    def populate_layouts_combobox(self):
        """Busca por arquivos .json na pasta de layouts e os adiciona ao ComboBox."""
        try:
            layouts = [f.replace('.json', '') for f in os.listdir(
                config.LAYOUTS_DIR) if f.endswith('.json')]
            self.window.combo_box_layouts.addItems(layouts)
        except FileNotFoundError:
            self.window.label_status.setText(
                "Erro: Pasta de layouts não encontrada.")

    def select_pdfs(self):
        """Abre uma caixa de diálogo para selecionar múltiplos arquivos PDF."""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "Selecionar arquivos PDF", "", "Arquivos PDF (*.pdf)")
        if file_paths:
            self.pdf_files = file_paths
            self.window.list_widget_files.clear()
            self.window.list_widget_files.addItems(
                [os.path.basename(p) for p in self.pdf_files])
            self.window.label_status.setText(
                f"{len(self.pdf_files)} arquivo(s) selecionado(s).")
        self.update_ui_state()

    def select_output_file(self):
        """Abre um diálogo para o usuário escolher o local e nome do arquivo de saída."""
        # Sugere um nome de arquivo e diretório inicial
        default_path = os.path.join(config.OUTPUT_DIR, "relatorio_nfse.xlsx")

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar Relatório Como...",
            default_path,
            "Arquivos Excel (*.xlsx)"
        )

        if file_path:
            self.output_file_path = file_path
            # Mostra o caminho escolhido na caixa de texto
            self.window.line_edit_output_path.setText(self.output_file_path)
            self.window.label_status.setText(
                f"Relatório será salvo em: {os.path.basename(file_path)}")
        self.update_ui_state()

    def process_files(self):
        """Inicia o processo de extração na worker thread."""
        if not self.pdf_files or not self.output_file_path:  # <-- Adicionar validação do caminho de saída
            self.window.label_status.setText(
                "Selecione os PDFs e o local de saída.")
            return

        layout_name = self.window.combo_box_layouts.currentText()
        if not layout_name:
            self.window.label_status.setText("Nenhum layout selecionado.")
            return

        try:
            layout_map = config.load_layout(layout_name)
        except Exception as e:
            self.window.label_status.setText(f"Erro ao carregar layout: {e}")
            return

        self.update_ui_state(processing=True)

        # Cria e inicia a worker thread
        self.worker = Worker(self.pdf_files, layout_map, self.output_file_path)
        self.worker.progress.connect(self.window.progress_bar.setValue)
        self.worker.status_changed.connect(self.window.label_status.setText)
        self.worker.finished.connect(self.on_processing_finished)
        self.worker.error.connect(self.on_processing_error)
        self.worker.start()

    def on_processing_finished(self, message):
        """Chamado quando o worker termina com sucesso."""
        self.window.label_status.setText(message)
        self.update_ui_state(processing=False)

    def on_processing_error(self, message):
        """Chamado quando o worker encontra um erro."""
        self.window.label_status.setText(f"ERRO: {message}")
        self.update_ui_state(processing=False)

    def update_ui_state(self, processing=False):
        """Habilita/desabilita os widgets com base no estado da aplicação."""
        self.window.btn_select_pdfs.setEnabled(not processing)

        enable_process_button = not processing and bool(
            self.pdf_files) and bool(self.output_file_path)
        self.window.btn_process_files.setEnabled(enable_process_button)

        self.window.combo_box_layouts.setEnabled(not processing)

        if not processing:
            self.window.progress_bar.setValue(0)

# --- Classe Worker para Processamento em Segundo Plano ---


class Worker(QThread):
    """
    Worker thread para executar o processo de extração de PDF sem congelar a GUI.
    """
    # Sinais que serão emitidos pelo worker
    # Para atualizar a barra de progresso (0-100)
    progress = Signal(int)
    # Para enviar mensagens de status para a GUI
    status_changed = Signal(str)
    # Para sinalizar o término (com mensagem final)
    finished = Signal(str)
    error = Signal(str)                # Para sinalizar um erro crítico

    def __init__(self, pdf_paths, layout_map, output_path):
        super().__init__()
        self.pdf_paths = pdf_paths
        self.layout_map = layout_map
        self.output_path = output_path  # Armazena o caminho completo

    def run(self):
        """
        Este método é executado quando a thread inicia. Contém a lógica de extração.
        """
        try:
            total_files = len(self.pdf_paths)
            all_nfse_data = []

            for i, pdf_path in enumerate(self.pdf_paths):
                filename = os.path.basename(pdf_path)
                self.status_changed.emit(f"Processando: {filename}...")

                raw_data = pdf_processor.extract_data_from_pdf(
                    pdf_path, self.layout_map)
                if not raw_data:
                    continue  # Pula arquivos que falharam na extração

                clean_data = {"arquivo_origem": filename}
                for field, raw_value in raw_data.items():
                    parser_function = getattr(
                        data_parser, f"parse_{field}", data_parser.clean_text)
                    clean_data[field] = parser_function(raw_value)

                all_nfse_data.append(clean_data)

                # Calcula e emite o progresso
                progress_percentage = int(((i + 1) / total_files) * 100)
                self.progress.emit(progress_percentage)

            if not all_nfse_data:
                self.error.emit(
                    "Nenhum dado pôde ser extraído dos arquivos selecionados.")
                return

            self.status_changed.emit("Gerando relatório Excel...")
            excel_writer.generate_excel_report(
                all_nfse_data, output_path=self.output_path)

            self.finished.emit(
                f"Processo concluído! Relatório salvo em:\n{self.output_path}")

        except Exception as e:
            self.error.emit(f"Ocorreu um erro: {str(e)}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    sys.exit(app.exec())
