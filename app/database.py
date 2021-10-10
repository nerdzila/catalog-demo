from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from . import config, security

SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def initialize_db():
    # TODO: delegate DB initalization to migrations library
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    with engine.connect() as conn:
        hashed_password = security.get_password_hash(
            config.FIRST_USER_PASSWORD
        )
        conn.execute(
            """
                INSERT INTO
                    users(email, hashed_password, is_admin)
                    VALUES(:email, :pwd, :is_admin)
            """,
            email=config.FIRST_USER_EMAIL,
            pwd=hashed_password,
            is_admin=True
        )

        for product in config.INITIAL_PRODUCTS:
            conn.execute(
                """
                    INSERT INTO
                        products(id, sku, name, brand, price, description)
                        VALUES(:id, :sku, :name, :brand, :price, :description)
                """,
                product
            )
