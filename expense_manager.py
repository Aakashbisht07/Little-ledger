"""
Little Ledger - Expense Management Service
Implements audited CRUD operations, search filters, pagination, CSV import/export, and schema validation.
Falls back to CSV file when MongoDB is offline.
"""

import io
import csv
import json
import logging
from typing import List, Dict, Any, Optional, Tuple, Union
from datetime import datetime, date
from pathlib import Path

from database import get_db, serialize_doc
from config import CATEGORIES, PAYMENT_METHODS, DEFAULT_USER_ID, DEFAULT_CURRENCY, DATA_DIR

logger = logging.getLogger("little_ledger.expense_manager")

CSV_FALLBACK_PATH = DATA_DIR / "little_ledger_transactions.csv"


def _load_csv_expenses(user_id: str = DEFAULT_USER_ID) -> List[Dict[str, Any]]:
    """Load expenses from CSV fallback file."""
    if not CSV_FALLBACK_PATH.exists():
        return []
    records = []
    with open(CSV_FALLBACK_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            try:
                uid = row.get("user_id", DEFAULT_USER_ID).strip()
                if uid != user_id:
                    continue
                date_str = (row.get("date") or "").strip()
                try:
                    dt = datetime.fromisoformat(date_str.replace("Z", "+00:00")[:19])
                except Exception:
                    dt = datetime.utcnow()
                records.append({
                    "id": f"csv_{i}",
                    "_id": f"csv_{i}",
                    "user_id": uid,
                    "amount": float(row.get("amount", 0) or 0),
                    "currency": row.get("currency", DEFAULT_CURRENCY).strip(),
                    "merchant": row.get("merchant", "").strip(),
                    "category": row.get("category", "Other").strip(),
                    "payment_method": row.get("payment_method", "UPI").strip(),
                    "date": dt,
                    "description": row.get("description", "").strip(),
                    "notes": row.get("notes", "").strip(),
                    "is_debit": True,
                })
            except Exception:
                continue
    return records


class ExpenseValidationError(Exception):
    """Raised when an expense payload fails schema validation."""
    pass


class ExpenseManager:
    """Manages expenses persisted in MongoDB, with CSV fallback when offline."""

    def __init__(self):
        self.db = get_db()
        if not self.db.is_connected:
            logger.warning("ExpenseManager: MongoDB offline — using CSV fallback.")

    def _is_online(self) -> bool:
        return self.db.is_connected and getattr(self.db, "expenses", None) is not None

    def _ensure_db(self):
        if not self._is_online():
            raise ConnectionError(
                "MongoDB is offline. Write operations are disabled. "
                "Connect MongoDB to add, edit, or delete transactions."
            )

    def validate_expense_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean transaction fields."""
        amount = data.get("amount")
        try:
            amount = float(amount)
        except (TypeError, ValueError):
            raise ExpenseValidationError("Transaction amount must be a valid positive number.")
        if amount <= 0:
            raise ExpenseValidationError("Transaction amount must be strictly greater than zero.")

        merchant = str(data.get("merchant", "")).strip()
        if not merchant:
            raise ExpenseValidationError("Merchant or Payee name cannot be empty.")

        category = str(data.get("category", "")).strip()
        if not category:
            category = "Other"

        tx_date = data.get("date")
        if isinstance(tx_date, str):
            try:
                tx_date = datetime.fromisoformat(tx_date.replace("Z", "+00:00"))
            except ValueError:
                try:
                    tx_date = datetime.strptime(tx_date, "%Y-%m-%d")
                except ValueError:
                    raise ExpenseValidationError("Date must be in YYYY-MM-DD or ISO format.")
        elif isinstance(tx_date, date) and not isinstance(tx_date, datetime):
            tx_date = datetime.combine(tx_date, datetime.min.time())
        elif not isinstance(tx_date, datetime):
            raise ExpenseValidationError("A valid transaction date is required.")

        payment_method = str(data.get("payment_method", "UPI")).strip() or "UPI"
        description = str(data.get("description", "")).strip()
        notes = str(data.get("notes", "")).strip()

        return {
            "user_id": data.get("user_id", DEFAULT_USER_ID),
            "amount": round(amount, 2),
            "currency": data.get("currency", DEFAULT_CURRENCY),
            "merchant": merchant,
            "category": category,
            "payment_method": payment_method,
            "date": tx_date,
            "description": description,
            "notes": notes,
            "is_debit": bool(data.get("is_debit", True)),
        }

    def add_expense(
        self,
        amount: float,
        merchant: str,
        category: str,
        date_val: Any,
        payment_method: str = "UPI",
        description: str = "",
        notes: str = "",
        is_debit: bool = True,
        user_id: str = DEFAULT_USER_ID,
        currency: str = DEFAULT_CURRENCY,
    ) -> str:
        """Create and persist a new verified transaction in MongoDB."""
        self._ensure_db()
        from bson import ObjectId
        from pymongo import ASCENDING, DESCENDING
        payload = {
            "user_id": user_id,
            "amount": amount,
            "currency": currency,
            "merchant": merchant,
            "category": category,
            "payment_method": payment_method,
            "date": date_val,
            "description": description,
            "notes": notes,
            "is_debit": is_debit,
        }
        clean_data = self.validate_expense_data(payload)
        now = datetime.utcnow()
        clean_data["created_at"] = now
        clean_data["updated_at"] = now
        result = self.db.expenses.insert_one(clean_data)
        return str(result.inserted_id)

    def get_expense(self, expense_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve single transaction by ObjectId."""
        if not self._is_online():
            return None
        from bson import ObjectId
        try:
            obj_id = ObjectId(expense_id)
        except Exception:
            return None
        doc = self.db.expenses.find_one({"_id": obj_id})
        return serialize_doc(doc)

    def update_expense(self, expense_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing transaction record by ObjectId."""
        self._ensure_db()
        from bson import ObjectId
        try:
            obj_id = ObjectId(expense_id)
        except Exception:
            raise ExpenseValidationError("Invalid transaction identifier.")
        existing = self.db.expenses.find_one({"_id": obj_id})
        if not existing:
            return False
        merged = {
            "user_id": updates.get("user_id", existing.get("user_id", DEFAULT_USER_ID)),
            "amount": updates.get("amount", existing.get("amount")),
            "currency": updates.get("currency", existing.get("currency", DEFAULT_CURRENCY)),
            "merchant": updates.get("merchant", existing.get("merchant")),
            "category": updates.get("category", existing.get("category")),
            "payment_method": updates.get("payment_method", existing.get("payment_method")),
            "date": updates.get("date", existing.get("date")),
            "description": updates.get("description", existing.get("description", "")),
            "notes": updates.get("notes", existing.get("notes", "")),
        }
        clean_data = self.validate_expense_data(merged)
        clean_data["updated_at"] = datetime.utcnow()
        res = self.db.expenses.update_one({"_id": obj_id}, {"$set": clean_data})
        return res.modified_count > 0 or res.matched_count > 0

    def delete_expense(self, expense_id: str) -> bool:
        """Delete an expense record."""
        self._ensure_db()
        from bson import ObjectId
        try:
            obj_id = ObjectId(expense_id)
        except Exception:
            return False
        res = self.db.expenses.delete_one({"_id": obj_id})
        return res.deleted_count > 0

    def get_expenses(
        self,
        user_id: str = DEFAULT_USER_ID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        category: Optional[str] = None,
        payment_method: Optional[str] = None,
        search_query: Optional[str] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None,
        sort_by: str = "date",
        sort_descending: bool = True,
        limit: int = 50,
        skip: int = 0,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Query expenses with multiple filters, sorting, and pagination.
        Returns: (list_of_expenses, total_count)
        Falls back to CSV when MongoDB is offline.
        """
        if not self._is_online():
            return self._get_expenses_csv(
                user_id, start_date, end_date, category, payment_method,
                search_query, min_amount, max_amount, sort_by, sort_descending, limit, skip
            )

        from pymongo import ASCENDING, DESCENDING as DESC
        query: Dict[str, Any] = {"user_id": user_id}

        if start_date or end_date:
            date_filter: Dict[str, Any] = {}
            if start_date:
                date_filter["$gte"] = start_date
            if end_date:
                date_filter["$lte"] = end_date
            query["date"] = date_filter

        if category and category != "All":
            query["category"] = category

        if payment_method and payment_method != "All":
            query["payment_method"] = payment_method

        if min_amount is not None or max_amount is not None:
            amount_filter: Dict[str, Any] = {}
            if min_amount is not None:
                amount_filter["$gte"] = float(min_amount)
            if max_amount is not None:
                amount_filter["$lte"] = float(max_amount)
            query["amount"] = amount_filter

        if search_query and search_query.strip():
            import re
            escaped_sq = re.escape(search_query.strip())
            query["$or"] = [
                {"merchant": {"$regex": escaped_sq, "$options": "i"}},
                {"description": {"$regex": escaped_sq, "$options": "i"}},
                {"notes": {"$regex": escaped_sq, "$options": "i"}},
            ]

        total_count = self.db.expenses.count_documents(query)
        sort_dir = DESC if sort_descending else ASCENDING
        cursor = self.db.expenses.find(query).sort(sort_by, sort_dir).skip(skip).limit(limit)
        records = [serialize_doc(doc) for doc in cursor]
        return records, total_count

    def _get_expenses_csv(
        self,
        user_id, start_date, end_date, category, payment_method,
        search_query, min_amount, max_amount, sort_by, sort_descending, limit, skip
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Filter and paginate expenses from CSV fallback."""
        all_records = _load_csv_expenses(user_id)

        filtered = []
        for r in all_records:
            dt = r["date"]
            if start_date and dt < start_date:
                continue
            if end_date and dt > end_date:
                continue
            if category and category != "All" and r["category"] != category:
                continue
            if payment_method and payment_method != "All" and r["payment_method"] != payment_method:
                continue
            if min_amount is not None and r["amount"] < min_amount:
                continue
            if max_amount is not None and r["amount"] > max_amount:
                continue
            if search_query and search_query.strip():
                sq = search_query.strip().lower()
                if not any(sq in str(r.get(f, "")).lower() for f in ("merchant", "description", "notes")):
                    continue
            filtered.append(r)

        reverse = sort_descending
        filtered.sort(key=lambda x: x.get(sort_by, x.get("date")), reverse=reverse)
        total_count = len(filtered)
        page = filtered[skip: skip + limit]
        return page, total_count

    def get_all_expenses_for_user(self, user_id: str = DEFAULT_USER_ID) -> List[Dict[str, Any]]:
        """Fetch all expenses chronologically for analytics and model training."""
        if not self._is_online():
            records = _load_csv_expenses(user_id)
            records.sort(key=lambda x: x["date"])
            return records

        from pymongo import ASCENDING
        cursor = self.db.expenses.find({"user_id": user_id}).sort("date", ASCENDING)
        return [serialize_doc(doc) for doc in cursor]

    def export_to_csv(self, expenses: List[Dict[str, Any]]) -> str:
        """Export list of serialized expenses to CSV format."""
        output = io.StringIO()
        fieldnames = ["id", "date", "merchant", "category", "amount", "currency",
                      "payment_method", "description", "notes"]
        writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for exp in expenses:
            row = dict(exp)
            if isinstance(row.get("date"), datetime):
                row["date"] = row["date"].strftime("%Y-%m-%d")
            writer.writerow(row)
        return output.getvalue()

    def import_from_csv(self, csv_data: str, user_id: str = DEFAULT_USER_ID) -> Dict[str, Any]:
        """
        Import transactions from CSV string.
        Validates row-by-row and provides comprehensive diagnostic report.
        """
        self._ensure_db()
        f = io.StringIO(csv_data.strip())
        reader = csv.DictReader(f)

        imported_count = 0
        skipped_count = 0
        errors: List[Dict[str, Any]] = []

        for row_idx, row in enumerate(reader, start=1):
            try:
                amount_str = row.get("amount") or row.get("Amount")
                merchant = row.get("merchant") or row.get("Merchant") or row.get("payee") or row.get("Payee")
                category = row.get("category") or row.get("Category") or "Other"
                date_str = row.get("date") or row.get("Date") or row.get("transaction_date")
                payment_method = (
                    row.get("payment_method") or row.get("Payment Method") or row.get("channel") or "UPI"
                )
                description = row.get("description") or row.get("Description") or ""
                notes = row.get("notes") or row.get("Notes") or ""

                if not date_str:
                    raise ExpenseValidationError("Missing date column")

                clean_payload = self.validate_expense_data({
                    "user_id": user_id,
                    "amount": amount_str,
                    "currency": DEFAULT_CURRENCY,
                    "merchant": merchant,
                    "category": category,
                    "payment_method": payment_method,
                    "date": date_str,
                    "description": description,
                    "notes": notes,
                })
                clean_payload["created_at"] = datetime.utcnow()
                clean_payload["updated_at"] = datetime.utcnow()
                self.db.expenses.insert_one(clean_payload)
                imported_count += 1
            except Exception as e:
                skipped_count += 1
                errors.append({"row": row_idx, "error": str(e), "data": row})

        return {
            "total_rows": imported_count + skipped_count,
            "imported": imported_count,
            "skipped": skipped_count,
            "errors": errors[:20],
        }

    def import_from_json(self, json_data: Any, user_id: str = DEFAULT_USER_ID) -> Dict[str, Any]:
        """
        Import transactions from JSON string, bytes, or parsed list/dict.
        Validates item-by-item and records imported count and errors.
        """
        self._ensure_db()
        if isinstance(json_data, (str, bytes)):
            try:
                data = json.loads(json_data)
            except Exception as e:
                return {
                    "total_rows": 0,
                    "imported": 0,
                    "skipped": 0,
                    "errors": [{"error": f"Invalid JSON format: {str(e)}"}],
                }
        else:
            data = json_data

        if isinstance(data, dict):
            # Extract array if nested under common container keys
            for key in ["expenses", "transactions", "data", "records", "items"]:
                if key in data and isinstance(data[key], list):
                    data = data[key]
                    break
            else:
                data = [data]

        if not isinstance(data, list):
            return {
                "total_rows": 0,
                "imported": 0,
                "skipped": 0,
                "errors": [{"error": "Expected a JSON array of transaction objects."}],
            }

        imported_count = 0
        skipped_count = 0
        errors: List[Dict[str, Any]] = []

        for idx, item in enumerate(data, start=1):
            if not isinstance(item, dict):
                skipped_count += 1
                errors.append({"row": idx, "error": "Item is not a valid JSON object", "data": item})
                continue
            try:
                amount_str = item.get("amount") or item.get("Amount")
                merchant = item.get("merchant") or item.get("Merchant") or item.get("payee") or item.get("Payee")
                category = item.get("category") or item.get("Category") or "Other"
                date_str = item.get("date") or item.get("Date") or item.get("transaction_date")
                payment_method = (
                    item.get("payment_method") or item.get("Payment Method") or item.get("channel") or "UPI"
                )
                description = item.get("description") or item.get("Description") or ""
                notes = item.get("notes") or item.get("Notes") or ""

                if not date_str:
                    raise ExpenseValidationError("Missing required 'date' field")

                clean_payload = self.validate_expense_data({
                    "user_id": user_id,
                    "amount": amount_str,
                    "currency": DEFAULT_CURRENCY,
                    "merchant": merchant,
                    "category": category,
                    "payment_method": payment_method,
                    "date": date_str,
                    "description": description,
                    "notes": notes,
                })
                clean_payload["created_at"] = datetime.utcnow()
                clean_payload["updated_at"] = datetime.utcnow()
                self.db.expenses.insert_one(clean_payload)
                imported_count += 1
            except Exception as e:
                skipped_count += 1
                errors.append({"row": idx, "error": str(e), "data": item})

        return {
            "total_rows": imported_count + skipped_count,
            "imported": imported_count,
            "skipped": skipped_count,
            "errors": errors[:20],
        }
