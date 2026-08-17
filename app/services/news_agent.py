import httpx
from bs4 import BeautifulSoup
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import Article

async def fetch_and_save_ufc_news(db: Session):
    url = "https://www.mmafighting.com/rss/current"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
    }
    
    async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
        try:
            response = await client.get(url, timeout=15.0)
            if response.status_code != 200:
                return {"status": "error", "message": f"HTTP Error: {response.status_code}"}
            
            soup = BeautifulSoup(response.content, "xml")
            items = soup.find_all("item")[:5]
            
            added_count = 0
            for item in items:
                title = item.find("title").text if item.find("title") else "No Title"
                link = item.find("link").text if item.find("link") else ""
                
                raw_desc = item.find("description").text if item.find("description") else ""
                clean_desc = BeautifulSoup(raw_desc, "html.parser").get_text()
                
                existing = db.query(Article).filter(Article.title == title).first()
                if not existing:
                    new_article = Article(
                        title=title,
                        category="UFC Auto News",
                        image_url="https://images.unsplash.com/photo-1517649763962-0c6232660102?auto=format&fit=crop&w=800&q=80",
                        content=f"{clean_desc}\n\n🔗 სრული სტატია: {link}",
                        created_at=datetime.utcnow()
                    )
                    db.add(new_article)
                    added_count += 1
            
            db.commit()
            return {"status": "success", "added_articles": added_count}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
