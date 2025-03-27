import sys
import logging
from PySide6.QtWidgets import QApplication
from scrapey.gui.main_window import MainWindow
from scrapey.utils import load_settings

def main():
    # Configure logging
    logging.basicConfig(
        filename='scrapey.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Load application settings
    load_settings()
    
    # Create Qt application
    app = QApplication(sys.argv)
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Start event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 