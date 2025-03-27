import logging
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QScrollArea,
    QMessageBox
)
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QPixmap, QPainter, QPen, QColor
from PIL import Image

class PreviewWindow(QDialog):
    def __init__(self, parent, image_path, callback):
        super().__init__(parent)
        self.image_path = image_path
        self.callback = callback
        self.start_pos = None
        self.current_rect = None
        self.scale_factor = 1.0
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Image Preview")
        self.setMinimumSize(800, 600)
        
        layout = QVBoxLayout(self)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        
        # Create label for image
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        scroll.setWidget(self.image_label)
        
        try:
            # Load and display image
            with Image.open(self.image_path) as img:
                # Calculate scale factor to fit within 800x600
                width, height = img.size
                max_width = 800
                max_height = 600
                
                if width > max_width or height > max_height:
                    scale_w = max_width / width
                    scale_h = max_height / height
                    self.scale_factor = min(scale_w, scale_h)
                    new_width = int(width * self.scale_factor)
                    new_height = int(height * self.scale_factor)
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Convert PIL image to QPixmap
                img.save("temp_preview.png")
                self.pixmap = QPixmap("temp_preview.png")
                self.image_label.setPixmap(self.pixmap)
                
                # Enable mouse tracking
                self.image_label.setMouseTracking(True)
                self.image_label.mousePressEvent = self.mousePressEvent
                self.image_label.mouseMoveEvent = self.mouseMoveEvent
                self.image_label.mouseReleaseEvent = self.mouseReleaseEvent
                
        except Exception as e:
            logging.exception("Error loading image for preview:")
            QMessageBox.critical(self, "Error", f"Failed to load image: {str(e)}")
            self.reject()
            
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_pos = event.pos()
            self.current_rect = None
            self.update_preview()
            
    def mouseMoveEvent(self, event):
        if self.start_pos is not None:
            self.current_rect = QRect(self.start_pos, event.pos()).normalized()
            self.update_preview()
            
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.start_pos is not None:
            end_pos = event.pos()
            if self.start_pos != end_pos:
                # Convert coordinates back to original image size
                x1 = int(min(self.start_pos.x(), end_pos.x()) / self.scale_factor)
                y1 = int(min(self.start_pos.y(), end_pos.y()) / self.scale_factor)
                x2 = int(max(self.start_pos.x(), end_pos.x()) / self.scale_factor)
                y2 = int(max(self.start_pos.y(), end_pos.y()) / self.scale_factor)
                
                self.callback((x1, y1, x2, y2))
                self.accept()
            
            self.start_pos = None
            self.current_rect = None
            self.update_preview()
            
    def update_preview(self):
        if not hasattr(self, 'pixmap'):
            return
            
        # Create a copy of the original pixmap
        preview = QPixmap(self.pixmap)
        painter = QPainter(preview)
        
        # Draw selection rectangle if exists
        if self.current_rect is not None:
            pen = QPen(QColor(255, 0, 0))  # Red color
            pen.setWidth(2)
            painter.setPen(pen)
            painter.drawRect(self.current_rect)
            
        painter.end()
        self.image_label.setPixmap(preview)
        
def open_preview(parent, image_path, callback):
    """Open the preview window for image selection.
    
    Args:
        parent: Parent window
        image_path: Path to the image file
        callback: Function to call with selected region coordinates
    """
    try:
        if not image_path or image_path.lower().endswith('.pdf'):
            QMessageBox.warning(parent, "Warning", "Please select an image file first.")
            return
            
        dialog = PreviewWindow(parent, image_path, callback)
        dialog.exec()
    except Exception as e:
        logging.exception("Error opening preview window:")
        QMessageBox.critical(parent, "Error", f"Failed to open preview window: {str(e)}") 