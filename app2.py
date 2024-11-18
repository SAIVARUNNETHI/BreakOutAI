from flask import Flask, request, render_template, redirect, send_file
import pandas as pd
import os

app = Flask(__name__)

# Directories
UPLOAD_FOLDER = 'uploads'
RESULT_FOLDER = 'extracted_results'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return render_template("DashBoard.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    file = request.files["file"]
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    data = pd.read_csv(filepath)
    preview = data.head().to_html(classes='table table-striped')
    return render_template("preview.html", preview=preview, filepath=filepath)

@app.route("/process-query", methods=["POST"])
def process_query():
    query = request.form.get("query")
    filepath = request.form.get("filepath")
    data = pd.read_csv(filepath)

    column = request.form.get("column", data.columns[0])  # Get the column name from the form or default to the first column
    results = []

    # Process each entity based on its data type
    for entity in data[column]:
        dynamic_query = query.replace("{entity}", str(entity))  # Ensure entity is treated as a string
        extracted_info = process_entity(entity, dynamic_query)
        results.append((entity, extracted_info))

    # Convert the results into a DataFrame and save them
    results_df = pd.DataFrame(results, columns=[column, "Extracted Information"])
    results_path = os.path.join(RESULT_FOLDER, "results.csv")
    results_df.to_csv(results_path, index=False)

    return render_template("results.html", results=results_df.values.tolist(), download_link=results_path)

@app.route("/download")
def download_csv():
    results_path = os.path.join(RESULT_FOLDER, "results.csv")
    return send_file(results_path, as_attachment=True)

# Function to process each entity based on its type
def process_entity(entity, query):
    """
    This function processes each entity depending on its data type.
    """
    if isinstance(entity, (int, float)):  # If the entity is numeric, handle differently
        return f"Processed numeric entity: {entity}"
    elif isinstance(entity, str):  # If the entity is a string, perform string operations
        return f"Processed string entity: {entity}"
    elif isinstance(entity, pd.Timestamp):  # If the entity is a timestamp (date)
        return f"Processed date entity: {entity.strftime('%Y-%m-%d')}"
    else:
        return f"Unsupported entity type: {type(entity)}"

if __name__ == "__main__":
    app.run(debug=True)
