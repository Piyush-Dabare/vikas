from flask import Flask, jsonify, request
import pandas as pd
from datetime import datetime

app = Flask(__name__)

# Load and prepare the dataset from GitHub
df = pd.read_csv(
    "https://raw.githubusercontent.com/VIKASBHOSALE1/API_data/main/Generated_data1.csv",
    parse_dates=["Date"]
)
df = df.sort_values(by="Date").reset_index(drop=True)

min_date = df["Date"].min().date()
max_date = df["Date"].max().date()


@app.route("/", methods=["GET"])
def home():
    """Provides API usage information"""
    return jsonify({
        "message": "Welcome to the Date Filtering API!",
        "usage": "/data?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD",
        "available_data_range": {
            "min_date": min_date.strftime("%Y-%m-%d"),
            "max_date": max_date.strftime("%Y-%m-%d")
        }
    })


@app.route("/data", methods=["GET"])
def get_data():
    # Expect start_date and end_date from the client
    start_date_str = request.args.get("start_date")
    end_date_str = request.args.get("end_date")

    if not start_date_str or not end_date_str:
        return jsonify({
            "error": "Missing parameters: Provide both start_date and end_date in YYYY-MM-DD format."
        }), 400

    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

    if start_date > end_date:
        return jsonify({"error": "start_date cannot be after end_date."}), 400

    # Validate that the requested dates fall within the dataset's range
    if start_date < min_date or end_date > max_date:
        return jsonify({
            "error": "Requested dates exceed available dataset range.",
            "dataset_min_date": min_date.strftime("%Y-%m-%d"),
            "dataset_max_date": max_date.strftime("%Y-%m-%d")
        }), 400

    # Filter the DataFrame for the specified date range
    filtered_df = df[(df["Date"].dt.date >= start_date) & (df["Date"].dt.date <= end_date)]
    result = filtered_df.to_dict(orient="records")

    response = jsonify({
        "start_date": start_date_str,
        "end_date": end_date_str,
        "data_count": len(result),
        "data": result
    })

    # Prevent caching issues
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"

    return response

# vikas
if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5003)
