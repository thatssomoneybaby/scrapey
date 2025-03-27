import sys
import logging
import json
import csv
import threading
import tempfile
import os
from PIL import Image
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QComboBox, QTextEdit, QProgressBar,
    QFileDialog, QMessageBox, QMenuBar, QMenu, QSpinBox, QCheckBox,
    QListWidget
)
from PySide6.QtCore import Qt, QThread, Signal, QUrl
from scrapey.utils import app_settings, save_settings
from scrapey.ocr import perform_ocr, ocr_scanned_pdf
from scrapey.pdf import extract_pdf_text, get_pdf_page_count
from scrapey.web import extract_web_text
from .preferences import open_preferences
from .preview import open_preview

class ScrapeWorker(QThread):
    finished = Signal(str)
    error = Signal(str)
    progress = Signal(int, int)  # current, total
    
    def __init__(self, sources, source_type, engine=None, selected_region=None, page_range=None):
        super().__init__()
        self.sources = sources if isinstance(sources, list) else [sources]
        self.source_type = source_type
        self.engine = engine
        self.selected_region = selected_region
        self.page_range = page_range
        
    def run(self):
        try:
            logging.info("Scraping started.")
            results = []
            total_sources = len(self.sources)
            
            for idx, source in enumerate(self.sources, 1):
                self.progress.emit(idx, total_sources)
                
                if self.source_type == "Web":
                    result = extract_web_text(source)
                elif self.source_type == "PDF":
                    result = extract_pdf_text(source, self.page_range)
                elif self.source_type == "Image OCR":
                    if source.lower().endswith(".pdf"):
                        result = ocr_scanned_pdf(source, self.engine, self.page_range)
                    else:
                        if self.selected_region:
                            with Image.open(source) as img:
                                cropped = img.crop(self.selected_region)
                                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                                    temp_filename = tmp.name
                                    cropped.save(temp_filename)
                            result = perform_ocr(temp_filename, self.engine)
                            os.remove(temp_filename)
                        else:
                            result = perform_ocr(source, self.engine)
                else:
                    result = "Unsupported source type"
                    
                results.append(f"=== Results for {os.path.basename(source)} ===\n{result}\n")
                
            self.finished.emit("\n".join(results))
            logging.info("Scraping completed successfully.")
        except Exception as e:
            logging.exception("Error during scraping:")
            self.error.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.selected_region = None
        self.scrape_thread = None
        self.source_files = []
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Scrapey: Comprehensive Scraping Tool")
        self.setMinimumSize(800, 600)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create menu bar
        menubar = self.menuBar()
        settings_menu = menubar.addMenu("Settings")
        preferences_action = settings_menu.addAction("Preferences...")
        preferences_action.triggered.connect(self.open_preferences)
        
        # Source input section for URL
        source_layout = QHBoxLayout()
        source_label = QLabel("Source (URL or file path):")
        self.source_entry = QLineEdit()
        self.browse_button = QPushButton("Browse...")
        self.preview_button = QPushButton("Preview")
        
        source_layout.addWidget(source_label)
        source_layout.addWidget(self.source_entry, 1)  # 1 is stretch factor
        source_layout.addWidget(self.browse_button)
        source_layout.addWidget(self.preview_button)
        layout.addLayout(source_layout)
        
        # File list for batch processing
        self.file_list = QListWidget()
        self.file_list.setMaximumHeight(100)
        layout.addWidget(QLabel("Selected Files:"))
        layout.addWidget(self.file_list)
        
        # Source type selection
        type_layout = QHBoxLayout()
        type_label = QLabel("Source Type:")
        self.source_type = QComboBox()
        self.source_type.addItems(["PDF", "Image OCR", "Web"])  # Reorder to make PDF first
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.source_type)
        type_layout.addStretch()
        layout.addLayout(type_layout)
        
        # OCR Engine selection
        ocr_layout = QHBoxLayout()
        ocr_label = QLabel("OCR Engine:")
        self.ocr_engine = QComboBox()
        self.ocr_engine.addItems(["Tesseract", "EasyOCR"])
        ocr_layout.addWidget(ocr_label)
        ocr_layout.addWidget(self.ocr_engine)
        ocr_layout.addStretch()
        layout.addLayout(ocr_layout)
        
        # Page range selection
        page_layout = QHBoxLayout()
        self.page_range_check = QCheckBox("Process Page Range:")
        self.page_start = QSpinBox()
        self.page_start.setMinimum(1)
        self.page_end = QSpinBox()
        self.page_end.setMinimum(1)
        page_range_label = QLabel("to")
        
        page_layout.addWidget(self.page_range_check)
        page_layout.addWidget(self.page_start)
        page_layout.addWidget(page_range_label)
        page_layout.addWidget(self.page_end)
        page_layout.addStretch()
        layout.addLayout(page_layout)
        
        # Output format selection
        format_layout = QHBoxLayout()
        format_label = QLabel("Output Format:")
        self.output_format = QComboBox()
        self.output_format.addItems(["Text", "JSON", "CSV", "HTML", "PDF"])
        format_layout.addWidget(format_label)
        format_layout.addWidget(self.output_format)
        format_layout.addStretch()
        layout.addLayout(format_layout)
        
        # Scrape button
        self.scrape_button = QPushButton("Scrape")
        layout.addWidget(self.scrape_button)
        
        # Output text area
        layout.addWidget(QLabel("Extracted Text:"))
        self.output_text = QTextEdit()
        layout.addWidget(self.output_text)
        
        # Save button
        self.save_button = QPushButton("Save Output")
        layout.addWidget(self.save_button)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)
        
        # Connect signals
        self.browse_button.clicked.connect(self.browse_file)
        self.preview_button.clicked.connect(self.preview_image)
        self.scrape_button.clicked.connect(self.run_scrape)
        self.save_button.clicked.connect(self.save_output)
        self.source_type.currentTextChanged.connect(self.update_gui)
        self.page_range_check.toggled.connect(self.toggle_page_range)
        
        # Initial GUI update
        self.update_gui()
        self.toggle_page_range(False)
        
    def toggle_page_range(self, enabled):
        self.page_start.setEnabled(enabled)
        self.page_end.setEnabled(enabled)
        
        if enabled and self.source_files:
            # Update page range for the first file
            self.update_page_range(self.source_files[0])
        
    def update_page_range(self, file_path):
        try:
            if file_path.lower().endswith('.pdf'):
                page_count = get_pdf_page_count(file_path)
                self.page_start.setMaximum(page_count)
                self.page_end.setMaximum(page_count)
                self.page_end.setValue(page_count)
                self.page_range_check.setEnabled(True)
            else:
                self.page_range_check.setEnabled(False)
                self.page_range_check.setChecked(False)
        except Exception as e:
            logging.exception("Error getting page count:")
            self.page_range_check.setEnabled(False)
            self.page_range_check.setChecked(False)
        
    def open_preferences(self):
        open_preferences(self)
        
    def browse_file(self):
        source_type = self.source_type.currentText()
        if source_type in ("PDF", "Image OCR"):
            if source_type == "PDF":
                file_filter = "PDF Files (*.pdf)"
            else:
                file_filter = "Image Files (*.png *.jpg *.jpeg *.bmp);;PDF Files (*.pdf);;All Files (*.*)"
            
            # Create file dialog with native options
            dialog = QFileDialog(self)
            dialog.setFileMode(QFileDialog.ExistingFiles)
            dialog.setViewMode(QFileDialog.Detail)
            dialog.setOption(QFileDialog.DontUseNativeDialog, False)  # Use native dialog
            dialog.setDirectory(os.path.expanduser("~"))  # Start from user's home directory
            dialog.setNameFilter(file_filter)
            
            # Enable access to all locations
            dialog.setOption(QFileDialog.ReadOnly, False)
            dialog.setOption(QFileDialog.HideNameFilterDetails, False)
            dialog.setSidebarUrls([
                QUrl.fromLocalFile(os.path.expanduser("~")),  # Home
                QUrl.fromLocalFile(os.path.expanduser("~/Documents")),  # Documents
                QUrl.fromLocalFile(os.path.expanduser("~/Downloads")),  # Downloads
                QUrl.fromLocalFile(os.path.expanduser("~/Desktop")),  # Desktop
                QUrl.fromLocalFile("/"),  # Root directory
            ])
            
            if dialog.exec():
                filenames = dialog.selectedFiles()
                if filenames:
                    self.source_files = filenames
                    self.file_list.clear()
                    self.file_list.addItems([os.path.basename(f) for f in filenames])
                    self.source_entry.setText(filenames[0])  # Show first file in entry
                    self.update_page_range(filenames[0])
                
    def preview_image(self):
        if not self.source_files:
            QMessageBox.warning(self, "Warning", "Please select an image file first.")
            return
            
        open_preview(self, self.source_files[0], self.set_selected_region)
        
    def set_selected_region(self, region):
        self.selected_region = region
        
    def update_gui(self):
        source_type = self.source_type.currentText()
        if source_type == "Image OCR":
            self.ocr_engine.setEnabled(True)
            self.browse_button.setEnabled(True)
            self.preview_button.setEnabled(True)
            self.source_entry.setPlaceholderText("Select image files using Browse...")
        elif source_type == "PDF":
            self.ocr_engine.setEnabled(False)
            self.browse_button.setEnabled(True)
            self.preview_button.setEnabled(False)
            self.source_entry.setPlaceholderText("Select PDF files using Browse...")
        else:  # Web
            self.ocr_engine.setEnabled(False)
            self.browse_button.setEnabled(False)
            self.preview_button.setEnabled(False)
            self.page_range_check.setEnabled(False)
            self.page_range_check.setChecked(False)
            self.source_entry.setPlaceholderText("Enter a URL to scrape...")
            
    def run_scrape(self):
        if self.source_type.currentText() == "Web":
            source = self.source_entry.text().strip()
            if not source:
                QMessageBox.warning(self, "Error", "Please enter a source URL.")
                return
            sources = [source]
        else:
            if not self.source_files and not self.source_entry.text().strip():
                QMessageBox.warning(self, "Error", "Please select one or more files using Browse...")
                return
            if self.source_files:
                sources = self.source_files
            else:
                # Allow manual path entry as fallback
                file_path = self.source_entry.text().strip()
                if not os.path.exists(file_path):
                    QMessageBox.warning(self, "Error", "The specified file does not exist.")
                    return
                sources = [file_path]
            
        self.progress_bar.setRange(0, len(sources))
        self.progress_bar.setValue(0)
        self.scrape_button.setEnabled(False)
        
        # Get page range if enabled
        page_range = None
        if self.page_range_check.isChecked():
            page_range = (self.page_start.value(), self.page_end.value())
        
        # Create and start worker thread
        self.scrape_thread = ScrapeWorker(
            sources,
            self.source_type.currentText(),
            self.ocr_engine.currentText() if self.ocr_engine.isEnabled() else None,
            self.selected_region,
            page_range
        )
        self.scrape_thread.finished.connect(self.on_scrape_finished)
        self.scrape_thread.error.connect(self.on_scrape_error)
        self.scrape_thread.progress.connect(self.update_progress)
        self.scrape_thread.start()
        
    def update_progress(self, current, total):
        self.progress_bar.setValue(current)
        self.progress_bar.setFormat(f"Processing file {current} of {total}")
        
    def on_scrape_finished(self, result):
        self.output_text.setText(result)
        self.progress_bar.setFormat("Processing complete")
        self.scrape_button.setEnabled(True)
        
    def on_scrape_error(self, error_msg):
        QMessageBox.critical(self, "Error", error_msg)
        self.progress_bar.setFormat("Error occurred")
        self.scrape_button.setEnabled(True)
        
    def save_output(self):
        text = self.output_text.toPlainText()
        if not text.strip():
            QMessageBox.warning(self, "Warning", "No output to save.")
            return
            
        out_format = self.output_format.currentText()
        if out_format == "Text":
            file_filter = "Text Files (*.txt)"
            default_suffix = ".txt"
        elif out_format == "JSON":
            file_filter = "JSON Files (*.json)"
            default_suffix = ".json"
        elif out_format == "CSV":
            file_filter = "CSV Files (*.csv)"
            default_suffix = ".csv"
        elif out_format == "HTML":
            file_filter = "HTML Files (*.html)"
            default_suffix = ".html"
        elif out_format == "PDF":
            file_filter = "PDF Files (*.pdf)"
            default_suffix = ".pdf"
        else:
            QMessageBox.critical(self, "Error", "Unsupported output format")
            return
            
        # Create save dialog with native options
        dialog = QFileDialog(self)
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setViewMode(QFileDialog.Detail)
        dialog.setOption(QFileDialog.DontUseNativeDialog, False)  # Use native dialog
        dialog.setDirectory(os.path.expanduser("~/Documents"))  # Start from Documents
        dialog.setNameFilter(file_filter)
        dialog.setDefaultSuffix(default_suffix.lstrip('.'))
        
        # Enable access to all locations
        dialog.setOption(QFileDialog.ReadOnly, False)
        dialog.setOption(QFileDialog.HideNameFilterDetails, False)
        dialog.setSidebarUrls([
            QUrl.fromLocalFile(os.path.expanduser("~")),  # Home
            QUrl.fromLocalFile(os.path.expanduser("~/Documents")),  # Documents
            QUrl.fromLocalFile(os.path.expanduser("~/Downloads")),  # Downloads
            QUrl.fromLocalFile(os.path.expanduser("~/Desktop")),  # Desktop
            QUrl.fromLocalFile("/"),  # Root directory
        ])
        
        if dialog.exec():
            filename = dialog.selectedFiles()[0]
            if filename:
                try:
                    if not filename.endswith(default_suffix):
                        filename += default_suffix
                        
                    if out_format == "Text":
                        with open(filename, "w", encoding="utf-8") as f:
                            f.write(text)
                    elif out_format == "JSON":
                        with open(filename, "w", encoding="utf-8") as f:
                            json.dump({"text": text}, f, indent=4)
                    elif out_format == "CSV":
                        with open(filename, "w", newline="", encoding="utf-8") as f:
                            writer = csv.writer(f)
                            for line in text.splitlines():
                                writer.writerow([line])
                    elif out_format == "HTML":
                        html_content = f"<html><body><pre>{text}</pre></body></html>"
                        with open(filename, "w", encoding="utf-8") as f:
                            f.write(html_content)
                    elif out_format == "PDF":
                        try:
                            from fpdf import FPDF
                        except ImportError:
                            QMessageBox.critical(self, "Error", "fpdf module not installed. Please install it to save as PDF.")
                            return
                        pdf = FPDF()
                        pdf.add_page()
                        pdf.set_auto_page_break(auto=True, margin=15)
                        pdf.set_font("Arial", size=12)
                        for line in text.splitlines():
                            pdf.cell(0, 10, txt=line, ln=True)
                        pdf.output(filename)
                        
                    QMessageBox.information(self, "Success", "Output saved successfully!")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to save file: {str(e)}")
                
    def closeEvent(self, event):
        save_settings()
        super().closeEvent(event) 