"""
Controller para a Janela do Criador de Layouts (Layout Builder).
"""
import json
import os
import traceback
from PySide6.QtWidgets import (QMainWindow, QFileDialog, QGraphicsScene,
                               QTableWidgetItem, QInputDialog, QMessageBox)
from PySide6.QtCore import QFile, Qt, QRectF
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QPixmap, QPen, QImage
import pdfplumber

from src import config


class LayoutBuilderWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Carrega a interface do arquivo .ui
        ui_file_path = "src/gui/ui/layout_builder_window.ui"
        ui_file = QFile(ui_file_path)
        ui_file.open(QFile.ReadOnly)
        loader = QUiLoader()
        self.window = loader.load(ui_file)

        self.pdf_page = None
        self.pixmap_item = None  # Referência ao item de imagem na cena
        self.scene = QGraphicsScene()
        self.window.graphics_view_pdf.setScene(self.scene)
        # Dicionário para armazenar {'nome_campo': [coords]}
        self.mapped_fields = {}

        # Variáveis para desenho do retângulo
        self.start_pos = None
        self.current_rect_item = None

        # Conecta os sinais aos slots
        self.window.btn_load_pdf.clicked.connect(self.load_pdf)
        self.window.btn_save_layout.clicked.connect(self.save_layout)
        self.window.btn_clear_selection.clicked.connect(self.clear_all_fields)

        # Sobrescreve os eventos do mouse do QGraphicsView
        self.window.graphics_view_pdf.mousePressEvent = self.mouse_press
        self.window.graphics_view_pdf.mouseMoveEvent = self.mouse_move
        self.window.graphics_view_pdf.mouseReleaseEvent = self.mouse_release

        self.update_table()
        self.window.show()

    def load_pdf(self):
        """Carrega um PDF de amostra e renderiza a primeira página."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Selecionar PDF de Amostra", "", "Arquivos PDF (*.pdf)")
        if not file_path:
            return

        try:
            with pdfplumber.open(file_path) as pdf:
                self.pdf_page = pdf.pages[0]
                pil_image = self.pdf_page.to_image(resolution=150).original

                # --- CONVERSÃO DE IMAGEM CORRIGIDA ---
                # Garante que a imagem Pillow está em um formato compatível
                if pil_image.mode != "RGBA":
                    pil_image = pil_image.convert("RGBA")

                # Cria um objeto QImage a partir dos bytes da imagem Pillow
                img_data = pil_image.tobytes("raw", "RGBA")
                qimage = QImage(img_data, pil_image.width,
                                pil_image.height, QImage.Format_RGBA8888)

                # Cria o QPixmap a partir do QImage (o formato correto)
                pixmap = QPixmap.fromImage(qimage)
                # --- FIM DA CORREÇÃO ---

                self.scene.clear()
                self.pixmap_item = self.scene.addPixmap(
                    pixmap)  # Adiciona e guarda a referência
                self.window.graphics_view_pdf.fitInView(
                    self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)
                self.clear_all_fields()

        except Exception as e:
            traceback.print_exc()  # Imprime o erro detalhado no console para depuração
            self.show_message_box(
                "Erro", f"Não foi possível carregar o PDF:\n{e}", "critical")

    def mouse_press(self, event):
        """Captura o início do clique e arrastar."""
        if not self.pdf_page:
            return
        self.start_pos = self.window.graphics_view_pdf.mapToScene(event.pos())

    def mouse_move(self, event):
        """Desenha o retângulo de seleção enquanto o mouse é arrastado."""
        if not self.start_pos:
            return

        end_pos = self.window.graphics_view_pdf.mapToScene(event.pos())

        # Cria um QRectF normalizado para garantir que a largura e altura sejam positivas
        rect = QRectF(self.start_pos, end_pos).normalized()

        if self.current_rect_item:
            self.scene.removeItem(self.current_rect_item)

        pen = QPen(Qt.red, 2, Qt.SolidLine)
        self.current_rect_item = self.scene.addRect(rect, pen)

    def mouse_release(self, event):
        """Finaliza a seleção e pede o nome do campo."""
        if not self.start_pos or not self.current_rect_item:
            return

        end_pos = self.window.graphics_view_pdf.mapToScene(event.pos())
        rect = QRectF(self.start_pos, end_pos).normalized()

        # Converte as coordenadas da imagem (pixels) para coordenadas do PDF (pontos)
        conversion_factor = 72 / 150

        x0 = rect.left() * conversion_factor
        top = rect.top() * conversion_factor
        x1 = rect.right() * conversion_factor
        bottom = rect.bottom() * conversion_factor

        coords = [round(c, 2) for c in [x0, top, x1, bottom]]

        field_name, ok = QInputDialog.getText(
            self, "Nome do Campo", "Digite o nome para este campo:")

        if ok and field_name:
            # Adiciona um novo retângulo permanente à cena para feedback visual
            perm_pen = QPen(Qt.green, 2, Qt.DashLine)
            self.scene.addRect(rect, perm_pen)

            self.mapped_fields[field_name] = coords
            self.update_table()

        # Remove o retângulo de seleção vermelho temporário
        if self.current_rect_item:
            self.scene.removeItem(self.current_rect_item)
            self.current_rect_item = None

        self.start_pos = None

    def update_table(self):
        """Atualiza a tabela com os campos mapeados."""
        self.window.table_widget_fields.setRowCount(0)
        for name, coords in self.mapped_fields.items():
            row_position = self.window.table_widget_fields.rowCount()
            self.window.table_widget_fields.insertRow(row_position)
            self.window.table_widget_fields.setItem(
                row_position, 0, QTableWidgetItem(name))
            self.window.table_widget_fields.setItem(
                row_position, 1, QTableWidgetItem(str(coords)))

    def clear_all_fields(self):
        """Limpa todos os campos mapeados e os retângulos da cena."""
        self.mapped_fields = {}
        # Remove todos os itens da cena, exceto a imagem base do PDF
        for item in self.scene.items():
            if item != self.pixmap_item:
                self.scene.removeItem(item)
        self.update_table()

    def save_layout(self):
        """Salva o layout mapeado em um arquivo JSON."""
        if not self.mapped_fields:
            self.show_message_box(
                "Atenção", "Nenhum campo foi mapeado ainda.", "warning")
            return

        file_name, ok = QInputDialog.getText(
            self, "Salvar Layout", "Digite o nome do arquivo de layout (ex: prefeitura_campinas):")
        if ok and file_name:
            layout_data = {}
            for name, coords in self.mapped_fields.items():
                layout_data[name] = {"page": 0, "coords": coords}

            output_path = os.path.join(config.LAYOUTS_DIR, f"{file_name}.json")
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(layout_data, f, indent=4)
                self.show_message_box(
                    "Sucesso", f"Layout salvo em:\n{output_path}", "info")
            except Exception as e:
                self.show_message_box(
                    "Erro", f"Não foi possível salvar o layout:\n{e}", "critical")

    def show_message_box(self, title, message, level="info"):
        """Função de utilidade para exibir caixas de mensagem."""
        msg_box = QMessageBox(self.window)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)

        icon_map = {
            "info": QMessageBox.Information,
            "warning": QMessageBox.Warning,
            "critical": QMessageBox.Critical
        }
        msg_box.setIcon(icon_map.get(level, QMessageBox.NoIcon))
        msg_box.exec()
