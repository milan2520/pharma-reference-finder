# Pharma Reference Finder

## Project Overview
Pharma Reference Finder is a web-based application that helps users search for pharmaceutical drug information and clinical trials using trusted public data sources.

## Features
- Search pharmaceutical drug information.
- Search clinical trials.
- Retrieve drug labels from the FDA OpenFDA API.
- Retrieve clinical trial information from ClinicalTrials.gov.
- Save search history using SQLite.
- Store reference links.
- Manually update reference verification status.
- Responsive and user-friendly interface.
- Input validation and error handling.

## Technologies Used

### Frontend
- HTML
- CSS
- JavaScript

### Backend
- Python
- FastAPI
- Uvicorn

### Database
- SQLite

### External APIs
- OpenFDA Drug Label API
- ClinicalTrials.gov API

## Project Structure

```text
web development/
│
├── backend/
│   ├── clinical_trials.py
│   ├── database.py
│   ├── drug_search.py
│   └── main.py
│
├── database/
│   └── pharma.db
│
├── frontend/
│   ├── index.html
│   ├── script.js
│   └── style.css
│
├── venv/
│
└── README.md
```

## How to Run the Project

### 1. Open the project folder

Open the project in Visual Studio Code.

### 2. Activate the virtual environment

On Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install fastapi uvicorn requests
```

### 4. Start the backend

```bash
cd backend
python -m uvicorn main:app --reload
```

### 5. Open the frontend

Open `frontend/index.html` in your web browser.

### 6. API documentation

Visit:

http://127.0.0.1:8000/docs

## How to Use

1. Open the Pharma Reference Finder website.
2. Select Drug Search or Clinical Trial Search.
3. Enter a search keyword.
4. Click the Search button.
5. View the results.
6. Open Search History to see previous searches.
7. View saved references and update their manual review status.

## Future Enhancements
- User authentication.
- Export search results as PDF.
- Advanced drug filtering.
- Improved reference review workflow.
- Deployment to a public server.

## Disclaimer

This application is intended for educational and research purposes only. It does not provide medical advice or replace professional medical consultation. Reference verification status is manually assigned and does not guarantee scientific accuracy.

## Author
Student Project