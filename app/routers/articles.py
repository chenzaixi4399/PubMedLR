# articles.py
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Article, User
from app.schemas import ArticleResponse, ReviewRequest, ArticleListResponse
from app.routers.auth import get_current_user
from typing import List, Optional

router = APIRouter(
    prefix="/article",
    tags=["article"],
    responses={404: {"description": "Not found"}}
)


@router.get("/list", response_model=ArticleListResponse)
async def get_articles(
        page: int = 1,
        search: str = "",
        review_status: Optional[str] = None,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    offset = (page - 1) * 10
    query = db.query(Article)

    # 根据审核状态筛选
    if review_status:
        query = query.filter(Article.review_status == review_status)

    # 根据标题或摘要搜索
    if search:
        query = query.filter(
            (Article.title.contains(search)) | (Article.abstract.contains(search))
        )

    articles = query.offset(offset).limit(10).all()
    total_articles = query.order_by(None).count()  # 获取总记录数
    total_pages = (total_articles + 9) // 10  # 每页10条记录

    return {
        "articles": articles,
        "page": page,
        "total_pages": total_pages
    }

@router.post("/review/{article_id}")
async def review_article(
        article_id: int,
        review: ReviewRequest,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    print(article_id)
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    # 如果审核状态为 "rejected"，审核原因不能为空
    if review.status == "rejected" and not review.reason:
        raise HTTPException(status_code=400, detail="Review reason is required for rejected articles")

    article.review_status = review.status
    article.review_reason = review.reason
    db.commit()
    return {"message": "Article reviewed successfully"}