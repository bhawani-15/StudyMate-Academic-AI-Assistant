"""Complete end-to-end test verifying persistent chat history, auth, and conversation lifecycle."""

from pathlib import Path
import tempfile
import unittest

import auth
import database


class TestCompleteChatHistoryFlow(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_flow.db"
        database.init_db(self.db_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_complete_flow(self):
        # 1. User Authentication (Sign up + Login)
        user, err = auth.register_user(
            username="academic_user",
            email="academic@college.edu",
            password="securePassword2026!",
            db_path=self.db_path,
        )
        self.assertIsNone(err)
        self.assertIsNotNone(user)

        auth_user, err = auth.authenticate_user(
            identifier="academic@college.edu",
            password="securePassword2026!",
            db_path=self.db_path,
        )
        self.assertIsNone(err)
        self.assertEqual(auth_user["id"], user["id"])

        # 2. Document Association
        doc1 = database.create_document(
            doc_id="b777f7f0d0dcf12e",
            user_id=user["id"],
            file_name="QUANTUM MECHANICS.pdf",
            file_path="Data/QUANTUM MECHANICS.pdf",
            file_size=121574,
            page_count=8,
            chunk_count=21,
            db_path=self.db_path,
        )
        self.assertEqual(doc1["id"], "b777f7f0d0dcf12e")

        user_docs = database.get_documents_by_user(user["id"], db_path=self.db_path)
        self.assertEqual(len(user_docs), 1)

        # 3. New Chat: Start Conversation 1
        q1 = "What is the Heisenberg uncertainty principle?"
        title1 = q1[:38] + ("..." if len(q1) > 38 else "")
        convo1 = database.create_conversation(
            user_id=user["id"],
            title=title1,
            db_path=self.db_path,
        )
        self.assertEqual(convo1["title"], title1)

        # 4. Save User Message in Convo 1
        msg1_user = database.create_message(
            conversation_id=convo1["id"],
            role="user",
            content=q1,
            db_path=self.db_path,
        )
        self.assertEqual(msg1_user["role"], "user")
        self.assertEqual(msg1_user["content"], q1)

        # 5. Save Assistant Message with Source Attributions in Convo 1
        mock_answer = (
            "The Heisenberg Uncertainty Principle states that position and momentum "
            "cannot be measured simultaneously with arbitrary precision."
        )
        mock_sources = [
            {
                "page_content": "Delta x * Delta p >= hbar / 2",
                "metadata": {"source": "Data/QUANTUM MECHANICS.pdf", "page": 1, "document_id": "b777f7f0d0dcf12e"},
            }
        ]
        msg1_assistant = database.create_message(
            conversation_id=convo1["id"],
            role="assistant",
            content=mock_answer,
            sources=mock_sources,
            db_path=self.db_path,
        )
        self.assertEqual(msg1_assistant["role"], "assistant")
        self.assertEqual(len(msg1_assistant["sources"]), 1)
        self.assertEqual(msg1_assistant["sources"][0]["metadata"]["page"], 1)

        # 6. Start Conversation 2 (New Chat)
        q2 = "Explain object-oriented programming concepts."
        title2 = q2[:38] + ("..." if len(q2) > 38 else "")
        convo2 = database.create_conversation(
            user_id=user["id"],
            title=title2,
            db_path=self.db_path,
        )

        database.create_message(
            conversation_id=convo2["id"],
            role="user",
            content=q2,
            db_path=self.db_path,
        )
        database.create_message(
            conversation_id=convo2["id"],
            role="assistant",
            content="OOP concepts include encapsulation, inheritance, and polymorphism.",
            sources=[],
            db_path=self.db_path,
        )

        # 7. Conversation List Verification
        all_convos = database.get_conversations_by_user(user["id"], db_path=self.db_path)
        self.assertEqual(len(all_convos), 2)
        # Most recently updated conversation should be first
        self.assertEqual(all_convos[0]["id"], convo2["id"])
        self.assertEqual(all_convos[1]["id"], convo1["id"])

        # 8. Open Conversation 1 and verify message history persistence
        reloaded_messages1 = database.get_messages_by_conversation(convo1["id"], db_path=self.db_path)
        self.assertEqual(len(reloaded_messages1), 2)
        self.assertEqual(reloaded_messages1[0]["content"], q1)
        self.assertEqual(reloaded_messages1[1]["content"], mock_answer)
        self.assertEqual(reloaded_messages1[1]["sources"][0]["metadata"]["document_id"], "b777f7f0d0dcf12e")

        # 9. Open Conversation 2 and verify message isolation
        reloaded_messages2 = database.get_messages_by_conversation(convo2["id"], db_path=self.db_path)
        self.assertEqual(len(reloaded_messages2), 2)
        self.assertEqual(reloaded_messages2[0]["content"], q2)

        # 10. Delete Conversation 1
        deleted = database.delete_conversation(convo1["id"], user_id=user["id"], db_path=self.db_path)
        self.assertTrue(deleted)

        remaining_convos = database.get_conversations_by_user(user["id"], db_path=self.db_path)
        self.assertEqual(len(remaining_convos), 1)
        self.assertEqual(remaining_convos[0]["id"], convo2["id"])

        # Check that messages of deleted convo1 were cascade-deleted
        self.assertEqual(len(database.get_messages_by_conversation(convo1["id"], db_path=self.db_path)), 0)

        # Check that messages of convo2 remain completely intact
        self.assertEqual(len(database.get_messages_by_conversation(convo2["id"], db_path=self.db_path)), 2)


if __name__ == "__main__":
    unittest.main()
