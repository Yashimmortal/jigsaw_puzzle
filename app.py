import os
from flask import Flask, request, jsonify
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)

@app.route('/')
def home():
    return "Backend is running! (Jigsaw API Server)"
CORS(app)  # Allow requests from browser

# --- GOOGLE SHEET SETUP ---
SHEET_NAME = "Jigsaw Scores"
CRED_PATH = "gcreds.json"

def save_score_to_sheet(name, puzzle_scores, total):
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(CRED_PATH, scope)
    client = gspread.authorize(creds)
    sheet = client.open(SHEET_NAME).sheet1
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = [name] + puzzle_scores + [total, timestamp]
    sheet.append_row(row)

@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_json()
    name = data.get("name", "")
    puzzles = data.get("puzzles", [])

    puzzle_scores = []
    total_score = 0

    for puzzle in puzzles:
        arr = puzzle['arrangement']    # Player's arrangement: list of 24 ints (piece numbers)
        correct = puzzle['correct']    # Always [1,2,3,...,24]
        points = 0
        # Score 1 point for each correct placement
        for i in range(len(correct)):
            if arr[i] == correct[i]:
                points += 1
        # 5 bonus if puzzle is perfect
        if points == 24:
            points += 5
        puzzle_scores.append(points)
        total_score += points

    # Save to Google Sheet
    save_score_to_sheet(name, puzzle_scores, total_score)

    # Respond with thank you (no scores)
    return jsonify({"msg": "Submitted!"})

if __name__ == '__main__':
    app.run(debug=True)
