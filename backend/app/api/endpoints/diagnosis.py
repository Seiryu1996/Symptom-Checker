from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter()

class DiagnosisInput(BaseModel):
    symptoms: List[str]
    patient_age: Optional[int] = None
    patient_gender: Optional[str] = None
    duration: Optional[str] = None
    severity: Optional[int] = None

class MedicalSpecialty(BaseModel):
    id: str
    name: str
    description: str
    urgency: str  # "low", "medium", "high"

class DiagnosisResult(BaseModel):
    possible_conditions: List[str]
    recommended_specialties: List[MedicalSpecialty]
    urgency_level: str
    advice: str
    confidence: float

@router.post("/analyze", response_model=DiagnosisResult)
async def analyze_symptoms(diagnosis_input: DiagnosisInput):
    """
    症状を分析して、考えられる病気と推奨される診療科を返す
    """
    try:
        # 実際の実装では、機械学習モデルや医療データベースを使用
        symptoms_text = " ".join(diagnosis_input.symptoms)
        
        # 簡単な症状マッチングロジック（実際は複雑な分析）
        possible_conditions = []
        recommended_specialties = []
        urgency_level = "medium"
        advice = "症状が続く場合は医療機関を受診してください。"
        confidence = 0.7
        
        # 症状に基づく条件分岐
        if any(keyword in symptoms_text.lower() for keyword in ["頭痛", "めまい", "意識"]):
            possible_conditions.append("頭部の疾患")
            recommended_specialties.append(
                MedicalSpecialty(
                    id="neurology",
                    name="神経内科",
                    description="脳神経に関する疾患を診療",
                    urgency="medium"
                )
            )
            recommended_specialties.append(
                MedicalSpecialty(
                    id="neurosurgery",
                    name="脳神経外科",
                    description="脳血管疾患や脳腫瘍の手術的治療",
                    urgency="high"
                )
            )
        
        if any(keyword in symptoms_text.lower() for keyword in ["発熱", "咳", "喉"]):
            possible_conditions.append("呼吸器感染症")
            recommended_specialties.append(
                MedicalSpecialty(
                    id="internal_medicine",
                    name="内科",
                    description="一般的な内科疾患の診療",
                    urgency="medium"
                )
            )
            recommended_specialties.append(
                MedicalSpecialty(
                    id="respiratory",
                    name="呼吸器科",
                    description="肺や気管支の疾患を専門的に診療",
                    urgency="medium"
                )
            )
        
        if any(keyword in symptoms_text.lower() for keyword in ["腹痛", "吐き気", "下痢"]):
            possible_conditions.append("消化器疾患")
            recommended_specialties.append(
                MedicalSpecialty(
                    id="gastroenterology",
                    name="消化器科",
                    description="胃腸や肝臓の疾患を診療",
                    urgency="medium"
                )
            )
        
        # 緊急度の判定
        if any(keyword in symptoms_text.lower() for keyword in ["激痛", "意識消失", "呼吸困難"]):
            urgency_level = "high"
            advice = "緊急性が高い可能性があります。すぐに医療機関を受診してください。"
            confidence = 0.9
        
        # デフォルトの診療科を追加
        if not recommended_specialties:
            recommended_specialties.append(
                MedicalSpecialty(
                    id="general",
                    name="一般内科",
                    description="幅広い疾患に対応する総合診療",
                    urgency="medium"
                )
            )
            possible_conditions.append("一般的な疾患")
        
        return DiagnosisResult(
            possible_conditions=possible_conditions,
            recommended_specialties=recommended_specialties,
            urgency_level=urgency_level,
            advice=advice,
            confidence=confidence
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"診断処理中にエラーが発生しました: {str(e)}")

@router.get("/specialties", response_model=List[MedicalSpecialty])
async def get_medical_specialties():
    """
    すべての診療科を取得するエンドポイント
    """
    specialties = [
        MedicalSpecialty(id="internal_medicine", name="内科", description="一般的な内科疾患", urgency="medium"),
        MedicalSpecialty(id="surgery", name="外科", description="外科的治療が必要な疾患", urgency="high"),
        MedicalSpecialty(id="pediatrics", name="小児科", description="子供の疾患全般", urgency="medium"),
        MedicalSpecialty(id="gynecology", name="婦人科", description="女性特有の疾患", urgency="medium"),
        MedicalSpecialty(id="dermatology", name="皮膚科", description="皮膚の疾患", urgency="low"),
        MedicalSpecialty(id="ophthalmology", name="眼科", description="目の疾患", urgency="medium"),
        MedicalSpecialty(id="ent", name="耳鼻咽喉科", description="耳・鼻・喉の疾患", urgency="medium"),
        MedicalSpecialty(id="orthopedics", name="整形外科", description="骨・関節・筋肉の疾患", urgency="medium"),
        MedicalSpecialty(id="neurology", name="神経内科", description="脳神経の疾患", urgency="high"),
        MedicalSpecialty(id="psychiatry", name="精神科", description="心の疾患", urgency="medium"),
    ]
    return specialties