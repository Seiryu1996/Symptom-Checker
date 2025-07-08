from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.symptom import Symptom, UserSymptom
from app.models.user import User

class SymptomService:
    def __init__(self, db: Session):
        self.db = db

    def get_all_symptoms(self, category: Optional[str] = None) -> List[Symptom]:
        """全症状を取得（カテゴリフィルター可能）"""
        query = self.db.query(Symptom).filter(Symptom.is_active == True)
        if category:
            query = query.filter(Symptom.category == category)
        return query.all()

    def get_symptom_categories(self) -> List[str]:
        """症状カテゴリ一覧を取得"""
        categories = self.db.query(Symptom.category).filter(
            Symptom.is_active == True
        ).distinct().all()
        return [category[0] for category in categories]

    def search_symptoms(self, query: str) -> List[Symptom]:
        """症状を検索"""
        return self.db.query(Symptom).filter(
            Symptom.is_active == True,
            Symptom.name.ilike(f"%{query}%")
        ).all()

    def get_symptom_suggestions(self, partial_name: str) -> List[dict]:
        """症状候補を取得"""
        symptoms = self.db.query(Symptom).filter(
            Symptom.is_active == True,
            Symptom.name.ilike(f"%{partial_name}%")
        ).limit(10).all()
        
        return [
            {
                "id": symptom.id,
                "name": symptom.name,
                "category": symptom.category,
                "description": symptom.description
            }
            for symptom in symptoms
        ]

    def record_user_symptoms(self, user_id: int, symptoms_data: List[dict]) -> List[UserSymptom]:
        """ユーザーの症状を記録"""
        # 既存のユーザー症状をクリア
        self.db.query(UserSymptom).filter(UserSymptom.user_id == user_id).delete()
        
        user_symptoms = []
        for symptom_data in symptoms_data:
            user_symptom = UserSymptom(
                user_id=user_id,
                symptom_id=symptom_data["symptom_id"],
                severity=symptom_data["severity"],
                duration_days=symptom_data.get("duration_days"),
                notes=symptom_data.get("notes"),
                location=symptom_data.get("location"),
                frequency=symptom_data.get("frequency")
            )
            self.db.add(user_symptom)
            user_symptoms.append(user_symptom)
        
        self.db.commit()
        return user_symptoms

    def get_user_symptoms(self, user_id: int) -> List[UserSymptom]:
        """ユーザーの症状履歴を取得"""
        return self.db.query(UserSymptom).filter(
            UserSymptom.user_id == user_id
        ).join(Symptom).all()

    def create_symptom(self, symptom_data: dict) -> Symptom:
        """新しい症状を作成（管理者用）"""
        symptom = Symptom(
            name=symptom_data["name"],
            description=symptom_data.get("description"),
            category=symptom_data["category"],
            severity_level=symptom_data.get("severity_level", 1),
            common_causes=symptom_data.get("common_causes"),
            related_specialties=symptom_data.get("related_specialties")
        )
        
        self.db.add(symptom)
        self.db.commit()
        self.db.refresh(symptom)
        return symptom