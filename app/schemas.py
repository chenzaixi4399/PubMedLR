from pydantic import BaseModel
from datetime import date
from typing import List, Optional

class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class ArticleCreate(BaseModel):
    pmid: str
    title: str
    doi: str
    pub_date: date
    journal_name: str
    authors: str
    abstract: str
    article_url: str

class ReviewRequest(BaseModel):
    status: str
    reason: Optional[str] = None

class ArticleResponse(BaseModel):
    id: int
    pmid: str
    title: str
    doi: str
    pub_date: date
    journal_name: str
    authors: str
    abstract: str
    article_url: str
    review_status: str
    review_reason: Optional[str]

    class Config:
        from_attributes = True

class ArticleListResponse(BaseModel):
    articles: List[ArticleResponse]
    page: int
    total_pages: int