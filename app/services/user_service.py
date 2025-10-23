"""User service for business logic."""

from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


def get_user_by_id(db: Session, user_id: int) -> User | None:
    """Get user by ID.

    Args:
        db: Database session.
        user_id: User ID to search for.

    Returns:
        User object if found, None otherwise.
    """
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> User | None:
    """Get user by email.

    Args:
        db: Database session.
        email: Email address to search for.

    Returns:
        User object if found, None otherwise.
    """
    return db.query(User).filter(User.email == email).first()


def get_users(
    db: Session, skip: int = 0, limit: int = 100, role: str | None = None, is_active: bool | None = None
) -> list[User]:
    """Get list of users with optional filters.

    Args:
        db: Database session.
        skip: Number of records to skip (for pagination).
        limit: Maximum number of records to return.
        role: Optional role filter ('admin' or 'user').
        is_active: Optional active status filter.

    Returns:
        List of User objects.
    """
    query = db.query(User)

    if role:
        query = query.filter(User.role == role)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    return query.offset(skip).limit(limit).all()


def count_users(db: Session, role: str | None = None, is_active: bool | None = None) -> int:
    """Count users with optional filters.

    Args:
        db: Database session.
        role: Optional role filter.
        is_active: Optional active status filter.

    Returns:
        Total count of users matching the filters.
    """
    query = db.query(User)

    if role:
        query = query.filter(User.role == role)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    return query.count()


def create_user(db: Session, user: UserCreate) -> User:
    """Create a new user.

    Args:
        db: Database session.
        user: User creation data.

    Returns:
        Created User object.
    """
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        role=user.role,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user_update: UserUpdate) -> User | None:
    """Update an existing user.

    Args:
        db: Database session.
        user_id: ID of user to update.
        user_update: User update data.

    Returns:
        Updated User object if found, None otherwise.
    """
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None

    update_data = user_update.model_dump(exclude_unset=True)

    # Hash password if provided
    if "password" in update_data and update_data["password"]:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))

    for key, value in update_data.items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int) -> bool:
    """Delete a user.

    Args:
        db: Database session.
        user_id: ID of user to delete.

    Returns:
        True if user was deleted, False if not found.
    """
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return False

    db.delete(db_user)
    db.commit()
    return True


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    """Authenticate a user by email and password.

    Args:
        db: Database session.
        email: User's email address.
        password: User's plain text password.

    Returns:
        User object if authentication successful, None otherwise.
    """
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    if not user.is_active:
        return None
    return user
