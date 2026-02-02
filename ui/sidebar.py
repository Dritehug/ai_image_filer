# ui/sidebar.py

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt
from config import CATEGORIES


class CategorySidebar(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        title = QLabel("Categories")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        self.buttons = {}

        for cat in CATEGORIES:
            btn = QPushButton(cat)
            btn.setFixedHeight(32)
            layout.addWidget(btn)
            self.buttons[cat] = btn

        layout.addSpacing(20)
        layout.addWidget(QLabel("Review Mode:"))

        toggle_row = QHBoxLayout()

        self.review_on = QPushButton("On")
        self.review_off = QPushButton("Off")

        toggle_row.addWidget(self.review_on)
        toggle_row.addWidget(self.review_off)

        layout.addLayout(toggle_row)
