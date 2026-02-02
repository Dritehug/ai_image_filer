# ui/image_viewer.py

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget, QPushButton, QHBoxLayout
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt, Signal

class ImageViewer(QWidget):
    changeRequested = Signal()
    nextRequested = Signal()
    backRequested = Signal()

    def __init__(self):
        super().__init__()

        self._current_path = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Displayed image
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("background: #222; border: 1px solid #444;")
        # Category button
        self.category_label = QLabel("Category: —")
        self.category_label.setAlignment(Qt.AlignCenter)
        self.category_label.setStyleSheet("color: #ccc; font-size: 14px; padding: 6px;")

        # Buttons
        btn_row = QHBoxLayout()
        self.change_button = QPushButton("Change")
        self.back_button = QPushButton("Back")
        self.next_button = QPushButton("Next")

        # Buttons again
        self.change_button.clicked.connect(self.changeRequested.emit)
        self.back_button.clicked.connect(self.backRequested.emit)
        self.next_button.clicked.connect(self.nextRequested.emit)

        btn_row.addWidget(self.change_button)
        btn_row.addWidget(self.back_button)
        btn_row.addWidget(self.next_button)

        layout.addWidget(self.image_label)
        layout.addWidget(self.category_label)
        layout.addLayout(btn_row)

    # Displays current image V

    def show_image(self, path: str):
        self._current_path = path
        img = QImage(path)

        if img.isNull():
            return
        pix = QPixmap.fromImage(img)

        scaled = pix.scaled(
            self.image_label.width(),
            self.image_label.height(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        self.image_label.setPixmap(scaled)

    def set_category_text(self, category: str):
        self.category_label.setText(f"Category: {category}")

    def resizeEvent(self, event):
        if self._current_path:
            self.show_image(self._current_path)
        super().resizeEvent(event)