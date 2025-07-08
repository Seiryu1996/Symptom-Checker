from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.auth.password import hash_password, verify_password
from app.auth.jwt_handler import create_access_token

class UserService:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user_data: dict) -> User:
        """新しいユーザーを作成"""
        # メールアドレスの重複チェック
        existing_user = self.db.query(User).filter(User.email == user_data["email"]).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # パスワードをハッシュ化
        hashed_password = hash_password(user_data["password"])
        
        # ユーザーオブジェクトを作成
        user = User(
            email=user_data["email"],
            hashed_password=hashed_password,
            full_name=user_data["full_name"],
            phone_number=user_data.get("phone_number"),
            birth_date=user_data.get("birth_date"),
            gender=user_data.get("gender"),
            address=user_data.get("address"),
            emergency_contact_name=user_data.get("emergency_contact_name"),
            emergency_contact_phone=user_data.get("emergency_contact_phone"),
            medical_history=user_data.get("medical_history"),
            allergies=user_data.get("allergies"),
            medications=user_data.get("medications")
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """ユーザー認証"""
        user = self.db.query(User).filter(User.email == email).first()
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user

    def login(self, email: str, password: str) -> dict:
        """ユーザーログイン"""
        user = self.authenticate_user(email, password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        
        access_token = create_access_token(data={"sub": user.email})
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "is_verified": user.is_verified
            }
        }

    def get_user_by_email(self, email: str) -> Optional[User]:
        """メールアドレスでユーザーを取得"""
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """IDでユーザーを取得"""
        return self.db.query(User).filter(User.id == user_id).first()

    def update_user(self, user_id: int, user_data: dict) -> User:
        """ユーザー情報を更新"""
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # 更新可能なフィールドのみ更新
        allowed_fields = [
            "full_name", "phone_number", "birth_date", "gender", "address",
            "emergency_contact_name", "emergency_contact_phone", 
            "medical_history", "allergies", "medications"
        ]
        
        for field in allowed_fields:
            if field in user_data:
                setattr(user, field, user_data[field])
        
        self.db.commit()
        self.db.refresh(user)
        return user

    def change_password(self, user_id: int, current_password: str, new_password: str) -> bool:
        """パスワードを変更"""
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if not verify_password(current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect current password"
            )
        
        user.hashed_password = hash_password(new_password)
        self.db.commit()
        return True

    def delete_user(self, user_id: int) -> bool:
        """ユーザーアカウントを削除"""
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # ソフトデリート（is_active = False）
        user.is_active = False
        self.db.commit()
        return True