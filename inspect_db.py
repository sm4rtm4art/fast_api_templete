from sqlalchemy import inspect
from sqlmodel import SQLModel, create_engine


def inspect_db() -> None:
    # Define the database URL
    db_url = "sqlite:///test.db"

    # Create engine with appropriate connection arguments
    engine = create_engine(db_url, connect_args={"check_same_thread": False})

    # Create all tables defined in SQLModel metadata
    SQLModel.metadata.create_all(engine)

    # Create inspector
    inspector = inspect(engine)

    # Print all table names
    print("Tables:", inspector.get_table_names())

    # Print table details
    for table in inspector.get_table_names():
        print(f"\nColumns in {table}:")
        for column in inspector.get_columns(table):
            print(f"  {column}")


if __name__ == "__main__":
    inspect_db()
