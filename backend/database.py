from sqlalchemy import create_engine, Column, Integer, String, Float, JSON, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///./supervised_ml.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    rows = Column(Integer)
    columns = Column(Integer)
    column_names = Column(JSON)
    task_type = Column(String)          # classification / regression
    target_column = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class Experiment(Base):
    __tablename__ = "experiments"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, nullable=False)
    dataset_name = Column(String)
    algorithm = Column(String, nullable=False)
    task_type = Column(String)
    target_column = Column(String)
    hyperparameters = Column(JSON)
    metrics = Column(JSON)              # accuracy, f1, rmse, r2, etc.
    feature_importance = Column(JSON)
    confusion_matrix = Column(JSON)
    training_time_ms = Column(Float)
    test_size = Column(Float)
    status = Column(String, default="pending")   # pending / success / failed
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
