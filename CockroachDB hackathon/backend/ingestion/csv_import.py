"""
CSV Fallback Ingestion — Import payment data from CSV files.

For SMEs that can't connect Stripe directly or want to import historical data.
Supports:
- Transaction history CSV
- Customer list CSV
- Invoice CSV
- Custom column mapping
"""

import csv
import io
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from ..api.auth import CurrentUser, check_sme_membership

router = APIRouter()


class ColumnMapping(BaseModel):
    """Maps CSV columns to our schema fields."""
    date_column: str = "date"
    amount_column: str = "amount"
    status_column: str = "status"
    customer_email_column: Optional[str] = "customer_email"
    customer_name_column: Optional[str] = "customer_name"
    currency_column: Optional[str] = "currency"
    description_column: Optional[str] = "description"
    failure_reason_column: Optional[str] = "failure_reason"
    transaction_id_column: Optional[str] = "transaction_id"


class CSVImportResult(BaseModel):
    total_rows: int
    imported: int
    skipped: int
    errors: list[str]


@router.post("/transactions", response_model=CSVImportResult)
async def import_transactions_csv(
    file: UploadFile = File(...),
    user: CurrentUser = Depends(check_sme_membership),
    date_column: str = "date",
    amount_column: str = "amount",
    status_column: str = "status",
    customer_email_column: Optional[str] = "customer_email",
):
    """
    Import transaction data from a CSV file.
    Maps CSV columns to the transactions schema.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    content = await file.read()
    decoded = content.decode("utf-8")
    reader = csv.DictReader(io.StringIO(decoded))

    imported = 0
    skipped = 0
    errors = []
    total_rows = 0

    for row_num, row in enumerate(reader, start=1):
        total_rows += 1
        try:
            # Parse required fields
            amount = float(row.get(amount_column, "0").replace("$", "").replace(",", ""))
            status = row.get(status_column, "succeeded").lower()
            date_str = row.get(date_column, "")

            # Parse date (support multiple formats)
            transaction_date = _parse_date(date_str)
            if not transaction_date:
                errors.append(f"Row {row_num}: Could not parse date '{date_str}'")
                skipped += 1
                continue

            # Normalize status
            status = _normalize_status(status)

            # TODO: Insert into CockroachDB transactions table
            # Also create/update customer record if email provided
            customer_email = row.get(customer_email_column, "") if customer_email_column else None

            imported += 1

        except Exception as e:
            errors.append(f"Row {row_num}: {str(e)}")
            skipped += 1

    return CSVImportResult(
        total_rows=total_rows,
        imported=imported,
        skipped=skipped,
        errors=errors[:20],  # Cap error list
    )


@router.post("/customers")
async def import_customers_csv(
    file: UploadFile = File(...),
    user: CurrentUser = Depends(check_sme_membership),
):
    """Import customer list from CSV."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    content = await file.read()
    decoded = content.decode("utf-8")
    reader = csv.DictReader(io.StringIO(decoded))

    imported = 0
    errors = []

    for row_num, row in enumerate(reader, start=1):
        try:
            email = row.get("email", "").strip()
            name = row.get("name", "").strip()

            if not email:
                errors.append(f"Row {row_num}: Missing email")
                continue

            # TODO: Upsert customer in CockroachDB
            imported += 1

        except Exception as e:
            errors.append(f"Row {row_num}: {str(e)}")

    return {
        "imported": imported,
        "errors": errors[:20],
    }


def _parse_date(date_str: str) -> Optional[datetime]:
    """Try multiple date formats."""
    formats = [
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%m/%d/%Y",
        "%d/%m/%Y",
        "%m-%d-%Y",
        "%d-%m-%Y",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except (ValueError, AttributeError):
            continue
    return None


def _normalize_status(status: str) -> str:
    """Normalize payment status from various CSV formats."""
    status_map = {
        "succeeded": "succeeded",
        "success": "succeeded",
        "paid": "succeeded",
        "completed": "succeeded",
        "failed": "failed",
        "failure": "failed",
        "declined": "failed",
        "pending": "pending",
        "processing": "pending",
        "refunded": "refunded",
        "refund": "refunded",
    }
    return status_map.get(status.lower(), "unknown")
