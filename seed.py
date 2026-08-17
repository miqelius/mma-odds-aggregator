import app.models  
from app.db.database import SessionLocal, engine
from app.models import Base, Fighter, OddsRecord, Event
from datetime import datetime, timezone

Base.metadata.create_all(bind=engine)

db = SessionLocal()
try:
    def get_or_create_fighter(name):
        fighter = db.query(Fighter).filter(Fighter.name == name).first()
        if not fighter:
            fighter = Fighter(name=name)
            db.add(fighter)
            db.commit()
            db.refresh(fighter)
        return fighter

    f1 = get_or_create_fighter("Conor McGregor")
    f2 = get_or_create_fighter("Dustin Poirier")

    event = db.query(Event).filter(
        Event.fighter_a_id == f1.id,
        Event.fighter_b_id == f2.id
    ).first()

    if not event:
        event = Event(
            promotion="UFC",
            fighter_a_id=f1.id,
            fighter_b_id=f2.id,
            event_date=str(datetime.now(timezone.utc))
        )
        db.add(event)
        db.commit()
        db.refresh(event)

    existing_odds1 = db.query(OddsRecord).filter(
        OddsRecord.event_id == event.id,
        OddsRecord.sportsbook == "DraftKings"
    ).first()
    
    if not existing_odds1:
        db.add(OddsRecord(
            event_id=event.id,
            fighter_id=f1.id,  # 💥 აი აქ მივუთითეთ fighter_id
            sportsbook="DraftKings",
            fighter1_odds=2.10,
            fighter2_odds=1.75
        ))

    existing_odds2 = db.query(OddsRecord).filter(
        OddsRecord.event_id == event.id,
        OddsRecord.sportsbook == "FanDuel"
    ).first()
    
    if not existing_odds2:
        db.add(OddsRecord(
            event_id=event.id,
            fighter_id=f1.id,  # 💥 აქაც მივუთითეთ fighter_id
            sportsbook="FanDuel",
            fighter1_odds=1.80,
            fighter2_odds=2.05
        ))

    db.commit()
    print(f"✅ მონაცემები წარმატებით დაემატა! ივენთის ID არის: {event.id}")

finally:
    db.close()
