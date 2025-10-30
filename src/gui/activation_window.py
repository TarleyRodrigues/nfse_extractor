from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader
# Import necessário para type hinting, se quiser
from PySide6.QtWidgets import QDialog
from src import license_manager


class ActivationWindow:
    def __init__(self):
        # NÃO chamamos super().__init__() porque não estamos mais herdando de QDialog

        ui_file_path = "src/gui/ui/activation_window.ui"
        ui_file = QFile(ui_file_path)
        ui_file.open(QFile.ReadOnly)
        loader = QUiLoader()

        # --- CORREÇÃO PRINCIPAL AQUI ---
        # Não passamos 'self' como pai. Deixamos o loader criar a janela independente.
        self.window = loader.load(ui_file)
        ui_file.close()

        # Conecta os sinais da caixa de botões padrão do Qt Designer
        # 'accepted' é o sinal do botão OK (que renomeamos para Ativar)
        # 'rejected' é o sinal do botão Cancel
        self.window.buttonBox.accepted.connect(self.activate_license)
        self.window.buttonBox.rejected.connect(self.window.reject)

    def exec(self):
        """
        Método wrapper para exibir o diálogo.
        Retorna 1 (True) se aceito (ativado), 0 (False) se rejeitado (cancelado).
        """
        return self.window.exec()

    def activate_license(self):
        key = self.window.line_edit_license_key.text().strip()
        if not key:
            self.window.label_status.setText("Por favor, insira uma chave.")
            return

        self.window.label_status.setText("Validando com o servidor...")

        # Força a interface a atualizar o texto visualmente antes de travar na requisição
        self.window.repaint()

        result = license_manager.validate_license_key(key)

        if result.get("status") == "valid":
            license_manager.save_local_license({
                "license_key": key,
                "status": "valid",
                "expires_on": result.get("expires_on")
            })
            self.window.accept()  # Fecha a janela retornando sucesso (1)
        else:
            message = result.get("message", "Ocorreu um erro desconhecido.")
            self.window.label_status.setText(f"Falha na ativação: {message}")
