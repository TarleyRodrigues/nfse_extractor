"""
Controller para a Janela do Criador de Layouts (Layout Builder).
"""
import json
import os
import traceback
from PySide6.QtWidgets import (QMainWindow, QFileDialog, QGraphicsScene, QGraphicsRectItem,
                               QTableWidgetItem, QInputDialog, QMessageBox, QGraphicsView)
# --- LINHA CORRIGIDA ---
from PySide6.QtCore import QFile, Qt, QRectF, Signal
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QPixmap, QPen, QImage
import pdfplumber

from src import config


class PdfViewer(QGraphicsView):
    """
    Uma QGraphicsView customizada para exibir o PDF e lidar com a seleção
    de retângulos com o mouse.
    """
    # Sinal que emitirá as coordenadas do retângulo selecionado
    rect_selected = Signal(QRectF)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setScene(QGraphicsScene(self))
        self.start_pos = None
        self.current_rect_item = None
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        # Permite que o QGraphicsView ancore a transformação no ponto do mouse
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

    def wheelEvent(self, event):
        """
        Captura o evento da roda do mouse para aplicar zoom in/out.
        """
        # Fator de zoom. Valores maiores = zoom mais rápido.
        zoom_factor = 1.15

        # Se a roda do mouse foi rolada para cima (delta > 0), aplica zoom in
        if event.angleDelta().y() > 0:
            self.scale(zoom_factor, zoom_factor)
        # Se foi rolada para baixo, aplica zoom out
        else:
            self.scale(1 / zoom_factor, 1 / zoom_factor)

    def set_pixmap(self, pixmap):
        """Define a imagem do PDF a ser exibida."""
        self.scene().clear()
        self.scene().addPixmap(pixmap)
        # Reseta a visualização para mostrar a imagem inteira com zoom
        self.fitInView(self.scene().itemsBoundingRect(), Qt.KeepAspectRatio)

    def mousePressEvent(self, event):
        """Inicia o desenho do retângulo com o botão esquerdo."""
        if event.button() == Qt.LeftButton:
            self.start_pos = self.mapToScene(event.pos())
            # Desativa o modo de rolagem para permitir o desenho
            self.setDragMode(QGraphicsView.NoDrag)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Atualiza o retângulo de seleção enquanto o mouse é movido."""
        if self.start_pos:
            end_pos = self.mapToScene(event.pos())
            rect = QRectF(self.start_pos, end_pos).normalized()

            if self.current_rect_item:
                self.scene().removeItem(self.current_rect_item)

            pen = QPen(Qt.red, 2, Qt.SolidLine)
            self.current_rect_item = self.scene().addRect(rect, pen)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Finaliza o desenho, emite o sinal e limpa."""
        if event.button() == Qt.LeftButton and self.current_rect_item:
            self.rect_selected.emit(self.current_rect_item.rect())
            self.scene().removeItem(self.current_rect_item)
            self.current_rect_item = None
            self.start_pos = None
            # Reativa o modo de rolagem
            self.setDragMode(QGraphicsView.ScrollHandDrag)
        super().mouseReleaseEvent(event)


class LayoutBuilderWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # --- LÓGICA DE CARREGAMENTO CORRIGIDA ---
        ui_file_path = "src/gui/ui/layout_builder_window.ui"
        ui_file = QFile(ui_file_path)
        ui_file.open(QFile.ReadOnly)

        # Cria um loader e registra nossa classe customizada nele
        loader = QUiLoader()
        loader.registerCustomWidget(PdfViewer)  # <-- PASSO CRUCIAL

        self.window = loader.load(ui_file, self)
        ui_file.close()

        self.pdf_page = None
        self.mapped_fields = {}

        # Conecta os sinais aos slots
        self.window.btn_load_pdf.clicked.connect(self.load_pdf)
        self.window.btn_save_layout.clicked.connect(self.save_layout)
        self.window.btn_clear_selection.clicked.connect(self.clear_all_fields)

        # Conecta o sinal do nosso PdfViewer customizado
        self.window.graphics_view_pdf.rect_selected.connect(
            self.on_rect_selected)

        self.update_table()
        self.window.show()

    def load_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Selecionar PDF de Amostra", "", "Arquivos PDF (*.pdf)")
        if not file_path:
            return

        try:
            with pdfplumber.open(file_path) as pdf:
                self.pdf_page = pdf.pages[0]
                # Aumenta a resolução para melhor zoom
                pil_image = self.pdf_page.to_image(resolution=200).original

                if pil_image.mode != "RGBA":
                    pil_image = pil_image.convert("RGBA")

                qimage = QImage(pil_image.tobytes(
                    "raw", "RGBA"), pil_image.width, pil_image.height, QImage.Format_RGBA8888)
                pixmap = QPixmap.fromImage(qimage)

                self.window.graphics_view_pdf.set_pixmap(pixmap)
                self.clear_all_fields()
        except Exception as e:
            traceback.print_exc()
            self.show_message_box(
                "Erro", f"Não foi possível carregar o PDF:\n{e}", "critical")

    def on_rect_selected(self, rect):
        """Chamado quando um retângulo é selecionado no PdfViewer."""
        if not self.pdf_page:
            return

        conversion_factor = 72 / 200  # Resolução aumentada para 200
        coords = [
            round(rect.left() * conversion_factor, 2),
            round(rect.top() * conversion_factor, 2),
            round(rect.right() * conversion_factor, 2),
            round(rect.bottom() * conversion_factor, 2)
        ]

        field_name, ok = QInputDialog.getText(
            self, "Nome do Campo", "Digite o nome para este campo:")
        if ok and field_name:
            perm_pen = QPen(Qt.green, 2, Qt.DashLine)
            self.window.graphics_view_pdf.scene().addRect(rect, perm_pen)
            self.mapped_fields[field_name] = coords
            self.update_table()

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
        self.mapped_fields = {}
        # Limpa apenas os retângulos verdes, a imagem base é gerenciada por set_pixmap
        scene = self.window.graphics_view_pdf.scene()
        items_to_remove = [item for item in scene.items(
            # Gambiarra para não remover a imagem base
        ) if not isinstance(item, type(scene.items()[-1]))]
        for item in items_to_remove:
            scene.removeItem(item)
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
