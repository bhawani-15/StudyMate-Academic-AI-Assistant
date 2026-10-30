"""SQLite database layer for the Academic RAG Assistant.

Manages persistent models and CRUD operations for:
- users
- documents
- conversations
- messages
"""

from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
import json
import sqlite3
import uuid
from typing import Any, Dict, List, Optional


DEFAULT_DB_PATH = Path(__file__).resolve().parent / "academic_assistant.db"


@contextmanager
def get_db(db_path: Optional[Path] = None):
    """Context manager for SQLite database connections.
    
    Enforces foreign key constraints and provides dict-like row access.
    """
    path = str(db_path or DEFAULT_DB_PATH)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db(db_path: Optional[Path] = None) -> None:
    """Initialize database tables and indexes."""
    with get_db(db_path) as conn:
        conn.executescript(
            """
            -- 1. Users Table
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            -- 2. Documents Table (Tracks user ownership and chunk metadata)
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                file_name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                page_count INTEGER NOT NULL,
                chunk_count INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (id, user_id),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            -- 3. Conversations Table
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                title TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            -- 4. Messages Table
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
                content TEXT NOT NULL,
                sources_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
            );

            -- Indexes for fast queries
            CREATE INDEX IF NOT EXISTS idx_documents_user ON documents(user_id);
            CREATE INDEX IF NOT EXISTS idx_conversations_user ON conversations(user_id, updated_at DESC);
            CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id, created_at ASC);
            """
        )

        # Migration check: Ensure documents table has composite primary key
        cursor = conn.cursor()
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='documents'")
        tbl_row = cursor.fetchone()
        if tbl_row and "PRIMARY KEY (id, user_id)" not in tbl_row[0]:
            cursor.execute("ALTER TABLE documents RENAME TO documents_old")
            cursor.execute(
                """
                CREATE TABLE documents (
                    id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    file_name TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
                    page_count INTEGER NOT NULL,
                    chunk_count INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (id, user_id),
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                );
                """
            )
            cursor.execute(
                """
                INSERT OR IGNORE INTO documents (id, user_id, file_name, file_path, file_size, page_count, chunk_count, created_at)
                SELECT id, user_id, file_name, file_path, file_size, page_count, chunk_count, created_at FROM documents_old;
                """
            )
            cursor.execute("DROP TABLE documents_old")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_user ON documents(user_id);")


# ============================================================================
# Users CRUD
# ============================================================================

def create_user(
    username: str,
    email: str,
    password_hash: str,
    user_id: Optional[str] = None,
    db_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """Create a new user."""
    uid = user_id or str(uuid.uuid4())
    username_clean = username.strip()
    email_clean = email.strip().lower()

    with get_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO users (id, username, email, password_hash)
            VALUES (?, ?, ?, ?)
            """,
            (uid, username_clean, email_clean, password_hash),
        )

    return get_user_by_id(uid, db_path=db_path)  # type: ignore


def get_user_by_id(user_id: str, db_path: Optional[Path] = None) -> Optional[Dict[str, Any]]:
    """Retrieve a user by their unique ID."""
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def get_user_by_username_or_email(
    identifier: str, db_path: Optional[Path] = None
) -> Optional[Dict[str, Any]]:
    """Retrieve a user by either username or email (case-insensitive for email)."""
    cleaned = identifier.strip()
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM users 
            WHERE username = ? OR LOWER(email) = LOWER(?)
            LIMIT 1
            """,
            (cleaned, cleaned),
        )
        row = cursor.fetchone()
        return dict(row) if row else None


def get_user_by_email(email: str, db_path: Optional[Path] = None) -> Optional[Dict[str, Any]]:
    """Retrieve a user by their email address."""
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE LOWER(email) = LOWER(?)",
            (email.strip(),),
        )
        row = cursor.fetchone()
        return dict(row) if row else None


def delete_user(user_id: str, db_path: Optional[Path] = None) -> bool:
    """Delete a user. Cascade deletes all related conversations, messages, and documents."""
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        return cursor.rowcount > 0


# ============================================================================
# Documents CRUD
# ============================================================================

def create_document(
    doc_id: str,
    user_id: str,
    file_name: str,
    file_path: str,
    file_size: int,
    page_count: int,
    chunk_count: int,
    db_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """Record metadata for an uploaded and processed PDF document."""
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO documents (
                id, user_id, file_name, file_path, file_size, page_count, chunk_count
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id, user_id) DO UPDATE SET
                file_name = excluded.file_name,
                file_path = excluded.file_path,
                file_size = excluded.file_size,
                page_count = excluded.page_count,
                chunk_count = excluded.chunk_count
            """,
            (doc_id, user_id, file_name, file_path, file_size, page_count, chunk_count),
        )

    return get_document_by_id(doc_id, user_id=user_id, db_path=db_path)  # type: ignore


def get_document_by_id(
    doc_id: str, user_id: Optional[str] = None, db_path: Optional[Path] = None
) -> Optional[Dict[str, Any]]:
    """Retrieve a document record by its hash ID (optionally filtered by user_id)."""
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        if user_id:
            cursor.execute("SELECT * FROM documents WHERE id = ? AND user_id = ?", (doc_id, user_id))
        else:
            cursor.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def get_documents_by_user(user_id: str, db_path: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Retrieve all documents belonging to a user, ordered by upload date."""
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM documents 
            WHERE user_id = ? 
            ORDER BY created_at DESC
            """,
            (user_id,),
        )
        return [dict(row) for row in cursor.fetchall()]


def delete_document(doc_id: str, user_id: Optional[str] = None, db_path: Optional[Path] = None) -> bool:
    """Delete a document record from the database.
    
    If user_id is provided, ensures ownership before deletion.
    """
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        if user_id:
            cursor.execute(
                "DELETE FROM documents WHERE id = ? AND user_id = ?",
                (doc_id, user_id),
            )
        else:
            cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
        return cursor.rowcount > 0


# ============================================================================
# Conversations CRUD
# ============================================================================

def create_conversation(
    user_id: str,
    title: str = "New Chat",
    conversation_id: Optional[str] = None,
    db_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """Create a new chat conversation for a user."""
    cid = conversation_id or str(uuid.uuid4())
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO conversations (id, user_id, title)
            VALUES (?, ?, ?)
            """,
            (cid, user_id, title.strip()),
        )

    return get_conversation_by_id(cid, db_path=db_path)  # type: ignore


def get_conversation_by_id(
    conversation_id: str, db_path: Optional[Path] = None
) -> Optional[Dict[str, Any]]:
    """Retrieve conversation details by ID."""
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM conversations WHERE id = ?", (conversation_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def get_conversations_by_user(
    user_id: str, db_path: Optional[Path] = None
) -> List[Dict[str, Any]]:
    """Retrieve all conversations for a user, sorted by most recently updated."""
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM conversations 
            WHERE user_id = ? 
            ORDER BY updated_at DESC, rowid DESC
            """,
            (user_id,),
        )
        return [dict(row) for row in cursor.fetchall()]


def update_conversation_title(
    conversation_id: str,
    title: str,
    user_id: Optional[str] = None,
    db_path: Optional[Path] = None,
) -> bool:
    """Update conversation title and refresh updated_at timestamp."""
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        if user_id:
            cursor.execute(
                """
                UPDATE conversations 
                SET title = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ? AND user_id = ?
                """,
                (title.strip(), conversation_id, user_id),
            )
        else:
            cursor.execute(
                """
                UPDATE conversations 
                SET title = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (title.strip(), conversation_id),
            )
        return cursor.rowcount > 0


def touch_conversation(conversation_id: str, db_path: Optional[Path] = None) -> bool:
    """Update conversation's updated_at timestamp to current time."""
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE conversations 
            SET updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
            """,
            (conversation_id,),
        )
        return cursor.rowcount > 0


def delete_conversation(
    conversation_id: str,
    user_id: Optional[str] = None,
    db_path: Optional[Path] = None,
) -> bool:
    """Delete a conversation. Cascade deletes all its associated messages."""
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        if user_id:
            cursor.execute(
                "DELETE FROM conversations WHERE id = ? AND user_id = ?",
                (conversation_id, user_id),
            )
        else:
            cursor.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))
        return cursor.rowcount > 0


# ============================================================================
# Messages CRUD
# ============================================================================

def create_message(
    conversation_id: str,
    role: str,
    content: str,
    sources: Optional[List[Dict[str, Any]]] = None,
    message_id: Optional[str] = None,
    db_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """Create a new message in a conversation and update the conversation timestamp."""
    mid = message_id or str(uuid.uuid4())
    sources_json = json.dumps(sources) if sources is not None else None

    with get_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO messages (id, conversation_id, role, content, sources_json)
            VALUES (?, ?, ?, ?, ?)
            """,
            (mid, conversation_id, role, content, sources_json),
        )
        # Also touch the parent conversation
        cursor.execute(
            """
            UPDATE conversations 
            SET updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
            """,
            (conversation_id,),
        )

    return get_message_by_id(mid, db_path=db_path)  # type: ignore


def get_message_by_id(message_id: str, db_path: Optional[Path] = None) -> Optional[Dict[str, Any]]:
    """Retrieve a single message by ID with deserialized sources."""
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM messages WHERE id = ?", (message_id,))
        row = cursor.fetchone()
        if not row:
            return None

        data = dict(row)
        if data.get("sources_json"):
            try:
                data["sources"] = json.loads(data["sources_json"])
            except Exception:
                data["sources"] = []
        else:
            data["sources"] = []
        return data


def get_messages_by_conversation(
    conversation_id: str, db_path: Optional[Path] = None
) -> List[Dict[str, Any]]:
    """Retrieve all messages in a conversation in chronological order."""
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM messages 
            WHERE conversation_id = ? 
            ORDER BY created_at ASC
            """,
            (conversation_id,),
        )
        results = []
        for row in cursor.fetchall():
            data = dict(row)
            if data.get("sources_json"):
                try:
                    data["sources"] = json.loads(data["sources_json"])
                except Exception:
                    data["sources"] = []
            else:
                data["sources"] = []
            results.append(data)
        return results


def delete_messages_by_conversation(
    conversation_id: str, db_path: Optional[Path] = None
) -> int:
    """Clear all messages from a conversation without deleting the conversation itself."""
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM messages WHERE conversation_id = ?", (conversation_id,))
        return cursor.rowcount
