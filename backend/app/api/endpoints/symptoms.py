from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter()

class SymptomInput(BaseModel):
    text: str
    severity: Optional[int] = None  # 1-5 scale
    duration: Optional[str] = None  # "1日", "1週間", etc.
    location: Optional[str] = None  # "頭", "腹", etc.

class SymptomResponse(BaseModel):
    id: str
    text: str
    severity: Optional[int]
    duration: Optional[str]
    location: Optional[str]
    category: Optional[str]
    keywords: List[str]

class SymptomSuggestion(BaseModel):
    text: str
    category: str
    common: bool

@router.post("/input", response_model=SymptomResponse)
async def input_symptom(symptom: SymptomInput):
    """
    症状入力エンドポイント
    自由入力された症状を解析し、構造化された形式で返す
    """
    try:
        # 症状の解析ロジック（実際の実装では自然言語処理を使用）
        keywords = symptom.text.split()
        category = "一般的な症状"  # 実際の実装では症状分類ロジック
        
        response = SymptomResponse(
            id=f"symptom_{hash(symptom.text)}",
            text=symptom.text,
            severity=symptom.severity,
            duration=symptom.duration,
            location=symptom.location,
            category=category,
            keywords=keywords
        )
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"症状の処理中にエラーが発生しました: {str(e)}")

@router.get("/suggestions", response_model=List[SymptomSuggestion])
async def get_symptom_suggestions(category: Optional[str] = None):
    """
    症状候補を取得するエンドポイント
    選択式の症状入力で使用
    """
    # 実際の実装では データベースから取得
    suggestions = [
        SymptomSuggestion(text="頭痛", category="頭部", common=True),
        SymptomSuggestion(text="発熱", category="全身", common=True),
        SymptomSuggestion(text="腹痛", category="腹部", common=True),
        SymptomSuggestion(text="咳", category="呼吸器", common=True),
        SymptomSuggestion(text="めまい", category="頭部", common=False),
        SymptomSuggestion(text="吐き気", category="消化器", common=False),
    ]
    
    if category:
        suggestions = [s for s in suggestions if s.category == category]
    
    return suggestions

@router.get("/categories")
async def get_symptom_categories():
    """
    症状カテゴリを取得するエンドポイント
    """
    return {
        "categories": [
            {"id": "head", "name": "頭部", "icon": "🧠"},
            {"id": "respiratory", "name": "呼吸器", "icon": "🫁"},
            {"id": "digestive", "name": "消化器", "icon": "🫃"},
            {"id": "body", "name": "全身", "icon": "🏃"},
            {"id": "skin", "name": "皮膚", "icon": "🤲"},
            {"id": "eyes", "name": "目", "icon": "👀"},
            {"id": "ears", "name": "耳", "icon": "👂"},
            {"id": "other", "name": "その他", "icon": "❓"},
        ]
    }