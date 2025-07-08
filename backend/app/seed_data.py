from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.symptom import Symptom
from app.models.diagnosis import Diagnosis
from app.models.hospital import Hospital, HospitalSpecialty
from app.models.news import HealthNews, HealthAlert
from datetime import datetime, time
import json

def seed_database():
    """データベースに初期データを投入"""
    db = SessionLocal()
    try:
        # 症状データ
        seed_symptoms(db)
        # 診断データ
        seed_diagnoses(db)
        # 病院データ
        seed_hospitals(db)
        # ニュースデータ
        seed_news(db)
        # ヘルスアラート
        seed_alerts(db)
        
        db.commit()
        print("初期データの投入が完了しました")
    except Exception as e:
        db.rollback()
        print(f"初期データ投入中にエラーが発生しました: {e}")
    finally:
        db.close()

def seed_symptoms(db: Session):
    """症状データを投入"""
    symptoms_data = [
        {"name": "発熱", "category": "全身症状", "severity_level": 3, "description": "体温が平熱より高い状態"},
        {"name": "頭痛", "category": "神経系", "severity_level": 2, "description": "頭部の痛み"},
        {"name": "咳", "category": "呼吸器", "severity_level": 2, "description": "気道の刺激による反射的な呼気"},
        {"name": "のどの痛み", "category": "呼吸器", "severity_level": 2, "description": "咽頭部の痛みや不快感"},
        {"name": "鼻水", "category": "呼吸器", "severity_level": 1, "description": "鼻腔からの分泌物"},
        {"name": "腹痛", "category": "消化器", "severity_level": 3, "description": "腹部の痛み"},
        {"name": "吐き気", "category": "消化器", "severity_level": 2, "description": "嘔吐したくなる感覚"},
        {"name": "下痢", "category": "消化器", "severity_level": 2, "description": "水様性の便"},
        {"name": "胸痛", "category": "循環器", "severity_level": 4, "description": "胸部の痛み"},
        {"name": "息切れ", "category": "呼吸器", "severity_level": 3, "description": "呼吸が苦しい状態"},
        {"name": "めまい", "category": "神経系", "severity_level": 2, "description": "平衡感覚の異常"},
        {"name": "疲労感", "category": "全身症状", "severity_level": 1, "description": "全身のだるさや疲れ"},
        {"name": "関節痛", "category": "整形外科", "severity_level": 2, "description": "関節部分の痛み"},
        {"name": "皮疹", "category": "皮膚科", "severity_level": 2, "description": "皮膚の発疹"},
        {"name": "視力低下", "category": "眼科", "severity_level": 3, "description": "見えにくさ"}
    ]
    
    for symptom_data in symptoms_data:
        if not db.query(Symptom).filter(Symptom.name == symptom_data["name"]).first():
            symptom = Symptom(**symptom_data)
            db.add(symptom)

def seed_diagnoses(db: Session):
    """診断データを投入"""
    diagnoses_data = [
        {
            "name": "感冒",
            "description": "一般的な風邪症状。ウイルスが原因の上気道感染症",
            "icd_10_code": "J00",
            "category": "呼吸器疾患",
            "severity_level": 1,
            "recommended_specialties": '["内科", "家庭医学科"]',
            "treatment_options": "安静、水分補給、症状に応じた対症療法",
            "prevention_tips": "手洗い、うがい、マスク着用、十分な睡眠"
        },
        {
            "name": "急性胃腸炎",
            "description": "消化器系の急性炎症。細菌やウイルスが原因",
            "icd_10_code": "K59.1",
            "category": "消化器疾患",
            "severity_level": 2,
            "recommended_specialties": '["内科", "消化器内科"]',
            "treatment_options": "水分補給、電解質補充、必要に応じて薬物療法",
            "prevention_tips": "食品の衛生管理、手洗いの徹底"
        },
        {
            "name": "緊張型頭痛",
            "description": "最も一般的な頭痛の種類。筋肉の緊張が原因",
            "icd_10_code": "G44.2",
            "category": "神経系疾患",
            "severity_level": 2,
            "recommended_specialties": '["内科", "神経内科"]',
            "treatment_options": "ストレス管理、姿勢改善、必要に応じて鎮痛剤",
            "prevention_tips": "適度な運動、ストレス解消、規則正しい生活"
        }
    ]
    
    for diagnosis_data in diagnoses_data:
        if not db.query(Diagnosis).filter(Diagnosis.name == diagnosis_data["name"]).first():
            diagnosis = Diagnosis(**diagnosis_data)
            db.add(diagnosis)

def seed_hospitals(db: Session):
    """病院データを投入"""
    hospitals_data = [
        {
            "name": "東京総合病院",
            "description": "地域の中核を担う総合病院",
            "address": "東京都新宿区西新宿1-1-1",
            "phone_number": "03-1234-5678",
            "email": "info@tokyo-general.jp",
            "website": "https://tokyo-general.jp",
            "latitude": 35.6896,
            "longitude": 139.6917,
            "rating": 4.2,
            "total_reviews": 128,
            "emergency_services": True,
            "monday_open": time(9, 0),
            "monday_close": time(17, 0),
            "tuesday_open": time(9, 0),
            "tuesday_close": time(17, 0),
            "wednesday_open": time(9, 0),
            "wednesday_close": time(17, 0),
            "thursday_open": time(9, 0),
            "thursday_close": time(17, 0),
            "friday_open": time(9, 0),
            "friday_close": time(17, 0),
            "saturday_open": time(9, 0),
            "saturday_close": time(12, 0)
        },
        {
            "name": "さくら医院",
            "description": "家族みんなで通えるクリニック",
            "address": "東京都渋谷区渋谷2-2-2",
            "phone_number": "03-2345-6789",
            "latitude": 35.6598,
            "longitude": 139.7036,
            "rating": 4.5,
            "total_reviews": 89,
            "emergency_services": False,
            "monday_open": time(9, 0),
            "monday_close": time(18, 0),
            "tuesday_open": time(9, 0),
            "tuesday_close": time(18, 0),
            "wednesday_open": time(9, 0),
            "wednesday_close": time(18, 0),
            "thursday_open": time(9, 0),
            "thursday_close": time(18, 0),
            "friday_open": time(9, 0),
            "friday_close": time(18, 0),
            "saturday_open": time(9, 0),
            "saturday_close": time(13, 0)
        }
    ]
    
    for hospital_data in hospitals_data:
        if not db.query(Hospital).filter(Hospital.name == hospital_data["name"]).first():
            hospital = Hospital(**hospital_data)
            db.add(hospital)
            db.flush()  # IDを取得するためにflush
            
            # 診療科を追加
            if hospital_data["name"] == "東京総合病院":
                specialties = [
                    {"specialty_name": "内科", "wait_time_avg": 30},
                    {"specialty_name": "外科", "wait_time_avg": 45},
                    {"specialty_name": "小児科", "wait_time_avg": 25},
                    {"specialty_name": "整形外科", "wait_time_avg": 40},
                    {"specialty_name": "救急科", "wait_time_avg": 60}
                ]
            else:
                specialties = [
                    {"specialty_name": "内科", "wait_time_avg": 20},
                    {"specialty_name": "小児科", "wait_time_avg": 15}
                ]
            
            for specialty_data in specialties:
                specialty = HospitalSpecialty(
                    hospital_id=hospital.id,
                    **specialty_data
                )
                db.add(specialty)

def seed_news(db: Session):
    """ニュースデータを投入"""
    news_data = [
        {
            "title": "インフルエンザ予防接種について",
            "content": "今シーズンのインフルエンザ予防接種が開始されました。高齢者や妊婦の方は特に接種をお勧めします。",
            "summary": "インフルエンザ予防接種の開始について",
            "author": "医療ニュース編集部",
            "source": "健康情報サイト",
            "category": "予防",
            "published_date": datetime.utcnow(),
            "is_featured": True
        },
        {
            "title": "新型コロナウイルス感染対策の最新情報",
            "content": "マスク着用、手洗い、換気などの基本的な感染対策を継続することが重要です。",
            "summary": "COVID-19感染対策の継続について",
            "author": "感染症専門医",
            "source": "厚生労働省",
            "category": "感染症",
            "published_date": datetime.utcnow(),
            "is_featured": True
        },
        {
            "title": "健康的な食生活のススメ",
            "content": "バランスの取れた食事は、生活習慣病の予防に重要な役割を果たします。野菜を多く摂取し、塩分を控えめにしましょう。",
            "summary": "バランスの良い食事の重要性について",
            "author": "栄養士",
            "source": "栄養健康サイト",
            "category": "栄養",
            "published_date": datetime.utcnow(),
            "is_featured": False
        }
    ]
    
    for news_item in news_data:
        if not db.query(HealthNews).filter(HealthNews.title == news_item["title"]).first():
            news = HealthNews(**news_item)
            db.add(news)

def seed_alerts(db: Session):
    """ヘルスアラートデータを投入"""
    alerts_data = [
        {
            "title": "熱中症注意報",
            "message": "気温が高く、熱中症の危険性が高まっています。こまめな水分補給と涼しい場所での休憩を心がけてください。",
            "alert_type": "warning",
            "severity_level": 3,
            "start_date": datetime.utcnow(),
            "source_authority": "気象庁",
            "is_active": True
        }
    ]
    
    for alert_data in alerts_data:
        if not db.query(HealthAlert).filter(HealthAlert.title == alert_data["title"]).first():
            alert = HealthAlert(**alert_data)
            db.add(alert)

if __name__ == "__main__":
    seed_database()