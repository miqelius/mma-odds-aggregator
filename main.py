from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine
from app.models import Base, Event, Fighter, OddsRecord
from app.api.v1.arbitrage import router as arbitrage_router
from app.services.scraper import scrape_tapology_legends

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MMA Betting Intelligence Hub",
    description="Arbitrage Detection & Odds Monitoring API",
    version="1.0.0"
)

# მივუჩინოთ FastAPI-ს სად არის ჩვენი templates საქაღალდე
templates = Jinja2Templates(directory="templates")

app.include_router(arbitrage_router)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# მთავარი გვერდი, რომელიც HTML ფაილს აჩვენებს ბრაუზერში
@app.get("/", response_class=HTMLResponse)
def read_root(request: Request, db: Session = Depends(get_db)):
    events = db.query(Event).all()
    # ვუგზავნით მონაცემებს HTML შაბლონს (გასწორებულია Starlette-ის ახალი ვერსიებისთვის)
    return templates.TemplateResponse(request, "index.html", {"events": events})

@app.get("/api/events")
def get_events(db: Session = Depends(get_db)):
    return db.query(Event).all()

@app.get("/api/fighters")
def get_fighters(db: Session = Depends(get_db)):
    return db.query(Fighter).all()

@app.get("/api/odds")
def get_odds(db: Session = Depends(get_db)):
    return db.query(OddsRecord).all()

# Tapology-ს სკრაპერის ენდპოინტი
@app.get("/api/legends")
async def get_legendary_fights():
    data = await scrape_tapology_legends()
    return data
