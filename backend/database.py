from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime
import os

# Configuration de la base de données
DATABASE_PATH = os.path.join(os.path.dirname(__file__), '..', 'snap_budget.db')
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    search_history = relationship("SearchHistory", back_populates="user")
    
class SearchHistory(Base):
    __tablename__ = "search_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    product_name = Column(String, index=True)
    product_price = Column(Float)
    budget = Column(Float)
    similarity_score = Column(Float, default=0.0)
    ai_advice = Column(String)
    search_date = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    
    user = relationship("User", back_populates="search_history")

# Créer les tables
Base.metadata.create_all(bind=engine)

def get_db():
    """Dépendance pour obtenir la session DB"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
