import json
import os
from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles

# 1. FastAPI აპლიკაციის ერთადერთი და სწორი ინიციალიზაცია
app = FastAPI(
    title="MMA Betting Intelligence Hub",
    description="Arbitrage Detection & Odds Monitoring API",
    version="1.0.0"
)

# 2. სტატიკური ფაილების და სდელების (Static & Templates) მიბმა
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# 3. სესიების მიდლვერი ავტორიზაციისთვის
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY", "super-secret-key-123"))

from app.db.database import SessionLocal, engine
from app.models import Base, Event, Fighter, OddsRecord, Article
from app.api.v1.arbitrage import router as arbitrage_router
from app.services.scraper import scrape_tapology_legends
from app.services.news_agent import fetch_and_save_ufc_news

Base.metadata.create_all(bind=engine)

# 4. ადმინ-პანელის ავტორიზაცია JSON ლექსიკონით (Environment Variables-დან)
class AdminAuth(AuthenticationBackend):
    def __init__(self, secret_key: str):
        super().__init__(secret_key=secret_key)

    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")
        
        admins_env = os.getenv("ADMINS_JSON", "{}")
        try:
            admins_dict = json.loads(admins_env)
        except json.JSONDecodeError:
            admins_dict = {}
        
        if username in admins_dict and admins_dict[username] == password:
            request.session.setdefault("token", "authenticated")
            return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")
        return token == "authenticated"

authentication_backend = AdminAuth(secret_key=os.getenv("SECRET_KEY", "super-secret-key-123"))

# 5. SQLAdmin მოდელების ხედები (Event, Fighter, OddsRecord, Article)
class EventAdmin(ModelView, model=Event):
    column_list = [Event.id]

class FighterAdmin(ModelView, model=Fighter):
    column_list = [Fighter.id]

class OddsRecordAdmin(ModelView, model=OddsRecord):
    column_list = [OddsRecord.id]

class ArticleAdmin(ModelView, model=Article):
    column_list = [Article.id, Article.title, Article.category, Article.created_at]
    form_columns = [Article.title, Article.category, Article.image_url, Article.content]

# ადმინ-პანელის ინიციალიზაცია
admin = Admin(app, engine, authentication_backend=authentication_backend)
admin.add_view(EventAdmin)
admin.add_view(FighterAdmin)
admin.add_view(OddsRecordAdmin)
admin.add_view(ArticleAdmin)

app.include_router(arbitrage_router)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# მთავარი გვერდი (სტატიების გამოტანით)
@app.get("/", response_class=HTMLResponse)
def read_root(request: Request, db: Session = Depends(get_db)):
    events = db.query(Event).all()
    articles = db.query(Article).order_by(Article.created_at.desc()).all()
    return templates.TemplateResponse(request, "index.html", {
        "events": events,
        "articles": articles
    })

@app.get("/api/events")
def get_events(db: Session = Depends(get_db)):
    return db.query(Event).all()

@app.get("/api/fighters")
def get_fighters(db: Session = Depends(get_db)):
    return db.query(Fighter).all()

@app.get("/api/odds")
def get_odds(db: Session = Depends(get_db)):
    return db.query(OddsRecord).all()

@app.get("/api/legends")
async def get_legendary_fights():
    data = await scrape_tapology_legends()
    return data

# --- ავტომატური ნიუსების აგენტის ენდპოინტი ---
@app.get("/api/fetch-news")
async def run_news_agent(db: Session = Depends(get_db)):
    result = await fetch_and_save_ufc_news(db)
    return result
