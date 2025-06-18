"""
Database operations for storing and retrieving recordings and transcriptions
"""

import os
import sqlite3
import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional


class Database:
    def __init__(self, db_path: str):
        # Expand the path if it contains ~
        db_path = os.path.expanduser(db_path)

        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        self.db_path = db_path
        self.conn = None
        self.initialize()

    def get_connection(self):
        """Get a database connection"""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
        return self.conn

    def initialize(self):
        """Initialize the database schema if it doesn't exist"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Create recordings table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS recordings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            audio_path TEXT NOT NULL,
            transcription TEXT,
            model_used TEXT,
            status TEXT DEFAULT 'done',
            error_message TEXT
        )
        """)

        # Create FTS virtual table for searching transcriptions
        cursor.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS recordings_fts USING fts5(
            transcription, 
            content='recordings', 
            content_rowid='id'
        )
        """)

        # Create trigger to keep FTS index updated
        cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS recordings_ai AFTER INSERT ON recordings
        BEGIN
            INSERT INTO recordings_fts(rowid, transcription) 
            VALUES (new.id, new.transcription);
        END
        """)

        cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS recordings_au AFTER UPDATE ON recordings
        BEGIN
            INSERT INTO recordings_fts(recordings_fts, rowid, transcription) 
            VALUES('delete', old.id, old.transcription);
            INSERT INTO recordings_fts(rowid, transcription) 
            VALUES (new.id, new.transcription);
        END
        """)

        cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS recordings_ad AFTER DELETE ON recordings
        BEGIN
            INSERT INTO recordings_fts(recordings_fts, rowid, transcription) 
            VALUES('delete', old.id, old.transcription);
        END
        """)

        conn.commit()

    def add_recording(
        self,
        audio_path: str,
        transcription: Optional[str] = None,
        model_used: Optional[str] = None,
        status: str = "done",
        error_message: Optional[str] = None,
    ) -> int:
        """Add a new recording to the database"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
        INSERT INTO recordings (audio_path, transcription, model_used, status, error_message)
        VALUES (?, ?, ?, ?, ?)
        """,
            (audio_path, transcription, model_used, status, error_message),
        )

        conn.commit()
        return cursor.lastrowid

    def update_recording(
        self,
        id: int,
        transcription: Optional[str] = None,
        model_used: Optional[str] = None,
        status: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> bool:
        """Update an existing recording's transcription or status"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Fetch current values
        cursor.execute("SELECT * FROM recordings WHERE id = ?", (id,))
        record = cursor.fetchone()

        if not record:
            return False

        # Use current values if new ones not provided
        transcription = (
            transcription if transcription is not None else record["transcription"]
        )
        model_used = model_used if model_used is not None else record["model_used"]
        status = status if status is not None else record["status"]
        error_message = (
            error_message if error_message is not None else record["error_message"]
        )

        cursor.execute(
            """
        UPDATE recordings 
        SET transcription = ?, model_used = ?, status = ?, error_message = ?
        WHERE id = ?
        """,
            (transcription, model_used, status, error_message, id),
        )

        conn.commit()
        return True

    def get_recent_recordings(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the most recent recordings"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
        SELECT * FROM recordings 
        ORDER BY created_at DESC 
        LIMIT ?
        """,
            (limit,),
        )

        results = cursor.fetchall()
        return [dict(row) for row in results]

    def get_recording(self, id: int) -> Optional[Dict[str, Any]]:
        """Get a specific recording by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM recordings WHERE id = ?", (id,))
        result = cursor.fetchone()

        return dict(result) if result else None

    def search_transcriptions(
        self, query: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search transcriptions using FTS"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
        SELECT r.* FROM recordings r
        JOIN recordings_fts fts ON r.id = fts.rowid
        WHERE recordings_fts MATCH ?
        ORDER BY r.created_at DESC
        LIMIT ?
        """,
            (query, limit),
        )

        results = cursor.fetchall()
        return [dict(row) for row in results]

    def delete_recording(self, id: int) -> bool:
        """Delete a recording from the database"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM recordings WHERE id = ?", (id,))
        conn.commit()

        return cursor.rowcount > 0

    def cleanup_old_recordings(self, keep_last_n: int = 10) -> List[str]:
        """Remove old recordings beyond the keep_last_n limit, returns paths to deleted audio files"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Get IDs to keep
        cursor.execute(
            """
        SELECT id FROM recordings
        ORDER BY created_at DESC
        LIMIT ?
        """,
            (keep_last_n,),
        )

        keep_ids = [row["id"] for row in cursor.fetchall()]

        if not keep_ids:
            return []

        # Get paths of files to delete
        cursor.execute(
            """
        SELECT id, audio_path FROM recordings
        WHERE id NOT IN ({})
        """.format(",".join(["?"] * len(keep_ids))),
            keep_ids,
        )

        delete_records = cursor.fetchall()
        deleted_paths = [dict(row)["audio_path"] for row in delete_records]
        delete_ids = [dict(row)["id"] for row in delete_records]

        # Delete records
        if delete_ids:
            id_placeholders = ",".join(["?"] * len(delete_ids))
            cursor.execute(
                f"DELETE FROM recordings WHERE id IN ({id_placeholders})", delete_ids
            )
            conn.commit()

        return deleted_paths

    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
