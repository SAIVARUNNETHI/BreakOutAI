from flask import Flask, request, render_template, send_file, redirect
import pandas as pd
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from serpapi import GoogleSearch
import openai

app = Flask(__name__)

# Directories
UPLOAD_FOLDER = 'uploads'
RESULT_FOLDER = 'extracted_results'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

# API Keys
SERPAPI_KEY = "serpapi-key"  
OPENAI_API_KEY = "openai-key" 
openai.api_key = OPENAI_API_KEY

# Routes
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    file = request.files["file"]
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    # Load and preview the file
    try:
        data = pd.read_csv(filepath)
    except Exception as e:
        return f"Error loading CSV file: {e}"

    preview = data.head().to_html(classes='table table-striped')
    return render_template("preview.html", preview=preview, source='file', filepath=filepath)

@app.route("/connect-sheet", methods=["POST"])
def connect_sheet():
    sheet_url = request.form.get("sheet_url")
    sheet_id = sheet_url.split("/")[5]  # Extracting sheet ID from the URL

    # Connecting to Google Sheets API
    try:
        credentials = service_account.Credentials.from_service_account_file(
            "path/to/credentials.json",  # Replace with the path to your credentials file
            scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
        )
        service = build("sheets", "v4", credentials=credentials)
        sheet = service.spreadsheets()

        # Fetching data from the Google Sheet
        result = sheet.values().get(spreadsheetId=sheet_id, range="Sheet1").execute()
        values = result.get("values", [])

        # Convert to DataFrame and save locally
        df = pd.DataFrame(values[1:], columns=values[0])
        preview = df.head().to_html(classes='table table-striped')
        df.to_csv(os.path.join(UPLOAD_FOLDER, "sheet_data.csv"), index=False)
    except Exception as e:
        return f"Error connecting to Google Sheets: {e}"

    return render_template("preview.html", preview=preview, source='sheet', filepath="sheet_data.csv")

@app.route("/process-query", methods=["POST"])
def process_query():
    query = request.form.get("query")
    filepath = request.form.get("filepath")
    
    # Reading the CSV file (could be from upload or Google Sheets)
    try:
        data = pd.read_csv(filepath)
    except Exception as e:
        return f"Error loading CSV file: {e}"

    results = []
    for column in data.columns:
        for entity in data[column]:
            dynamic_query = query.replace("{entity}", str(entity))
            search_results = perform_search(dynamic_query)
            extracted_info = extract_information(query, search_results)
            results.append((entity, extracted_info))

    results_df = pd.DataFrame(results, columns=[column, "Extracted Information"])
    results_path = os.path.join(RESULT_FOLDER, "results.csv")
    results_df.to_csv(results_path, index=False)

    return render_template("results.html", results=results_df.values.tolist(), download_link=results_path)

@app.route("/download")
def download_csv():
    results_path = os.path.join(RESULT_FOLDER, "results.csv")
    return send_file(results_path, as_attachment=True)

# Utilities
def perform_search(query):
    search = GoogleSearch({
        "q": query,
        "api_key": SERPAPI_KEY
    })
    results = search.get_dict()
    return results.get("organic_results", [])

def extract_information(prompt, search_results):
    combined_prompt = f"{prompt}\n\nResults:\n{search_results}"
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=combined_prompt,
        max_tokens=150
    )
    return response.choices[0].text.strip()

if __name__ == "__main__":
    app.run(debug=True)
