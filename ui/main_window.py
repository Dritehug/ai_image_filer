# ui/main_window.py

from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout
from PySide6.QtCore import Qt

from ui.sidebar import CategorySidebar
from ui.drop_area import ImageDropArea
from ui.image_viewer import ImageViewer
from ui.dialogs import InfoDialog

from backend.ai_classifier import classify_image
from backend.file_manager import move_image_to_category

from PySide6.QtGui import QDesktopServices
from PySide6.QtCore import QUrl
import os


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.review_mode = True
        self.override_mode = False 

        self.setWindowTitle("Image Sorter")
        self.setMinimumSize(900, 600)

        # Layouts
        main_layout = QHBoxLayout(self)
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        # Widgets
        self.sidebar = CategorySidebar()
        self.drop_area = ImageDropArea()
        self.viewer = ImageViewer()

        # Uses sidebar + drop_area
        left_layout.addWidget(self.sidebar)
        left_layout.addStretch()

        right_layout.addWidget(self.drop_area)
        right_layout.addWidget(self.viewer, stretch=1)

        main_layout.addLayout(left_layout, 1)
        main_layout.addLayout(right_layout, 3)

        # Connections
        self.drop_area.imageDropped.connect(self.handle_image_drop)
        self.viewer.changeRequested.connect(self.on_change_clicked)
        self.viewer.nextRequested.connect(self.on_next_clicked)
        self.viewer.backRequested.connect(self.on_back_clicked)

        # Lambda function has two branches.
        # Open folder or change category. Check on_category_clicked if error.
        for cat, btn in self.sidebar.buttons.items():
            btn.clicked.connect(lambda _, c=cat: self.on_category_clicked(c))

        self.sidebar.review_on.clicked.connect(self.enable_review_mode)
        self.sidebar.review_off.clicked.connect(self.disable_review_mode)


        self.current_image_path = None
        self.current_predicted_category = None

        self.history_stack = []
        self.forward_stack = []
        self.batch_queue = []

    # Happens the moment you drop image:
    def handle_image_drop(self, paths: list):
        import os

        # Reset navigation state for a new batch
        self.history_stack = []
        self.forward_stack = []
        self.current_image_path = None
        self.current_predicted_category = None

        all_files = []

        for p in paths:
            if os.path.isdir(p):
                for root, _, files in os.walk(p):
                    for f in files:
                        if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                            all_files.append(os.path.join(root, f))
            else:
                if p.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                    all_files.append(p)

        if not all_files:
            InfoDialog("No images found").exec()
            return

        self.batch_queue = all_files

        if self.review_mode:
            self.load_next_image()
        else:
            for img in all_files:
                self.process_single_image(img)
            InfoDialog(f"Processed {len(all_files)} images").exec()
            self.reset_ui_state()

    # Image processor. Passes to queues.
    def process_single_image(self, path: str):
        """Classify and move a NEW image."""
        category = classify_image(path)
        self.current_predicted_category = category

        # Move + log
        new_path = move_image_to_category(path, category)

        # Keep queue clean if the original path is still in it
        self.batch_queue = [
            new_path if p == path else p
            for p in self.batch_queue
        ]

        # Update state + show
        self.current_image_path = new_path
        self.viewer.show_image(new_path)
        self.viewer.set_category_text(category)

    # If something goes wrong while procesing:

    def on_change_clicked(self):
        if not self.current_image_path:
            return
        self.override_mode = True  # Next category click overrides

    def on_category_clicked(self, category: str):
        if self.override_mode:
            self.manual_override(category)
            self.override_mode = False
        else:
            self.open_category_folder(category)
    # Continued:

    def manual_override(self, category: str):
        """Move current image to a user-selected category."""
        if not self.current_image_path:
            return

        old_path = self.current_image_path

        # Move original image to new category
        new_path = move_image_to_category(old_path, category)

        # Delete the old copy
        if os.path.exists(old_path):
            try:
                os.remove(old_path)
            except Exception as e:
                InfoDialog(f"Failed to delete old file:\n{e}").exec()

        # Update state
        self.current_image_path = new_path
        self.current_predicted_category = category
        self.viewer.set_category_text(category)
        self.viewer.show_image(new_path)

        InfoDialog(f"Moved to: {category}").exec()


    def on_next_clicked(self):
        # If we have forward history, go forward
        if self.forward_stack:
            next_path, next_category = self.forward_stack.pop()
            self.history_stack.append(
                (self.current_image_path, self.current_predicted_category)
            )
            self.show_existing_image(next_path, next_category)
            return

        # Otherwise load next unprocessed image
        self.load_next_image()


    def load_next_image(self):
        if not self.batch_queue:
            InfoDialog("All images processed").exec()
            return

        # Save current image state for Back
        if self.current_image_path:
            self.history_stack.append(
                (self.current_image_path, self.current_predicted_category)
            )
        # Clear forward history because we're branching
        self.forward_stack = []

        next_img = self.batch_queue.pop(0)
        self.process_single_image(next_img)

    def on_back_clicked(self):
        if not self.history_stack:
            InfoDialog("No previous image").exec()
            return

        # Move current image into forward stack
        if self.current_image_path:
            self.forward_stack.append(
                (self.current_image_path, self.current_predicted_category)
            )

        prev_path, prev_category = self.history_stack.pop()
        self.show_existing_image(prev_path, prev_category)


    # Review mode

    def enable_review_mode(self):
        self.review_mode = True
        InfoDialog("Review Mode enabled").exec()

    def disable_review_mode(self):
        self.review_mode = False
        InfoDialog("Review Mode disabled").exec()

    # No review mode

    def reset_ui_state(self):

        # Resets the stack. Deal with UI elements afterwards.

        self.history_stack = []
        self.forward_stack = []
        self.batch_queue = []

        self.current_image_path = None
        self.current_predicted_category = None
        self.override_mode = False
        self.viewer._current_path = None
        self.viewer.image_label.clear()
        self.viewer.set_category_text("—")


    def open_category_folder(self, category: str):
        folder_path = os.path.join(os.getcwd(), "sorted_images", category)

        if not os.path.isdir(folder_path):
            InfoDialog(f"No folder found for category: {category}").exec()
            return

        QDesktopServices.openUrl(QUrl.fromLocalFile(folder_path))

    def show_existing_image(self, path: str, category: str):
        self.current_image_path = path
        self.current_predicted_category = category
        self.viewer.show_image(path)
        self.viewer.set_category_text(category)
