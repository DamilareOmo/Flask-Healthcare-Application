"""
models/user.py

Defines the User class used to represent a single survey respondent.
Each User wraps the raw MongoDB document and exposes convenience
properties/methods used by export_to_csv.py and the analysis notebook.
"""

from dataclasses import dataclass, field
from typing import Dict


# The five expense categories the survey form collects.
EXPENSE_CATEGORIES = ["utilities", "entertainment", "school_fees", "shopping", "healthcare"]


@dataclass
class User:
    """Represents one survey respondent and their income/expense data."""

    age: int
    gender: str
    total_income: float
    expenses: Dict[str, float] = field(default_factory=dict)

    @classmethod
    def from_mongo_doc(cls, doc: dict) -> "User":
        """Build a User from a raw MongoDB document."""
        expenses = {cat: float(doc.get("expenses", {}).get(cat, 0) or 0) for cat in EXPENSE_CATEGORIES}
        return cls(
            age=int(doc.get("age", 0)),
            gender=str(doc.get("gender", "unknown")),
            total_income=float(doc.get("total_income", 0) or 0),
            expenses=expenses,
        )

    @property
    def total_expenses(self) -> float:
        return sum(self.expenses.values())

    @property
    def savings(self) -> float:
        """Income left over after expenses (can be negative)."""
        return self.total_income - self.total_expenses

    def to_csv_row(self) -> dict:
        """Flatten this user into a single dict suitable for a CSV row."""
        row = {
            "age": self.age,
            "gender": self.gender,
            "total_income": self.total_income,
            "total_expenses": self.total_expenses,
            "savings": self.savings,
        }
        for cat in EXPENSE_CATEGORIES:
            row[f"expense_{cat}"] = self.expenses.get(cat, 0)
        return row

    @staticmethod
    def csv_fieldnames() -> list:
        fields = ["age", "gender", "total_income", "total_expenses", "savings"]
        fields += [f"expense_{cat}" for cat in EXPENSE_CATEGORIES]
        return fields
