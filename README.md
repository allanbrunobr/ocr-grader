# OCR Grader

An intelligent OCR system for grading exams and documents with advanced content detection capabilities, including text, graphs, equations, and statistical charts.

## Features

- Multi-format document processing (PDF, PNG, JPG, JPEG)
- Advanced text extraction with multiple OCR engines
- Intelligent content detection:
    - Statistical graphs and charts
    - Mathematical equations
    - Text in multiple languages (Portuguese and English)
- Automated grading system using ChatGPT
- Web interface for easy document submission
- Detailed analysis and feedback generation

## Prerequisites

```bash
python 3.8+
tesseract-ocr
poppler-utils

Installation
------------

1.  Clone the repository:

```
git clone https://github.com/yourusername/ocr-grader.git
cd ocr-grader

```

CopyApply

1.  Install dependencies:

```
pip install -r requirements.txt

```

CopyApply

1.  Set up environment variables:

```
export GOOGLE_APPLICATION_CREDENTIALS="./credentials/credentials.json"

```

CopyApply

Usage
-----

### Web Interface

Run the Flask application:

```
python app_gcloud_vision.py

```

Access the web interface at `http://localhost:5000`

### Key Components

-   `process_document()`: Handles single image processing
-   `process_pdf()`: Processes multi-page PDF documents
-   `detect_graphs()`: Identifies and extracts graphical content
-   `extract_graph_text()`: Extracts text from graphs using EasyOCR
-   `detect_content()`: Comprehensive content detection system

Processing Pipeline
-------------------

1.  Document Upload
2.  Preprocessing
    -   Image enhancement
    -   Noise reduction
    -   Contrast adjustment
3.  Content Detection
    -   Text extraction
    -   Graph detection
    -   Equation recognition
4.  Analysis
    -   Content interpretation
    -   Automated grading
    -   Feedback generation

Output Format
-------------

The system generates structured output including:

-   Extracted text
-   Detected graphs and charts
-   Mathematical equations
-   Comprehensive analysis
-   Grading feedback

Technologies Used
-----------------

-   OpenCV for image processing
-   Tesseract OCR for text extraction
-   EasyOCR for complex text scenarios
-   Google Cloud Vision API
-   Flask for web interface
-   ChatGPT for analysis and grading

Contributing
------------

Contributions are welcome! Please feel free to submit a Pull Request.

License
-------

This project is licensed under the MIT License - see the LICENSE file for details.
