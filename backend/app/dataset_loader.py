"""CSV dataset loading and validation for burnout training."""

from __future__ import annotations

import csv
import io
from typing import Any

REQUIRED_COLUMNS = ["Sleep", "Meetings", "Weekends", "Stress", "Target"]
FEATURE_COLUMNS = ["Sleep", "Meetings", "Weekends", "Stress"]
ALLOWED_TARGETS = {
    "healthy",
    "risk of burnout",
    "vacation required",
    "critical condition",
}
ALLOWED_WEEKENDS = {"YES", "NO"}


class DatasetError(ValueError):
    """Raised when dataset validation fails."""


# Small built-in fallback used only when no CSV upload is provided.
FALLBACK_ROWS: list[dict[str, Any]] = [
    {"Sleep": 8, "Meetings": 2, "Weekends": "NO", "Stress": 3, "Target": "healthy"},
    {"Sleep": 7.5, "Meetings": 3, "Weekends": "NO", "Stress": 4, "Target": "healthy"},
    {"Sleep": 7, "Meetings": 4, "Weekends": "NO", "Stress": 5, "Target": "healthy"},
    {"Sleep": 6.5, "Meetings": 5, "Weekends": "YES", "Stress": 6, "Target": "risk of burnout"},
    {"Sleep": 6, "Meetings": 6, "Weekends": "YES", "Stress": 7, "Target": "risk of burnout"},
    {"Sleep": 5.5, "Meetings": 7, "Weekends": "YES", "Stress": 8, "Target": "vacation required"},
    {"Sleep": 5, "Meetings": 8, "Weekends": "YES", "Stress": 9, "Target": "vacation required"},
    {"Sleep": 4, "Meetings": 9, "Weekends": "YES", "Stress": 10, "Target": "critical condition"},
    {"Sleep": 4.5, "Meetings": 10, "Weekends": "YES", "Stress": 9, "Target": "critical condition"},
    {"Sleep": 3.5, "Meetings": 8, "Weekends": "YES", "Stress": 10, "Target": "critical condition"},
    {"Sleep": 8, "Meetings": 1, "Weekends": "NO", "Stress": 2, "Target": "healthy"},
    {"Sleep": 6, "Meetings": 5, "Weekends": "NO", "Stress": 6, "Target": "risk of burnout"},
    {"Sleep": 5, "Meetings": 6, "Weekends": "YES", "Stress": 7, "Target": "vacation required"},
    {"Sleep": 4, "Meetings": 7, "Weekends": "YES", "Stress": 8, "Target": "critical condition"},
    {"Sleep": 7, "Meetings": 3, "Weekends": "NO", "Stress": 5, "Target": "healthy"},
]


def get_fallback_dataset() -> list[dict[str, Any]]:
    return [dict(row) for row in FALLBACK_ROWS]


def parse_csv_content(content: str) -> list[dict[str, Any]]:
    if not content.strip():
        raise DatasetError("Dataset file is empty.")

    reader = csv.DictReader(io.StringIO(content))
    if reader.fieldnames is None:
        raise DatasetError("CSV has no header row.")

    headers = [name.strip() for name in reader.fieldnames]
    missing = [col for col in REQUIRED_COLUMNS if col not in headers]
    if missing:
        raise DatasetError(f"Missing required columns: {', '.join(missing)}")

    rows: list[dict[str, Any]] = []
    for line_no, raw_row in enumerate(reader, start=2):
        row = {key.strip(): (value.strip() if value is not None else "") for key, value in raw_row.items()}
        if not any(row.values()):
            continue

        try:
            validated = _validate_row(row, line_no)
        except DatasetError:
            raise
        rows.append(validated)

    if not rows:
        raise DatasetError("Dataset contains no valid data rows.")

    return rows


def _validate_row(row: dict[str, str], line_no: int) -> dict[str, Any]:
    try:
        sleep = float(row["Sleep"])
        meetings = float(row["Meetings"])
        stress = float(row["Stress"])
    except ValueError as exc:
        raise DatasetError(f"Line {line_no}: Sleep, Meetings, and Stress must be numeric.") from exc

    weekends = row["Weekends"].strip().upper()
    if weekends not in ALLOWED_WEEKENDS:
        raise DatasetError(
            f"Line {line_no}: Weekends must be YES or NO, got '{row['Weekends']}'."
        )

    target = row["Target"].strip().lower()
    if target not in ALLOWED_TARGETS:
        raise DatasetError(
            f"Line {line_no}: unsupported Target '{row['Target']}'. "
            f"Allowed: {', '.join(sorted(ALLOWED_TARGETS))}."
        )

    return {
        "Sleep": sleep,
        "Meetings": meetings,
        "Weekends": weekends,
        "Stress": stress,
        "Target": target,
    }
