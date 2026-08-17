from sqlalchemy.orm import Session, joinedload
from datetime import datetime, timedelta
from app.models.event import Event
from app.models.odds import OddsRecord

def find_arbitrage_opportunities(db: Session, max_age_minutes: int = 15):
    now = datetime.utcnow()
    cutoff_time = now - timedelta(minutes=max_age_minutes)

    # N+1 პრობლემის მოგვარება: მებრძოლების წინასწარ ჩატვირთვა
    events = db.query(Event).options(
        joinedload(Event.fighter_a),
        joinedload(Event.fighter_b)
    ).all()

    opportunities = []

    for event in events:
        odds_records = db.query(OddsRecord).filter(
            OddsRecord.event_id == event.id,
            OddsRecord.timestamp >= cutoff_time
        ).all()

        if not odds_records:
            continue

        fighter_a_odds = [r for r in odds_records if r.fighter_id == event.fighter_a_id]
        fighter_b_odds = [r for r in odds_records if r.fighter_id == event.fighter_b_id]

        if not fighter_a_odds or not fighter_b_odds:
            continue

        # Pairwise Matching: ყველა შესაძლო ბუკმეიკერის კომბინაციის შემოწმება
        for odd_a in fighter_a_odds:
            for odd_b in fighter_b_odds:
                # გამოვრიცხოთ ერთი და იგივე ბუკმეიკერი (self-match აკრძალულია)
                if odd_a.bookmaker == odd_b.bookmaker:
                    continue

                if odd_a.odds_value <= 1 or odd_b.odds_value <= 1:
                    continue

                inv_sum = (1 / odd_a.odds_value) + (1 / odd_b.odds_value)

                # თუ ჯამი 1-ზე ნაკლებია, გვაქვს არბიტრაჟი!
                if inv_sum < 1:
                    arbitrage_pct = (1 - inv_sum) / inv_sum * 100
                    
                    # 1000 ერთეულის (მაგ. ლარის) გარანტირებული გადახდის სიმულაცია
                    payout = 1000
                    stake_a = payout / odd_a.odds_value
                    stake_b = payout / odd_b.odds_value
                    
                    # ვიგებთ უახლესი odds-ის ასაკს წუთებში
                    latest_timestamp = max(odd_a.timestamp, odd_b.timestamp)
                    odds_age_minutes = int((now - latest_timestamp).total_seconds() // 60)

                    opportunities.append({
                        "event_id": event.id,
                        "event_name": event.name,
                        "fighter_a_name": event.fighter_a.name,
                        "fighter_b_name": event.fighter_b.name,
                        "best_odds_a": odd_a.odds_value,
                        "best_odds_b": odd_b.odds_value,
                        "bookmaker_a": odd_a.bookmaker,
                        "bookmaker_b": odd_b.bookmaker,
                        "implied_probability": inv_sum,
                        "arbitrage_percentage": arbitrage_pct,
                        "stake_a": stake_a,
                        "stake_b": stake_b,
                        "odds_age_minutes": odds_age_minutes,
                    })

    # სორტირება: ყველაზე მომგებიანი არბიტრაჟი გამოჩნდეს პირველი
    opportunities.sort(key=lambda x: x["arbitrage_percentage"], reverse=True)
    return opportunities