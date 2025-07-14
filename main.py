from flask import Flask, request, render_template, redirect, url_for
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json

app = Flask(__name__)

# ✅ Google Sheets Setup (compatible with Render & local)
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

if os.environ.get("RENDER"):
    # On Render: use GOOGLE_CREDENTIALS env variable
    GOOGLE_CREDS = os.environ.get("GOOGLE_CREDENTIALS")
    creds_dict = json.loads(GOOGLE_CREDS)
else:
    # Local: use credentials.json file
    with open("credentials.json") as f:
        creds_dict = json.load(f)

creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# ✅ Open your sheet by exact name
sheet = client.open("Expenses Tracker").sheet1  # Match Google Sheet title exactly

# ✅ Ensure header row exists
expected_headers = [
    "Entry Type", "Date", "Project Name", "Amount By", "Amount",
    "Invoice Number", "Party Name", "Expense For", "Description", "Labour Name"
]

existing_headers = sheet.row_values(1)
if existing_headers != expected_headers:
    sheet.delete_rows(1)  # Remove old header if needed
    sheet.insert_row(expected_headers, index=1)  # Add correct header

@app.route('/')
def index():
    success = request.args.get("success") == "true"
    return render_template("form.html", success=success)

@app.route('/submit', methods=['POST'])
def submit():
    data = [
        request.form.get("entry_type"),
        request.form.get("date"),
        request.form.get("project_name"),
        request.form.get("amount_by"),
        f"₹{request.form.get('amount')}",
        request.form.get("invoice_number", ""),
        request.form.get("party_name", ""),
        request.form.get("expense_for", ""),
        request.form.get("description", ""),
        request.form.get("labour_name", "")
    ]

    sheet.append_row(data)
    return redirect(url_for('index', success='true'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81)  # Works on Render, Replit, and local
