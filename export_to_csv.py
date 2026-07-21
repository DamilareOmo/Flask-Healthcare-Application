"""
export_to_csv.py

Connects to MongoDB, loops through every stored survey response, wraps
each one in a `User` object, and writes the flattened result to a CSV
file that the Jupyter notebook then loads for analysis.

Run:
    python export_to_csv.py
"""

import csv
import os
import sys

from pymongo import MongoClient
from pymongo.errors import PyMongoError

from config import Config
from models.user import User


def fetch_users(collection) -> list:
    """Loop through every MongoDB document and turn it into a User object."""
    users = []
    for doc in collection.find({}):
        users.append(User.from_mongo_doc(doc))
    return users


def write_csv(users: list, output_path: str) -> None:
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=User.csv_fieldnames())
        writer.writeheader()
        for user in users:
            writer.writerow(user.to_csv_row())


def main():
    try:
        client = MongoClient(Config.MONGO_URI, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
    except PyMongoError as exc:
        print(f"Could not connect to MongoDB at {Config.MONGO_URI}: {exc}", file=sys.stderr)
        sys.exit(1)

    db = client[Config.MONGO_DB_NAME]
    collection = db[Config.MONGO_COLLECTION]

    users = fetch_users(collection)
    if not users:
        print("No survey responses found in MongoDB — nothing to export.")
        return

    write_csv(users, Config.CSV_OUTPUT_PATH)
    print(f"Exported {len(users)} responses to {Config.CSV_OUTPUT_PATH}")


if __name__ == "__main__":
    main()
