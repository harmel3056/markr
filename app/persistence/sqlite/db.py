from sqlalchemy import create_engine, MetaData

DATABASE_URL = "sqlite:///./data/markr.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)
