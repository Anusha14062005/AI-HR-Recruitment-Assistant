import re
from typing import Tuple, Optional

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')

def validate_email(email: str) -> bool:
    """Check if email matches standard pattern."""
    if not email or len(email) > 150:
        return False
    return bool(EMAIL_REGEX.match(email.strip()))

def validate_password(password: str) -> Tuple[bool, Optional[str]]:
    """Validate password length and basic complexity."""
    if not password:
        return False, "Password is required."
    if len(password) < 6:
        return False, "Password must be at least 6 characters long."
    return True, None

def validate_registration(name: str, email: str, password: str, confirm_password: str) -> Tuple[bool, Optional[str]]:
    """Validate user registration inputs."""
    if not name or not name.strip():
        return False, "Full Name is required."
    if len(name.strip()) < 2:
        return False, "Name must be at least 2 characters."
    if not validate_email(email):
        return False, "A valid email address is required."
    valid_pwd, pwd_err = validate_password(password)
    if not valid_pwd:
        return False, pwd_err
    if password != confirm_password:
        return False, "Passwords do not match."
    return True, None

def validate_file_extension(filename: str, allowed_extensions: set) -> bool:
    """Validate file extension."""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in allowed_extensions

