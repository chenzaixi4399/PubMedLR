from sqlalchemy import Column, Integer, String, Text, Date, Enum
from app.database import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

class Article(Base):
    __tablename__ = 'articles'
    id = Column(Integer, primary_key=True, index=True)
    pmid = Column(String(50), unique=True, nullable=False)
    title = Column(Text, nullable=False)
    doi = Column(String(255))
    pub_date = Column(Date)
    journal_name = Column(String(255))
    authors = Column(Text)
    abstract = Column(Text)
    article_url = Column(Text)
    review_status = Column(Enum('pending', 'approved', 'rejected'), default='pending')
    review_reason = Column(Text)