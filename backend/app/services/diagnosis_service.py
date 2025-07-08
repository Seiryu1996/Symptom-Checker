from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import json
from app.models.diagnosis import Diagnosis, DiagnosisResult
from app.models.symptom import UserSymptom, Symptom
from app.models.user import User

class DiagnosisService:
    def __init__(self, db: Session):
        self.db = db

    def analyze_symptoms(self, user_id: int, symptoms_data: List[dict]) -> dict:
        """症状を分析して診断結果を生成"""
        # 症状データを分析
        analysis_result = self._perform_ai_analysis(symptoms_data)
        
        # 最も可能性の高い診断を取得
        top_diagnosis = self._find_matching_diagnosis(analysis_result)
        
        # 診断結果を保存
        diagnosis_result = self._save_diagnosis_result(
            user_id, top_diagnosis, symptoms_data, analysis_result
        )
        
        return {
            "diagnosis_result_id": diagnosis_result.id,
            "diagnosis": {
                "name": top_diagnosis.name,
                "description": top_diagnosis.description,
                "icd_10_code": top_diagnosis.icd_10_code,
                "category": top_diagnosis.category
            },
            "confidence_score": diagnosis_result.confidence_score,
            "urgency_level": diagnosis_result.urgency_level,
            "ai_analysis": diagnosis_result.ai_analysis,
            "recommended_actions": json.loads(diagnosis_result.recommended_actions or "[]"),
            "recommended_specialties": json.loads(top_diagnosis.recommended_specialties or "[]"),
            "follow_up_days": diagnosis_result.follow_up_date
        }

    def _perform_ai_analysis(self, symptoms_data: List[dict]) -> dict:
        """AI分析を実行（シンプルなルールベース実装）"""
        total_severity = sum(symptom["severity"] for symptom in symptoms_data)
        avg_severity = total_severity / len(symptoms_data) if symptoms_data else 0
        
        # 緊急度を判定
        urgency_level = "low"
        if avg_severity >= 8:
            urgency_level = "emergency"
        elif avg_severity >= 6:
            urgency_level = "high"
        elif avg_severity >= 4:
            urgency_level = "medium"
        
        # 推奨アクション
        recommended_actions = []
        if urgency_level == "emergency":
            recommended_actions.append("すぐに救急外来を受診してください")
        elif urgency_level == "high":
            recommended_actions.append("24時間以内に医療機関を受診してください")
        elif urgency_level == "medium":
            recommended_actions.append("数日以内に医療機関を受診することをお勧めします")
        else:
            recommended_actions.append("症状が続く場合は医療機関にご相談ください")
        
        return {
            "urgency_level": urgency_level,
            "avg_severity": avg_severity,
            "recommended_actions": recommended_actions,
            "analysis_text": f"入力された症状の平均重要度は {avg_severity:.1f}/10 です。"
        }

    def _find_matching_diagnosis(self, analysis_result: dict) -> Diagnosis:
        """症状に最も適合する診断を検索"""
        # シンプルな実装：一般的な診断を返す
        diagnosis = self.db.query(Diagnosis).filter(
            Diagnosis.is_active == True
        ).first()
        
        if not diagnosis:
            # デフォルト診断を作成
            diagnosis = Diagnosis(
                name="一般的な症状",
                description="複数の症状が確認されました。詳しい診断には医療機関での検査が必要です。",
                category="general",
                severity_level=1,
                recommended_specialties='["内科", "家庭医学科"]',
                treatment_options="医療機関での詳細な検査と診断",
                prevention_tips="規則正しい生活習慣を心がけ、症状の変化を観察してください。"
            )
            self.db.add(diagnosis)
            self.db.commit()
            self.db.refresh(diagnosis)
        
        return diagnosis

    def _save_diagnosis_result(self, user_id: int, diagnosis: Diagnosis, 
                             symptoms_data: List[dict], analysis_result: dict) -> DiagnosisResult:
        """診断結果をデータベースに保存"""
        # 信頼度スコアを計算（シンプルな実装）
        confidence_score = min(0.85, 0.5 + (analysis_result["avg_severity"] / 20))
        
        # フォローアップ日数を決定
        follow_up_days = 7
        if analysis_result["urgency_level"] == "high":
            follow_up_days = 3
        elif analysis_result["urgency_level"] == "emergency":
            follow_up_days = 1
        
        diagnosis_result = DiagnosisResult(
            user_id=user_id,
            diagnosis_id=diagnosis.id,
            confidence_score=confidence_score,
            symptoms_data=symptoms_data,
            ai_analysis=analysis_result["analysis_text"],
            recommended_actions=json.dumps(analysis_result["recommended_actions"]),
            urgency_level=analysis_result["urgency_level"],
            follow_up_date=follow_up_days
        )
        
        self.db.add(diagnosis_result)
        self.db.commit()
        self.db.refresh(diagnosis_result)
        return diagnosis_result

    def get_user_diagnosis_history(self, user_id: int) -> List[DiagnosisResult]:
        """ユーザーの診断履歴を取得"""
        return self.db.query(DiagnosisResult).filter(
            DiagnosisResult.user_id == user_id
        ).join(Diagnosis).order_by(DiagnosisResult.created_at.desc()).all()

    def get_diagnosis_result(self, result_id: int, user_id: int) -> Optional[DiagnosisResult]:
        """特定の診断結果を取得"""
        return self.db.query(DiagnosisResult).filter(
            DiagnosisResult.id == result_id,
            DiagnosisResult.user_id == user_id
        ).join(Diagnosis).first()

    def get_specialties_list(self) -> List[str]:
        """診療科一覧を取得"""
        specialties = [
            "内科", "外科", "小児科", "産婦人科", "整形外科",
            "皮膚科", "眼科", "耳鼻咽喉科", "精神科", "神経内科",
            "循環器内科", "消化器内科", "呼吸器内科", "泌尿器科",
            "放射線科", "麻酔科", "救急科", "家庭医学科"
        ]
        return specialties