from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="scrapey",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A comprehensive GUI tool for extracting text from PDFs, images, and web pages",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/scrapey",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Text Processing :: General",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Environment :: X11 Applications :: Qt",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
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