from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="scrapey",
    version="1.0.0",
    description="A comprehensive GUI tool for extracting text from various sources",
    author="thatssomoneybaby",
    author_email="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/thatssomoneybaby/scrapey",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Text Processing :: General",
    ],
    python_requires=">=3.9",
    install_requires=[
        "PySide6>=6.4.0",
        "pdf2image>=1.16.3",
        "pytesseract>=0.3.10",
        "easyocr>=1.7.1",
        "beautifulsoup4>=4.12.2",
        "requests>=2.31.0",
        "Pillow>=10.0.0",
        "numpy>=1.24.0",
        "scipy>=1.10.0",
        "torch>=2.0.0",
        "torchvision>=0.15.0"
    ],
    entry_points={
        "console_scripts": [
            "scrapey=scrapey.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "scrapey": ["*.ini"],
    },
) 