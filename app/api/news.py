from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.news import NewsItem

 router = APIRouter(prefix="/news", tags=["MMA News"])

 @router.get("/")
 def get_news(db: Session = Depends(get_db)):
     return db.query(NewsItem).all()
