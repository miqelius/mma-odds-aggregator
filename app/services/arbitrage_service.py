from datetime import datetime, timezone
from sqlalchemy.orm import Session, joinedload
from app.models import Event, Fighter, OddsRecord


def utcnow():
    return datetime.now(timezone.utc)


def calculate_event_arbitrage(
    db: Session,
    event_id: int,
    total_stake: float = 1000.0,
    staleness_minutes: int = 15,
):
    """
    Find the best arbitrage opportunity for a given event.
    Evaluates odds age to correctly assign ACTIVE or STALE statuses.
    """
    now = utcnow()

    event = (
        db.query(Event)
        .options(joinedload(Event.fighter_a), joinedload(Event.fighter_b))
        .filter(Event.id == event_id)
        .first()
    )

    if not event:
        return {
            "event_id": event_id,
            "market_status": "EVENT_NOT_FOUND",
        }

    odds_records = (
        db.query(OddsRecord)
        .filter(OddsRecord.event_id == event_id)
        .order_by(OddsRecord.timestamp.desc())
        .all()
    )

    if not odds_records:
        return {
            "event_id": event_id,
            "promotion": event.promotion,
            "fighter_a_name": event.fighter_a.name,
            "fighter_b_name": event.fighter_b.name,
            "market_status": "NO_ODDS",
        }

    best_odd_a = None  # საუკეთესო კოეფიციენტი პირველი მებრძოლისთვის
    best_odd_b = None  # საუკეთესო კოეფიციენტი მეორე მებრძოლისთვის

    for record in odds_records:
        if record.fighter1_odds and record.fighter1_odds > 1:
            if not best_odd_a or record.fighter1_odds > best_odd_a["odds"]:
                best_odd_a = {
                    "odds": record.fighter1_odds,
                    "sportsbook": record.sportsbook,
                    "timestamp": record.timestamp
                }
        if record.fighter2_odds and record.fighter2_odds > 1:
            if not best_odd_b or record.fighter2_odds > best_odd_b["odds"]:
                best_odd_b = {
                    "odds": record.fighter2_odds,
                    "sportsbook": record.sportsbook,
                    "timestamp": record.timestamp
                }

    if not best_odd_a or not best_odd_b:
        return {
            "event_id": event_id,
            "promotion": event.promotion,
            "fighter_a_name": event.fighter_a.name,
            "fighter_b_name": event.fighter_b.name,
            "market_status": "INSUFFICIENT_ODDS",
        }

    odds_a_val = best_odd_a["odds"]
    odds_b_val = best_odd_b["odds"]

    inv_sum = (1 / odds_a_val) + (1 / odds_b_val)
    
    if inv_sum >= 1:
        return {
            "event_id": event_id,
            "promotion": event.promotion,
            "fighter_a_name": event.fighter_a.name,
            "fighter_b_name": event.fighter_b.name,
            "best_odds_a": odds_a_val,
            "best_odds_b": odds_b_val,
            "bookmaker_a": best_odd_a["sportsbook"],
            "bookmaker_b": best_odd_b["sportsbook"],
            "implied_probability": round(inv_sum, 4),
            "market_status": "NO_OPPORTUNITY",
        }

    arb_pct = (1 - inv_sum) / inv_sum * 100

    age_a = (now - best_odd_a["timestamp"]).total_seconds() / 60
    age_b = (now - best_odd_b["timestamp"]).total_seconds() / 60
    max_age_minutes = int(max(age_a, age_b))

    market_status = "STALE" if max_age_minutes > staleness_minutes else "ACTIVE"

    stake_a = total_stake * (1 / odds_a_val) / inv_sum
    stake_b = total_stake * (1 / odds_b_val) / inv_sum

    return {
        "event_id": event_id,
        "promotion": event.promotion,
        "fighter_a_name": event.fighter_a.name,
        "fighter_b_name": event.fighter_b.name,
        "best_odds_a": odds_a_val,
        "best_odds_b": odds_b_val,
        "bookmaker_a": best_odd_a["sportsbook"],
        "bookmaker_b": best_odd_b["sportsbook"],
        "implied_probability": round(inv_sum, 4),
        "arbitrage_percentage": round(arb_pct, 2),
        "stake_a": round(stake_a, 2),
        "stake_b": round(stake_b, 2),
        "odds_age_minutes": max_age_minutes,
        "market_status": market_status,
    }
