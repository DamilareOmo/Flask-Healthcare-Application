"""
app.py

Flask web app that collects survey responses (age, gender, total income,
and expenses broken out by category) and stores each submission as a
document in MongoDB.

Run locally:
    python app.py

Environment variables are read via config.py / .env (see .env.example).
"""

from datetime import datetime, timezone

from flask import Flask, render_template, request, redirect, url_for, flash
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from config import Config
from models.user import EXPENSE_CATEGORIES

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.FLASK_SECRET_KEY

# --- MongoDB connection -----------------------------------------------------
client = MongoClient(Config.MONGO_URI)
db = client[Config.MONGO_DB_NAME]
collection = db[Config.MONGO_COLLECTION]

CATEGORY_LABELS = {
    "utilities": "Utilities",
    "entertainment": "Entertainment",
    "school_fees": "School Fees",
    "shopping": "Shopping",
    "healthcare": "Healthcare",
}


@app.route("/", methods=["GET"])
def index():
    return render_template(
        "index.html",
        categories=EXPENSE_CATEGORIES,
        category_labels=CATEGORY_LABELS,
    )


@app.route("/submit", methods=["POST"])
def submit():
    try:
        age = int(request.form.get("age", 0))
        gender = request.form.get("gender", "").strip()
        total_income = float(request.form.get("total_income", 0) or 0)

        expenses = {}
        for category in EXPENSE_CATEGORIES:
            # Only record an amount if the checkbox for that category was ticked
            if request.form.get(f"has_{category}"):
                amount = request.form.get(f"amount_{category}", "0")
                expenses[category] = float(amount or 0)
            else:
                expenses[category] = 0.0

        if age <= 0 or age > 120:
            flash("Please enter a valid age.", "error")
            return redirect(url_for("index"))
        if not gender:
            flash("Please select a gender.", "error")
            return redirect(url_for("index"))
        if total_income < 0:
            flash("Total income cannot be negative.", "error")
            return redirect(url_for("index"))

        document = {
            "age": age,
            "gender": gender,
            "total_income": total_income,
            "expenses": expenses,
            "submitted_at": datetime.now(timezone.utc),
        }

        collection.insert_one(document)
        flash("Thank you! Your response has been recorded.", "success")
        return redirect(url_for("index"))

    except (ValueError, TypeError):
        flash("There was a problem with your submission. Please check your entries.", "error")
        return redirect(url_for("index"))
    except PyMongoError:
        flash("We couldn't save your response right now. Please try again shortly.", "error")
        return redirect(url_for("index"))


@app.route("/health")
def health():
    """Simple health check endpoint, useful for AWS load balancer checks."""
    try:
        client.admin.command("ping")
        return {"status": "ok", "mongo": "connected"}, 200
    except PyMongoError:
        return {"status": "degraded", "mongo": "unreachable"}, 503


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=Config.FLASK_DEBUG)
