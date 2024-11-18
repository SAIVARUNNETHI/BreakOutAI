# BreakOutAI

Here's a concise summary for your README.md:

Data Extraction Web App
This web app allows users to upload CSV files or connect to Google Sheets and perform dynamic queries. It processes the data, performs searches using external APIs, and extracts relevant information. The results can be downloaded as a CSV file.

Features:
Upload CSV or connect to Google Sheets.
Enter queries using {entity} as a placeholder for column values.
Extract information from search results using APIs.
Download extracted results as a CSV.
Files:
app.py: Uses SerpAPI and OpenAI APIs to perform Google searches and extract information.
app2.py: A version that works without APIs, processes data locally based on static queries.
Requirements:
Python 3.x
Install dependencies:


pip install -r requirements.txt
Set up Google Sheets API and SerpAPI and OpenAI keys (for app.py).
Running the App:
For API-based processing (app.py), run:
python app.py

For local processing (app2.py), run:

python app2.py
This version doesn’t require API keys.

Video link :  https://youtu.be/AIvTywkLcug
