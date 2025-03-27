# Scrapey

A powerful text extraction tool that can extract text from various sources including PDFs, scanned documents, and web pages.

## Features

- Extract text from PDF documents (both text-based and scanned)
- OCR support for scanned documents using Tesseract or EasyOCR
- Web page text extraction
- Modern Qt-based GUI
- Support for multiple output formats
- Customizable settings

## Requirements

- Python 3.9 or higher
- Tesseract OCR (for OCR functionality)
- Poppler (for PDF processing)

### macOS Installation

1. Install Homebrew if you haven't already:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

2. Install required system dependencies:
```bash
brew install tesseract
brew install poppler
```

3. Download the latest release from the [Releases](https://github.com/thatssomoneybaby/scrapey/releases) page.

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/thatssomoneybaby/scrapey.git
cd scrapey
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python -m scrapey.main
```

## Building from Source

To build the application from source:

```bash
pyinstaller scrapey.spec
```

The built application will be available in the `dist` directory.

## Usage

1. Launch Scrapey
2. Choose your input source (PDF, scanned document, or web page)
3. Select your preferred OCR engine and settings
4. Click "Extract" to process the document
5. Save or copy the extracted text

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 