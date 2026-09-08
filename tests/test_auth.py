import unittest
from utils.security import hash_password, verify_password
from utils.validators import validate_registration, validate_email

class TestAuthSecurity(unittest.TestCase):
    """Test user authentication security functions and validators."""

    def test_password_hashing(self):
        password = "SecurePassword@123"
        hashed = hash_password(password)
        self.assertNotEqual(password, hashed)
        self.assertTrue(verify_password(hashed, password))
        self.assertFalse(verify_password(hashed, "WrongPassword"))

    def test_email_validator(self):
        self.assertTrue(validate_email("admin@recruitment.ai"))
        self.assertTrue(validate_email("user.name+tag@example.co.uk"))
        self.assertFalse(validate_email("invalid-email"))
        self.assertFalse(validate_email("@missinguser.com"))
        self.assertFalse(validate_email(""))

    def test_registration_validator(self):
        # Valid
        valid, err = validate_registration("Sarah Jenkins", "sarah@test.com", "Secret@123", "Secret@123")
        self.assertTrue(valid)
        self.assertIsNone(err)

        # Mismatched passwords
        valid, err = validate_registration("Sarah Jenkins", "sarah@test.com", "Secret@123", "Different@123")
        self.assertFalse(valid)
        self.assertEqual(err, "Passwords do not match.")

        # Short password
        valid, err = validate_registration("Sarah Jenkins", "sarah@test.com", "123", "123")
        self.assertFalse(valid)
        self.assertIn("at least 6 characters", err)

if __name__ == '__main__':
    unittest.main()

