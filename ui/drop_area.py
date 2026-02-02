    # ui/drop_area.py

from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt, Signal


class ImageDropArea(QLabel):
    imageDropped = Signal(list)

    def __init__(self):
        super().__init__("Drop an image here")
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            border: 2px dashed #888;
            padding: 40px;
            font-size: 16px;
        """)
        self.setAcceptDrops(True)


    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        event.acceptProposedAction()

    # Reads folder. Link to main_window URL reader
    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if not urls:
            return

        paths = [u.toLocalFile() for u in urls]
        self.imageDropped.emit(paths)