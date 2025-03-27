import logging
import configparser
import os

# Configure a basic logger
logging.basicConfig(
    filename='scrapey.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

# Global app settings stored in memory
app_settings = {
    'ocr_language': 'eng',
    'default_ocr_engine': 'tesseract',
    'default_output_format': 'Text'
}

def load_settings():
    config = configparser.ConfigParser()
    if os.path.exists('scrapey.ini'):
        config.read('scrapey.ini')
        if 'Settings' in config:
            app_settings['ocr_language'] = config['Settings'].get('ocr_language', 'eng')
            app_settings['default_ocr_engine'] = config['Settings'].get('default_ocr_engine', 'tesseract')
            app_settings['default_output_format'] = config['Settings'].get('default_output_format', 'Text')

def save_settings():
    config = configparser.ConfigParser()
    config['Settings'] = {
        'ocr_language': app_settings['ocr_language'],
        'default_ocr_engine': app_settings['default_ocr_engine'],
        'default_output_format': app_settings['default_output_format']
    }
    with open('scrapey.ini', 'w') as f:
        config.write(f)

def check_dependency(import_name, friendly_name=None):
    try:
        __import__(import_name)
        return True
    except ImportError:
        if not friendly_name:
            friendly_name = import_name
        from tkinter import messagebox
        messagebox.showerror(
            "Missing Dependency",
            f"Required module '{friendly_name}' is not installed. Please install it and re-run Scrapey.\n\n"
            f"Try: pip install {friendly_name}"
        )
        return False 