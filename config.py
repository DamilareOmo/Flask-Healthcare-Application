"""
config.py

Central configuration for the survey app, driven entirely by environment
variables so the same code works with local MongoDB, MongoDB Atlas, or
any other deployment target without code changes.

Set these in a `.env` file (see `.env.example`) or in your shell/AWS
environment before running the app.
"""

import os
from dotenv import load_dotenv

load_dotenv()  # loads variables from a .env file if present, no-op otherwise


class Config:
    # Full MongoDB connection string.
    # Local example:  mongodb://localhost:27017
    # Atlas example:  mongodb+srv://<user>:<password>@<cluster>.mongodb.net
    MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB_NAME = os.environ.get("MONGO_DB_NAME", "survey_db")
    MONGO_COLLECTION = os.environ.get("MONGO_COLLECTION", "responses")

    # Flask
    FLASK_SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key-change-me")
    FLASK_DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"

    # Where export_to_csv.py writes its output
    CSV_OUTPUT_PATH = os.environ.get("CSV_OUTPUT_PATH", "data/survey_export.csv")
