from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.odds import ArbitrageOpportunity
from app.services.arbitrage import find_arbitrage_opportunities
from app.dependencies import get_current_user

router = APIRouter(prefix="/arbitrage", tags=["Arbitrage"])

@router.get("/opportunities", response_model=List[ArbitrageOpportunity])
def get_opportunities(
    max_age_minutes: int = Query(15, ge=1, le=180),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return find_arbitrage_opportunities(db, max_age_minutes=max_age_minutes)