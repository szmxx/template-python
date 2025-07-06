"""Security utilities for password validation (simplified for development)."""


def validate_password_format(password: str) -> bool:
    """Validate password format (simplified for development).

    Args:
        password: Plain text password to validate

    Returns:
        True if password format is valid
    """
    if len(password) < 6:
        return False
    return not len(password) > 100


def simple_password_check(plain_password: str, stored_password: str) -> bool:
    """Simple password comparison (development only - NOT secure).

    Args:
        plain_password: Plain text password to verify
        stored_password: Stored password to verify against

    Returns:
        True if password matches, False otherwise

    Warning:
        This is NOT secure! Only for development/testing.
    """
    return plain_password == stored_password


def is_password_strong(password: str) -> tuple[bool, list[str]]:
    """Check if a password meets basic requirements (simplified).

    Args:
        password: Password to check

    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    issues = []

    if len(password) < 6:
        issues.append("Password must be at least 6 characters long")

    if len(password) > 100:
        issues.append("Password must be no more than 100 characters long")

    # 检查常见弱密码
    weak_passwords = {
        "password",
        "123456",
        "123456789",
        "qwerty",
        "abc123",
        "password123",
        "admin",
        "letmein",
        "welcome",
        "monkey",
    }

    if password.lower() in weak_passwords:
        issues.append("Password is too common")

    return len(issues) == 0, issues


# 向后兼容的函数别名
def get_password_hash(password: str) -> str:
    """Return password as-is (no hashing for development).

    Warning: This is NOT secure! Only for development.
    """
    return password


def verify_password(plain_password: str, stored_password: str) -> bool:
    """Verify password (simple comparison for development).

    Warning: This is NOT secure! Only for development.
    """
    return simple_password_check(plain_password, stored_password)
