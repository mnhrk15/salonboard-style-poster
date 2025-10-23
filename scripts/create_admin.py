"""Script to create initial admin user."""

import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User


def create_admin(email: str, password: str) -> None:
    """Create an admin user.

    Args:
        email: Admin email address.
        password: Admin password (plain text).
    """
    db = SessionLocal()

    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"Error: User with email '{email}' already exists.")
            sys.exit(1)

        # Create admin user
        hashed_password = get_password_hash(password)
        admin_user = User(
            email=email,
            hashed_password=hashed_password,
            role="admin",
            is_active=True,
        )

        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

        print(f"Successfully created admin user:")
        print(f"  ID: {admin_user.id}")
        print(f"  Email: {admin_user.email}")
        print(f"  Role: {admin_user.role}")
        print("\nYou can now sign in with these credentials.")

    except Exception as e:
        print(f"Error creating admin user: {e}")
        db.rollback()
        sys.exit(1)

    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python create_admin.py <email> <password>")
        print("Example: python create_admin.py admin@example.com SecurePassword123!")
        sys.exit(1)

    email = sys.argv[1]
    password = sys.argv[2]

    # Basic validation
    if "@" not in email:
        print("Error: Invalid email address")
        sys.exit(1)

    if len(password) < 8:
        print("Error: Password must be at least 8 characters long")
        sys.exit(1)

    create_admin(email, password)
