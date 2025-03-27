import logging
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QPushButton, QMessageBox
)
from scrapey.utils import app_settings, save_settings

class PreferencesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Preferences")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # OCR Engine selection
        engine_layout = QHBoxLayout()
        engine_label = QLabel("Default OCR Engine:")
        self.engine_combo = QComboBox()
        self.engine_combo.addItems(["Tesseract", "EasyOCR"])
        current_engine = app_settings.get('default_ocr_engine', 'Tesseract')
        self.engine_combo.setCurrentText(current_engine)
        
        engine_layout.addWidget(engine_label)
        engine_layout.addWidget(self.engine_combo)
        layout.addLayout(engine_layout)
        
        # Language selection
        lang_layout = QHBoxLayout()
        lang_label = QLabel("OCR Language:")
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["eng", "fra", "deu", "spa", "ita", "por", "rus", "chi_sim", "jpn", "kor"])
        current_lang = app_settings.get('ocr_language', 'eng')
        self.lang_combo.setCurrentText(current_lang)
        
        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(self.lang_combo)
        layout.addLayout(lang_layout)
        
        # Output format selection
        format_layout = QHBoxLayout()
        format_label = QLabel("Default Output Format:")
        self.format_combo = QComboBox()
        self.format_combo.addItems(["Text", "JSON", "CSV", "HTML", "PDF"])
        current_format = app_settings.get('default_output_format', 'Text')
        self.format_combo.setCurrentText(current_format)
        
        format_layout.addWidget(format_label)
        format_layout.addWidget(self.format_combo)
        layout.addLayout(format_layout)
        
        # Save button
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_preferences)
        layout.addWidget(save_button)
        
    def save_preferences(self):
        try:
            # Update settings
            app_settings['default_ocr_engine'] = self.engine_combo.currentText()
            app_settings['ocr_language'] = self.lang_combo.currentText()
            app_settings['default_output_format'] = self.format_combo.currentText()
            
            # Save to file
            save_settings()
            
            QMessageBox.information(self, "Success", "Preferences saved successfully!")
            self.accept()
            
        except Exception as e:
            logging.exception("Error saving preferences:")
            QMessageBox.critical(self, "Error", f"Failed to save preferences: {str(e)}")
            
def open_preferences(parent):
    """Open the preferences dialog.
    
    Args:
        parent: Parent window
    """
    try:
        dialog = PreferencesDialog(parent)
        dialog.exec()
    except Exception as e:
        logging.exception("Error opening preferences dialog:")
        QMessageBox.critical(parent, "Error", f"Failed to open preferences: {str(e)}") 