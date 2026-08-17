from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.arbitrage_service import calculate_event_arbitrage

router = APIRouter(prefix="/api/v1/events", tags=["Arbitrage"])


@router.get("/{event_id}/arbitrage")
def get_event_arbitrage(
    event_id: int, total_stake: float = 1000.0, db: Session = Depends(get_db)
):
    result = calculate_event_arbitrage(db=db, event_id=event_id, total_stake=total_stake)

    if result.get("market_status") == "EVENT_NOT_FOUND":
        raise HTTPException(status_code=404, detail="Event not found")

    return result