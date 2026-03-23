from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.services.auth import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Kimlik Doğrulama"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Bu e-posta adresi zaten kayıtlı")

    existing_phone = db.query(User).filter(User.phone == user_data.phone).first()
    if existing_phone:
        raise HTTPException(status_code=400, detail="Bu telefon numarası zaten kayıtlı")

    new_user = User(
        email=user_data.email,
        phone=user_data.phone,
        full_name=user_data.full_name,
        hashed_password=hash_password(user_data.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Geçersiz e-posta veya şifre")

    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}
