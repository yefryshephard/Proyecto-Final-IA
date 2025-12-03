"""
Repository for analysis history persistence using SQLite.
Follows the Repository pattern for data access abstraction.
"""

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import Generator, Optional

from src.config import get_settings


class HistoryRepository:
    """Repository for managing analysis history in SQLite database."""

    def __init__(self, db_path: Optional[str] = None):
        """Initialize repository with database path."""
        self.db_path = db_path or get_settings().db_path
        self._init_db()

    def _init_db(self):
        """Initialize database schema."""
        with self._get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS analyses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    entrada TEXT,
                    titulo TEXT,
                    score INTEGER,
                    semaforo TEXT,
                    full_analysis TEXT,
                    sources TEXT,
                    url TEXT,
                    domain TEXT
                )
                """
            )
            conn.commit()

    @contextmanager
    def _get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    def save(
        self,
        timestamp: str,
        entrada: str,
        titulo: str,
        score: int,
        semaforo: str,
        full_analysis: str = "",
        sources: str = "",
        url: str = "",
        domain: str = "",
    ) -> int:
        """
        Save an analysis result to the database.

        Returns:
            int: The ID of the inserted record.
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO analyses 
                (timestamp, entrada, titulo, score, semaforo, full_analysis, sources, url, domain)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    timestamp,
                    entrada,
                    titulo,
                    score,
                    semaforo,
                    full_analysis,
                    sources,
                    url,
                    domain,
                ),
            )
            conn.commit()
            return cursor.lastrowid or 0

    def get_recent(self, limit: int = 10) -> list[list]:
        """
        Get the most recent analyses.

        Args:
            limit: Maximum number of records to return.

        Returns:
            List of [timestamp, titulo, score, semaforo] lists.
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT timestamp, titulo, score, semaforo 
                FROM analyses 
                ORDER BY id DESC 
                LIMIT ?
                """,
                (limit,),
            )
            return [list(row) for row in cursor.fetchall()]

    def get_all(self, limit: int = 1000) -> list[dict]:
        """
        Get all analyses with full details.

        Args:
            limit: Maximum number of records to return.

        Returns:
            List of analysis dictionaries.
        """
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """
                SELECT id, timestamp, entrada, titulo, score, semaforo, 
                       full_analysis, sources, url, domain
                FROM analyses 
                ORDER BY id DESC 
                LIMIT ?
                """,
                (limit,),
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_by_id(self, analysis_id: int) -> Optional[dict]:
        """
        Get a specific analysis by ID.

        Args:
            analysis_id: The ID of the analysis to retrieve.

        Returns:
            Analysis dictionary or None if not found.
        """
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM analyses WHERE id = ?", (analysis_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def search(self, query: str, limit: int = 50) -> list[dict]:
        """
        Search analyses by title or content.

        Args:
            query: Search query string.
            limit: Maximum number of results.

        Returns:
            List of matching analysis dictionaries.
        """
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """
                SELECT id, timestamp, entrada, titulo, score, semaforo
                FROM analyses 
                WHERE titulo LIKE ? OR entrada LIKE ?
                ORDER BY id DESC 
                LIMIT ?
                """,
                (f"%{query}%", f"%{query}%", limit),
            )
            return [dict(row) for row in cursor.fetchall()]

    def clear_all(self) -> int:
        """
        Clear all analysis history.

        Returns:
            Number of deleted records.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("DELETE FROM analyses")
            conn.commit()
            return cursor.rowcount

    def get_statistics(self) -> dict:
        """
        Get statistics about stored analyses.

        Returns:
            Dictionary with statistics.
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT 
                    COUNT(*) as total,
                    AVG(score) as avg_score,
                    MIN(score) as min_score,
                    MAX(score) as max_score,
                    SUM(CASE WHEN score >= 70 THEN 1 ELSE 0 END) as reliable_count,
                    SUM(CASE WHEN score >= 40 AND score < 70 THEN 1 ELSE 0 END) as suspicious_count,
                    SUM(CASE WHEN score < 40 THEN 1 ELSE 0 END) as fake_count
                FROM analyses
                """
            )
            row = cursor.fetchone()
            if row:
                return {
                    "total": row[0] or 0,
                    "avg_score": round(row[1] or 0, 1),
                    "min_score": row[2] or 0,
                    "max_score": row[3] or 0,
                    "reliable_count": row[4] or 0,
                    "suspicious_count": row[5] or 0,
                    "fake_count": row[6] or 0,
                }
            return {}

    def export_to_rows(self, limit: int = 1000) -> list[list]:
        """
        Export analyses as rows for CSV export.

        Returns:
            List of [timestamp, titulo, score, semaforo] lists.
        """
        return self.get_recent(limit)
