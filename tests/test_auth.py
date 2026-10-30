"""Test suite for authentication module."""

from pathlib import Path
import tempfile
import unittest

from auth import (
    hash_password,
    verify_password,
    validate_registration_inputs,
    register_user,
    authenticate_user,
)
from database import init_db


class TestAuth(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_auth.db"
        init_db(self.db_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_password_hashing_and_verification(self):
        password = "SecurePassword123!"
        hashed = hash_password(password)

        self.assertNotEqual(password, hashed)
        self.assertTrue(verify_password(password, hashed))
        self.assertFalse(verify_password("WrongPassword", hashed))

    def test_input_validation(self):
        # Username too short
        valid, msg = validate_registration_inputs("ab", "test@example.com", "pass123")
        self.assertFalse(valid)

        # Invalid username characters
        valid, msg = validate_registration_inputs("user name!", "test@example.com", "pass123")
        self.assertFalse(valid)

        # Invalid email
        valid, msg = validate_registration_inputs("user1", "invalid-email", "pass123")
        self.assertFalse(valid)

        # Password too short
        valid, msg = validate_registration_inputs("user1", "test@example.com", "123")
        self.assertFalse(valid)

        # Valid inputs
        valid, msg = validate_registration_inputs("user1", "test@example.com", "secure123")
        self.assertTrue(valid)
        self.assertNil = self.assertIsNone(msg)

    def test_register_and_authenticate(self):
        # Registration success
        user, err = register_user(
            username="student1",
            email="student1@university.edu",
            password="studyPassword!2026",
            db_path=self.db_path,
        )
        self.assertIsNone(err)
        self.assertIsNotNone(user)
        self.assertEqual(user["username"], "student1")

        # Duplicate registration fails
        _, dup_err = register_user(
            username="student1",
            email="other@university.edu",
            password="password123",
            db_path=self.db_path,
        )
        self.assertIsNotNone(dup_err)

        # Login with username
        auth_user, err = authenticate_user(
            identifier="student1",
            password="studyPassword!2026",
            db_path=self.db_path,
        )
        self.assertIsNone(err)
        self.assertEqual(auth_user["id"], user["id"])

        # Login with email (case-insensitive)
        auth_user_email, err = authenticate_user(
            identifier="STUDENT1@UNIVERSITY.EDU",
            password="studyPassword!2026",
            db_path=self.db_path,
        )
        self.assertIsNone(err)
        self.assertEqual(auth_user_email["id"], user["id"])

        # Login with wrong password
        failed_user, err = authenticate_user(
            identifier="student1",
            password="WrongPassword123",
            db_path=self.db_path,
        )
        self.assertIsNone(failed_user)
        self.assertIn("Invalid", err)


if __name__ == "__main__":
    unittest.main()
