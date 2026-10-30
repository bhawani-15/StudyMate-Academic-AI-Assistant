"""Automated test suite to verify database creation and CRUD operations."""

import os
from pathlib import Path
import sqlite3
import tempfile
import unittest

from database import (
    init_db,
    create_user,
    get_user_by_id,
    get_user_by_username_or_email,
    get_user_by_email,
    delete_user,
    create_document,
    get_document_by_id,
    get_documents_by_user,
    delete_document,
    create_conversation,
    get_conversation_by_id,
    get_conversations_by_user,
    update_conversation_title,
    touch_conversation,
    delete_conversation,
    create_message,
    get_message_by_id,
    get_messages_by_conversation,
    delete_messages_by_conversation,
)


class TestDatabaseCRUD(unittest.TestCase):
    def setUp(self):
        # Use an isolated temporary database file for each test
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_assistant.db"
        init_db(self.db_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_database_initialization(self):
        """Verify all expected tables and indexes exist."""
        from database import get_db
        with get_db(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
            )
            tables = {row[0] for row in cursor.fetchall()}
            expected_tables = {"users", "documents", "conversations", "messages"}
            self.assertTrue(expected_tables.issubset(tables))

    def test_user_crud(self):
        """Verify user creation, lookup, and unique constraints."""
        user = create_user(
            username="bhawani",
            email="bhawani@example.com",
            password_hash="fake_bcrypt_hash_123",
            db_path=self.db_path,
        )
        self.assertIsNotNone(user)
        self.assertEqual(user["username"], "bhawani")
        self.assertEqual(user["email"], "bhawani@example.com")

        # Lookup by ID
        by_id = get_user_by_id(user["id"], db_path=self.db_path)
        self.assertEqual(by_id["username"], "bhawani")

        # Lookup by Username
        by_user = get_user_by_username_or_email("bhawani", db_path=self.db_path)
        self.assertEqual(by_user["id"], user["id"])

        # Lookup by Email (case insensitive)
        by_email = get_user_by_username_or_email("BHAWANI@example.com", db_path=self.db_path)
        self.assertEqual(by_email["id"], user["id"])

        # Duplicate username should raise IntegrityError
        with self.assertRaises(sqlite3.IntegrityError):
            create_user(
                username="bhawani",
                email="another@example.com",
                password_hash="hash",
                db_path=self.db_path,
            )

        # Duplicate email should raise IntegrityError
        with self.assertRaises(sqlite3.IntegrityError):
            create_user(
                username="another_user",
                email="bhawani@example.com",
                password_hash="hash",
                db_path=self.db_path,
            )

    def test_document_crud(self):
        """Verify document creation, listing, upsert, and deletion."""
        user = create_user(
            username="student1",
            email="student1@example.com",
            password_hash="hash",
            db_path=self.db_path,
        )

        doc = create_document(
            doc_id="a1b2c3d4e5f67890",
            user_id=user["id"],
            file_name="QUANTUM MECHANICS.pdf",
            file_path="Data/QUANTUM MECHANICS.pdf",
            file_size=121574,
            page_count=8,
            chunk_count=21,
            db_path=self.db_path,
        )
        self.assertIsNotNone(doc)
        self.assertEqual(doc["file_name"], "QUANTUM MECHANICS.pdf")
        self.assertEqual(doc["chunk_count"], 21)

        # Lookup by ID
        found_doc = get_document_by_id("a1b2c3d4e5f67890", db_path=self.db_path)
        self.assertEqual(found_doc["file_size"], 121574)

        # User documents list
        user_docs = get_documents_by_user(user["id"], db_path=self.db_path)
        self.assertEqual(len(user_docs), 1)
        self.assertEqual(user_docs[0]["id"], "a1b2c3d4e5f67890")

        # Document upsert updates chunk_count
        updated_doc = create_document(
            doc_id="a1b2c3d4e5f67890",
            user_id=user["id"],
            file_name="QUANTUM MECHANICS.pdf",
            file_path="Data/QUANTUM MECHANICS.pdf",
            file_size=121574,
            page_count=8,
            chunk_count=25,
            db_path=self.db_path,
        )
        self.assertEqual(updated_doc["chunk_count"], 25)

        # Delete document
        deleted = delete_document("a1b2c3d4e5f67890", user_id=user["id"], db_path=self.db_path)
        self.assertTrue(deleted)
        self.assertIsNone(get_document_by_id("a1b2c3d4e5f67890", db_path=self.db_path))

    def test_conversation_and_messages_crud(self):
        """Verify conversations, message storage, JSON sources, and ordering."""
        user = create_user(
            username="student2",
            email="student2@example.com",
            password_hash="hash",
            db_path=self.db_path,
        )

        # Create conversation
        convo = create_conversation(
            user_id=user["id"],
            title="Quantum Physics Chat",
            db_path=self.db_path,
        )
        self.assertEqual(convo["title"], "Quantum Physics Chat")

        # Add user message
        msg1 = create_message(
            conversation_id=convo["id"],
            role="user",
            content="What is the uncertainty principle?",
            db_path=self.db_path,
        )
        self.assertEqual(msg1["content"], "What is the uncertainty principle?")

        # Add assistant message with sources
        mock_sources = [
            {
                "page_content": "Delta x * Delta p >= hbar / 2",
                "metadata": {"source": "Data/QUANTUM MECHANICS.pdf", "page": 1},
            }
        ]
        msg2 = create_message(
            conversation_id=convo["id"],
            role="assistant",
            content="It states position and momentum cannot be known simultaneously.",
            sources=mock_sources,
            db_path=self.db_path,
        )

        # Retrieve messages for conversation
        messages = get_messages_by_conversation(convo["id"], db_path=self.db_path)
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]["role"], "user")
        self.assertEqual(messages[1]["role"], "assistant")
        self.assertEqual(len(messages[1]["sources"]), 1)
        self.assertEqual(messages[1]["sources"][0]["metadata"]["page"], 1)

        # Update title
        update_conversation_title(convo["id"], "Heisenberg Principles", db_path=self.db_path)
        updated_convo = get_conversation_by_id(convo["id"], db_path=self.db_path)
        self.assertEqual(updated_convo["title"], "Heisenberg Principles")

        # Clear messages only
        count = delete_messages_by_conversation(convo["id"], db_path=self.db_path)
        self.assertEqual(count, 2)
        self.assertEqual(len(get_messages_by_conversation(convo["id"], db_path=self.db_path)), 0)

    def test_cascade_deletions(self):
        """Verify foreign key cascading deletes children properly."""
        user = create_user(
            username="student3",
            email="student3@example.com",
            password_hash="hash",
            db_path=self.db_path,
        )

        convo = create_conversation(user_id=user["id"], title="Test Convo", db_path=self.db_path)
        create_message(conversation_id=convo["id"], role="user", content="Hi", db_path=self.db_path)

        create_document(
            doc_id="doc123456789012",
            user_id=user["id"],
            file_name="OOPs.pdf",
            file_path="Data/OOPs.pdf",
            file_size=1000,
            page_count=5,
            chunk_count=10,
            db_path=self.db_path,
        )

        # Deleting conversation should cascade delete its messages
        delete_conversation(convo["id"], db_path=self.db_path)
        self.assertIsNone(get_conversation_by_id(convo["id"], db_path=self.db_path))
        self.assertEqual(len(get_messages_by_conversation(convo["id"], db_path=self.db_path)), 0)

        # Re-create convo and delete user -> should delete all convos, messages, docs
        convo2 = create_conversation(user_id=user["id"], title="Test Convo 2", db_path=self.db_path)
        create_message(conversation_id=convo2["id"], role="user", content="Hello again", db_path=self.db_path)

        delete_user(user["id"], db_path=self.db_path)
        self.assertIsNone(get_user_by_id(user["id"], db_path=self.db_path))
        self.assertIsNone(get_conversation_by_id(convo2["id"], db_path=self.db_path))
        self.assertIsNone(get_document_by_id("doc123456789012", db_path=self.db_path))


if __name__ == "__main__":
    unittest.main()
