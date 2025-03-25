from sqlmodel import Session, SQLModel, create_engine, select

from fast_api_template.models.user import User, UserCreate
from fast_api_template.utils.password import get_password_hash


def create_test_db_and_user() -> None:
    # Define the database URL
    db_url = "sqlite:///test.db"

    # Create engine with appropriate connection arguments
    engine = create_engine(db_url, connect_args={"check_same_thread": False})

    # Drop all tables if they exist
    SQLModel.metadata.drop_all(engine)

    # Create all tables defined in SQLModel metadata
    SQLModel.metadata.create_all(engine)

    # Create session
    with Session(engine) as session:
        # Create a user
        user_in = UserCreate(
            username="admin",
            email="admin@example.com",
            password="admin",
            is_admin=True,
            is_active=True,
            is_superuser=True,
        )

        # Create user in database
        db_user = User(
            username=user_in.username,
            email=user_in.email,
            hashed_password=get_password_hash(user_in.password),
            full_name=user_in.full_name,
            is_active=user_in.is_active,
            is_superuser=user_in.is_superuser,
            is_admin=user_in.is_admin,
            disabled=user_in.disabled,
        )
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        print(f"Created user: {db_user.username}")

        # Test querying for the user
        statement = select(User).where(User.username == "admin")
        result = session.exec(statement).first()

        if result:
            print(f"Found user: {result.username}")
        else:
            print("No user found")


if __name__ == "__main__":
    create_test_db_and_user()
