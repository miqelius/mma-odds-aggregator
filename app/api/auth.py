from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse

router = APIRouter(prefix="/auth", tags=["Auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="ეს ემაილი უკვე დაკავებულია")
    
    hashed_password = pwd_context.hash(user.password)
    db_user = User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
