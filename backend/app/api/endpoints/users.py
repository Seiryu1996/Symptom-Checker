from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

router = APIRouter()
security = HTTPBearer(auto_error=False)

class UserRegistration(BaseModel):
    email: EmailStr
    name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    notification_preferences: Optional[List[str]] = []

class UserProfile(BaseModel):
    id: str
    email: EmailStr
    name: str
    age: Optional[int]
    gender: Optional[str]
    phone: Optional[str]
    notification_preferences: List[str]
    created_at: datetime
    updated_at: datetime

class NotificationPreference(BaseModel):
    type: str
    enabled: bool
    description: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    notification_preferences: Optional[List[str]] = None

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    現在のユーザーを取得する（認証チェック）
    実際の実装では、JWTトークンの検証を行う
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="認証が必要です",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 実際の実装では、トークンの検証とユーザー情報の取得を行う
    # ここではサンプルユーザーを返す
    return {"user_id": "user_123", "email": "user@example.com"}

@router.post("/register", response_model=UserProfile)
async def register_user(user_data: UserRegistration):
    """
    ユーザー登録エンドポイント
    """
    try:
        # 実際の実装では、データベースにユーザーを作成
        # ここではサンプルレスポンスを返す
        user_profile = UserProfile(
            id=f"user_{hash(user_data.email)}",
            email=user_data.email,
            name=user_data.name,
            age=user_data.age,
            gender=user_data.gender,
            phone=user_data.phone,
            notification_preferences=user_data.notification_preferences or [],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        return user_profile
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ユーザー登録中にエラーが発生しました: {str(e)}")

@router.get("/profile", response_model=UserProfile)
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    """
    ユーザープロフィールを取得するエンドポイント
    """
    try:
        # 実際の実装では、データベースからユーザー情報を取得
        # ここではサンプルデータを返す
        user_profile = UserProfile(
            id=current_user["user_id"],
            email=current_user["email"],
            name="テストユーザー",
            age=30,
            gender="その他",
            phone="080-1234-5678",
            notification_preferences=["病院からのお知らせ", "健康情報"],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        return user_profile
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"プロフィール取得中にエラーが発生しました: {str(e)}")

@router.put("/profile", response_model=UserProfile)
async def update_user_profile(
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    ユーザープロフィールを更新するエンドポイント
    """
    try:
        # 実際の実装では、データベースのユーザー情報を更新
        # ここではサンプルデータを返す
        updated_profile = UserProfile(
            id=current_user["user_id"],
            email=current_user["email"],
            name=user_update.name or "テストユーザー",
            age=user_update.age or 30,
            gender=user_update.gender or "その他",
            phone=user_update.phone or "080-1234-5678",
            notification_preferences=user_update.notification_preferences or ["病院からのお知らせ"],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        return updated_profile
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"プロフィール更新中にエラーが発生しました: {str(e)}")

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

@router.delete("/account")
async def delete_user_account(current_user: dict = Depends(get_current_user)):
    """
    ユーザーアカウントを削除するエンドポイント
    """
    try:
        # 実際の実装では、データベースからユーザーを削除
        # ここではサンプルレスポンスを返す
        return {"message": "アカウントが正常に削除されました"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"アカウント削除中にエラーが発生しました: {str(e)}")