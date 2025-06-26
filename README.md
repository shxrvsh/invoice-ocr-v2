# Invoice Parser AI Application

![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)

This project is an end-to-end web application for extracting structured data from invoice images using advanced AI, OCR, and LLMs (Large Language Models). It features a Django frontend for user interaction and a FastAPI backend for processing, OCR, and LLM-based parsing.

---

## Table of Contents

- [Features](#features)
- [Architecture Overview](#architecture-overview)
- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
  - [1. Clone the Repository](#1-clone-the-repository)
  - [2. Python Environment](#2-python-environment)
  - [3. Install Dependencies](#3-install-dependencies)
  - [4. Environment Variables](#4-environment-variables)
  - [5. Model Weights](#5-model-weights)
  - [6. Database Migration](#6-database-migration)
  - [7. Running the Application](#7-running-the-application)
- [Usage](#usage)
- [Screenshots](#screenshots)
- [File/Folder Descriptions](#filefolder-descriptions)
- [Customization](#customization)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## Features

- **Invoice Upload:** Upload invoice images (JPG, PNG, etc.) via a web interface.
- **AI Layout Detection:** Uses Detectron2 (via LayoutParser) to detect layout blocks (text, tables, etc.).
- **OCR Extraction:** Extracts text from detected regions using Tesseract OCR.
- **LLM Parsing:** Sends extracted text to LLMs (Gemini, Cohere, Mistral) for structured JSON parsing.
- **Field Viewer:** Visualizes detected fields and their bounding boxes on the invoice image.
- **Document Chatbot:** Ask questions about the extracted invoice data using LLMs.
- **Multiple LLM Support:** Easily switch between Gemini, Cohere, and Mistral (Together) models.
- **Modern UI:** Clean, responsive frontend built with Django templates and CSS.

---

## Architecture Overview

```
[User] <---> [Django Frontend] <--HTTP--> [FastAPI Backend] <---> [LayoutParser/Detectron2 + Tesseract OCR + LLM APIs]
```

- **Frontend:** Django app (`frontend/invoice_app`) for user interaction, file upload, field viewing, and chatbot.
- **Backend:** FastAPI app (`backend/main.py`) for handling parsing and chat endpoints.
- **Parser:** Handles layout detection, OCR, and LLM routing (`backend/parser/`).
- **Models:** Pickled files storing extracted data and field mappings (`backend/models/`).

---

## Project Structure

```
project/
  v2/
    backend/
      main.py           # FastAPI backend entrypoint
      config.py
      models/           # Pickled invoice data
      parser/
        ocr_layout.py   # Layout detection & OCR
        llm_router.py   # LLM API calls & routing
        matcher.py      # Field-to-box mapping
    frontend/
      manage.py         # Django entrypoint
      invoice_app/
        views.py        # Django views (upload, viewer, chatbot)
        templates/
        static/
        uploads/
    .env                # Environment variables (API keys, etc.)
```

---

## Setup Instructions

### 1. Clone the Repository

```sh
git clone https://github.com/shxrvsh/invoice-ocr-v2.git
```

### 2. Python Environment

Create and activate a virtual environment (recommended):

```sh
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

Install requirements for both backend and frontend:

```sh
pip install -r requirements.txt
# If requirements.txt is split, install for both Django and FastAPI
pip install django fastapi uvicorn layoutparser opencv-python pillow python-dotenv requests
# For Detectron2 (follow official instructions): https://detectron2.readthedocs.io/en/latest/tutorials/install.html
```

### 4. Environment Variables

Create a `.env` file in both `backend/` and `frontend/` as needed. Example:

```
GEMINI_API_KEY=your_gemini_api_key
COHERE_API_KEY=your_cohere_api_key
TOGETHER_API_KEY=your_together_api_key
API_KEY=your_gemini_api_key  # For frontend if needed
```

### 5. Model Weights

- Download the Detectron2 PubLayNet model weights from the [official source](https://layout-parser.github.io/guide/models.html).
- After downloading, specify the local path to the model weights in your code or configuration, for example:
  model_path="/path/to/your/model_final.pth"
- Do NOT use the sample path from this README; use your own path where you saved the weights.

### 6. Database Migration

For Django:

```sh
cd frontend
python manage.py migrate
```

### 7. Running the Application

**Start the FastAPI backend:**

```sh
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Start the Django frontend:**

```sh
cd frontend
python manage.py runserver 8001
```

- Access the app at: http://localhost:8000 (FastAPI) and http://localhost:8001 (Django by default)

---

## Usage

1. **Home:** Visit the home page for an overview.
2. **Upload:** Go to the Upload page, select an invoice image, and choose an LLM.
3. **Viewer:** After upload, view detected fields and bounding boxes on the invoice.
4. **Chatbot:** Ask questions about the extracted invoice data.

---

## Screenshots


### Home Page

![Home Screenshot](https://raw.githubusercontent.com/shxrvsh/invoice-ocr-v2/main/Screenshots/main_page.png)

### Upload Page

![Upload Screenshot](https://raw.githubusercontent.com/shxrvsh/invoice-ocr-v2/main/Screenshots/upload_page.png)

### Viewer Page

![Viewer Screenshot](https://raw.githubusercontent.com/shxrvsh/invoice-ocr-v2/main/Screenshots/viewer_page.png)

### ChatBot Page

![ChatBot Screenshot](https://raw.githubusercontent.com/shxrvsh/invoice-ocr-v2/main/Screenshots/chatbot_page.png)



---

## File/Folder Descriptions

- **backend/main.py**: FastAPI endpoints for `/parse` (invoice parsing) and `/chat` (chatbot Q&A).
- **backend/parser/ocr_layout.py**: Handles layout detection and OCR extraction.
- **backend/parser/llm_router.py**: Routes prompts to Gemini, Cohere, or Mistral APIs.
- **backend/models/**: Stores pickled invoice data for each upload.
- **frontend/invoice_app/views.py**: Django views for upload, viewer, and chatbot.
- **frontend/invoice_app/templates/**: HTML templates for all pages.
- **frontend/invoice_app/static/**: CSS and static assets.
- **frontend/invoice_app/uploads/**: Uploaded invoice files.
- **.env**: API keys and configuration.

---

## Customization

- **Add new LLMs:** Extend [`llm_router.py`](backend/parser/llm_router.py) with new API calls.
- **Change model weights:** Update the `model_path` in [`ocr_layout.py`](backend/parser/ocr_layout.py).
- **UI tweaks:** Edit CSS in [`style.css`](frontend/invoice_app/static/invoice_app/style.css) or templates in [`templates/`](frontend/invoice_app/templates/invoice_app/).

---

## Troubleshooting

- **Model not found:** Ensure the Detectron2 weights are downloaded and the path is correct.
- **API errors:** Check your `.env` for valid API keys.
- **OCR issues:** Make sure Tesseract is installed and accessible.
- **CORS issues:** If running frontend/backend on different ports, configure CORS in FastAPI.

---
## Acknowledgements

- Document layout detection powered by [LayoutParser](https://github.com/Layout-Parser/layout-parser) and [Detectron2](https://github.com/facebookresearch/detectron2)
- Layout models based on [PubLayNet](https://github.com/ibm-aur-nlp/PubLayNet)
- OCR by [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
- Invoice dataset: [Kaggle - High-Quality Invoice Images for OCR](https://www.kaggle.com/datasets/osamahosamabdellatif/high-quality-invoice-images-for-ocr)
- LLM-powered parsing using APIs from:
  - [Gemini (Google AI)](https://deepmind.google/technologies/gemini/)
  - [Cohere](https://cohere.com/)
  - [Together AI](https://www.together.ai/)

Special thanks to the open-source community!

---

## Previous Versions

You can also check out the original version of this project here:  
[Invoice OCR - Version 1 (Prototype)](https://github.com/shxrvsh/invoice-ocr-v1)

## License

This project is licensed under the [Creative Commons Attribution-NonCommercial 4.0 International License (CC BY-NC 4.0)](https://creativecommons.org/licenses/by-nc/4.0/).  
You may use this code for personal or educational purposes.  
**Commercial use is not permitted without permission — contact the author for licensing.**