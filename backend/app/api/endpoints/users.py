from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

from app.database import get_db
from app.services.user_service import UserService
from app.auth.dependencies import get_current_active_user
from app.models.user import User

router = APIRouter()

class UserRegistration(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone_number: Optional[str] = None
    birth_date: Optional[datetime] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    medical_history: Optional[str] = None
    allergies: Optional[str] = None
    medications: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserProfile(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    phone_number: Optional[str]
    birth_date: Optional[datetime]
    gender: Optional[str]
    address: Optional[str]
    emergency_contact_name: Optional[str]
    emergency_contact_phone: Optional[str]
    medical_history: Optional[str]
    allergies: Optional[str]
    medications: Optional[str]
    is_verified: bool
    created_at: datetime
    updated_at: datetime

class NotificationPreference(BaseModel):
    type: str
    enabled: bool
    description: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    birth_date: Optional[datetime] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    medical_history: Optional[str] = None
    allergies: Optional[str] = None
    medications: Optional[str] = None

class PasswordChange(BaseModel):
    current_password: str
    new_password: str

@router.post("/login")
async def login_user(user_login: UserLogin, db: Session = Depends(get_db)):
    """ユーザーログインエンドポイント"""
    user_service = UserService(db)
    return user_service.login(user_login.email, user_login.password)

@router.post("/register", response_model=UserProfile)
async def register_user(user_data: UserRegistration, db: Session = Depends(get_db)):
    """ユーザー登録エンドポイント"""
    user_service = UserService(db)
    user = user_service.create_user(user_data.dict())
    
    return UserProfile(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        phone_number=user.phone_number,
        birth_date=user.birth_date,
        gender=user.gender,
        address=user.address,
        emergency_contact_name=user.emergency_contact_name,
        emergency_contact_phone=user.emergency_contact_phone,
        medical_history=user.medical_history,
        allergies=user.allergies,
        medications=user.medications,
        is_verified=user.is_verified,
        created_at=user.created_at,
        updated_at=user.updated_at
    )

@router.get("/profile", response_model=UserProfile)
async def get_user_profile(current_user: User = Depends(get_current_active_user)):
    """ユーザープロフィールを取得するエンドポイント"""
    return UserProfile(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        phone_number=current_user.phone_number,
        birth_date=current_user.birth_date,
        gender=current_user.gender,
        address=current_user.address,
        emergency_contact_name=current_user.emergency_contact_name,
        emergency_contact_phone=current_user.emergency_contact_phone,
        medical_history=current_user.medical_history,
        allergies=current_user.allergies,
        medications=current_user.medications,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )

@router.put("/profile", response_model=UserProfile)
async def update_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """ユーザープロフィールを更新するエンドポイント"""
    user_service = UserService(db)
    updated_user = user_service.update_user(current_user.id, user_update.dict(exclude_unset=True))
    
    return UserProfile(
        id=updated_user.id,
        email=updated_user.email,
        full_name=updated_user.full_name,
        phone_number=updated_user.phone_number,
        birth_date=updated_user.birth_date,
        gender=updated_user.gender,
        address=updated_user.address,
        emergency_contact_name=updated_user.emergency_contact_name,
        emergency_contact_phone=updated_user.emergency_contact_phone,
        medical_history=updated_user.medical_history,
        allergies=updated_user.allergies,
        medications=updated_user.medications,
        is_verified=updated_user.is_verified,
        created_at=updated_user.created_at,
        updated_at=updated_user.updated_at
    )

@router.get("/notification-preferences", response_model=List[NotificationPreference])
async def get_notification_preferences():
    """
    通知設定のオプションを取得するエンドポイント
    """
    preferences = [
        NotificationPreference(
            type="hospital_news",
            enabled=True,
            description="病院からのお知らせ"
        ),
        NotificationPreference(
            type="health_info",
            enabled=True,
            description="健康情報・予防情報"
        ),
        NotificationPreference(
            type="appointment_reminder",
            enabled=False,
            description="予約リマインダー"
        ),
        NotificationPreference(
            type="emergency_alert",
            enabled=True,
            description="緊急時のアラート"
        ),
    ]
    
    return preferences

@router.put("/password")
async def change_password(
    password_change: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """パスワードを変更するエンドポイント"""
    user_service = UserService(db)
    user_service.change_password(
        current_user.id, 
        password_change.current_password, 
        password_change.new_password
    )
    return {"message": "パスワードが正常に変更されました"}

@router.delete("/account")
async def delete_user_account(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """ユーザーアカウントを削除するエンドポイント"""
    user_service = UserService(db)
    user_service.delete_user(current_user.id)
    return {"message": "アカウントが正常に削除されました"}