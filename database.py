"""
Little Ledger - MongoDB Database Connection & Index Management
Provides resilient PyMongo client management, health check diagnostics, and index initialization.
"""

import logging
from typing import Optional, Dict, Any, Tuple
from datetime import datetime
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from bson import ObjectId

from config import MONGODB_URI, MONGODB_DATABASE

logger = logging.getLogger("little_ledger.database")

class Database:
    """Singleton MongoDB Database wrapper using PyMongo."""
    _instance: Optional["Database"] = None
    _client: Optional[MongoClient] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance._init_connection()
        return cls._instance

    def _init_connection(self):
        try:
            self._client = MongoClient(
                MONGODB_URI,
                serverSelectionTimeoutMS=4000,
                connectTimeoutMS=4000,
                socketTimeoutMS=5000,
            )
            # Verify connectivity
            self._client.admin.command("ping")
            self.db = self._client[MONGODB_DATABASE]
            self.expenses = self.db["expenses"]
            self.budgets = self.db["budgets"]
            self.predictions = self.db["predictions"]
            self.model_evaluations = self.db["model_evaluations"]
            self.settings = self.db["settings"]
            self.is_connected = True
            self.error_message = ""
            self._ensure_indexes()
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            self.is_connected = False
            self.error_message = f"Could not connect to MongoDB at {MONGODB_URI}: {str(e)}"
            self.db = None
            logger.error(self.error_message)
        except Exception as e:
            self.is_connected = False
            self.error_message = f"Database initialization error: {str(e)}"
            self.db = None
            logger.error(self.error_message)

    def _ensure_indexes(self):
        """Build essential performance and uniqueness indexes."""
        if not self.is_connected or self.db is None:
            return

        try:
            # Expenses collection indexes
            self.expenses.create_index([("user_id", ASCENDING), ("date", DESCENDING)])
            self.expenses.create_index([("user_id", ASCENDING), ("category", ASCENDING)])
            self.expenses.create_index([("user_id", ASCENDING), ("merchant", ASCENDING)])

            # Budgets collection compound unique index (one budget per user/year/month/category)
            self.budgets.create_index(
                [
                    ("user_id", ASCENDING),
                    ("year", ASCENDING),
                    ("month", ASCENDING),
                    ("category", ASCENDING),
                ],
                unique=True,
            )

            # Predictions collection index
            self.predictions.create_index([("user_id", ASCENDING), ("created_at", DESCENDING)])

            # Model evaluations index
            self.model_evaluations.create_index(
                [("model_name", ASCENDING), ("evaluation_date", DESCENDING)]
            )

            # Settings collection index (unique per user)
            self.settings.create_index([("user_id", ASCENDING)], unique=True)
        except Exception as e:
            logger.warning(f"Error creating indexes: {e}")

    def get_client(self) -> Optional[MongoClient]:
        return self._client

    def health_check(self) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Check database connection and return stats.
        Returns: (is_healthy, message, stats_dict)
        """
        if not self.is_connected or self._client is None or self.db is None:
            # Attempt reconnect
            self._init_connection()
            if not self.is_connected:
                return False, self.error_message, {}

        try:
            ping_res = self._client.admin.command("ping")
            server_info = self._client.server_info()
            
            stats = {
                "version": server_info.get("version", "Unknown"),
                "db_name": MONGODB_DATABASE,
                "expenses_count": self.expenses.count_documents({}),
                "budgets_count": self.budgets.count_documents({}),
                "predictions_count": self.predictions.count_documents({}),
                "evaluations_count": self.model_evaluations.count_documents({}),
            }
            return True, "MongoDB connected and healthy", stats
        except Exception as e:
            self.is_connected = False
            self.error_message = str(e)
            return False, f"Health check failed: {str(e)}", {}


def serialize_doc(doc: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Convert MongoDB Document ObjectId and datetimes into serializable primitives."""
    if doc is None:
        return None
    res = dict(doc)
    if "_id" in res:
        res["id"] = str(res["_id"])
        res["_id"] = str(res["_id"])
    for k, v in res.items():
        if isinstance(v, datetime):
            res[k] = v.isoformat()
        elif isinstance(v, ObjectId):
            res[k] = str(v)
    return res


def get_db() -> Database:
    """Return database instance."""
    return Database()
