# ui/dialogs.py

from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt


class InfoDialog(QDialog):
    def __init__(self, message: str):
        super().__init__()
        self.setWindowTitle("Info")

        layout = QVBoxLayout(self)

        label = QLabel(message)
        label.setWordWrap(True)
        layout.addWidget(label)

        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        layout.addWidget(ok_btn)