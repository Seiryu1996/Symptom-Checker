from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status
import math
from datetime import datetime, time
from app.models.hospital import Hospital, HospitalSpecialty

class HospitalService:
    def __init__(self, db: Session):
        self.db = db

    def search_hospitals(self, query: str, specialty: Optional[str] = None, 
                        limit: int = 20) -> List[Hospital]:
        """病院を検索"""
        hospital_query = self.db.query(Hospital).filter(Hospital.is_active == True)
        
        # テキスト検索
        if query:
            hospital_query = hospital_query.filter(
                Hospital.name.ilike(f"%{query}%")
            )
        
        # 診療科フィルター
        if specialty:
            hospital_query = hospital_query.join(HospitalSpecialty).filter(
                HospitalSpecialty.specialty_name.ilike(f"%{specialty}%"),
                HospitalSpecialty.is_available == True
            )
        
        return hospital_query.limit(limit).all()

    def get_nearby_hospitals(self, latitude: float, longitude: float, 
                           distance_km: float = 10, specialty: Optional[str] = None,
                           emergency_only: bool = False, limit: int = 20) -> List[dict]:
        """近くの病院を取得"""
        hospitals = self.db.query(Hospital).filter(
            Hospital.is_active == True,
            Hospital.latitude.isnot(None),
            Hospital.longitude.isnot(None)
        )
        
        # 救急対応フィルター
        if emergency_only:
            hospitals = hospitals.filter(Hospital.emergency_services == True)
        
        # 診療科フィルター
        if specialty:
            hospitals = hospitals.join(HospitalSpecialty).filter(
                HospitalSpecialty.specialty_name.ilike(f"%{specialty}%"),
                HospitalSpecialty.is_available == True
            )
        
        all_hospitals = hospitals.all()
        
        # 距離計算とフィルタリング
        nearby_hospitals = []
        for hospital in all_hospitals:
            distance = self._calculate_distance(
                latitude, longitude, hospital.latitude, hospital.longitude
            )
            
            if distance <= distance_km:
                hospital_data = {
                    "id": hospital.id,
                    "name": hospital.name,
                    "address": hospital.address,
                    "phone_number": hospital.phone_number,
                    "distance": round(distance, 2),
                    "rating": hospital.rating,
                    "total_reviews": hospital.total_reviews,
                    "emergency_services": hospital.emergency_services,
                    "is_open": self._is_hospital_open(hospital),
                    "specialties": [
                        {"name": spec.specialty_name, "wait_time": spec.wait_time_avg}
                        for spec in hospital.specialties if spec.is_available
                    ]
                }
                nearby_hospitals.append(hospital_data)
        
        # 距離順でソート
        nearby_hospitals.sort(key=lambda x: x["distance"])
        return nearby_hospitals[:limit]

    def get_hospital_detail(self, hospital_id: int) -> Optional[Hospital]:
        """病院詳細情報を取得"""
        hospital = self.db.query(Hospital).filter(
            Hospital.id == hospital_id,
            Hospital.is_active == True
        ).first()
        
        if hospital:
            # 営業時間情報を追加
            hospital.is_open_now = self._is_hospital_open(hospital)
            hospital.today_hours = self._get_today_hours(hospital)
            hospital.next_open = self._get_next_open_time(hospital)
        
        return hospital

    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """2点間の距離を計算（ハーバサイン公式）"""
        R = 6371  # 地球の半径（km）
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat / 2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c

    def _is_hospital_open(self, hospital: Hospital) -> bool:
        """病院が現在営業中かチェック"""
        now = datetime.now()
        current_time = now.time()
        weekday = now.weekday()  # 0=月曜日, 6=日曜日
        
        # 曜日に応じた営業時間を取得
        open_time, close_time = self._get_hospital_hours_for_day(hospital, weekday)
        
        if open_time and close_time:
            return open_time <= current_time <= close_time
        
        return False

    def _get_hospital_hours_for_day(self, hospital: Hospital, weekday: int) -> tuple:
        """指定された曜日の営業時間を取得"""
        hours_map = {
            0: (hospital.monday_open, hospital.monday_close),
            1: (hospital.tuesday_open, hospital.tuesday_close),
            2: (hospital.wednesday_open, hospital.wednesday_close),
            3: (hospital.thursday_open, hospital.thursday_close),
            4: (hospital.friday_open, hospital.friday_close),
            5: (hospital.saturday_open, hospital.saturday_close),
            6: (hospital.sunday_open, hospital.sunday_close),
        }
        return hours_map.get(weekday, (None, None))

    def _get_today_hours(self, hospital: Hospital) -> Optional[str]:
        """今日の営業時間を取得"""
        today = datetime.now().weekday()
        open_time, close_time = self._get_hospital_hours_for_day(hospital, today)
        
        if open_time and close_time:
            return f"{open_time.strftime('%H:%M')} - {close_time.strftime('%H:%M')}"
        
        return "営業時間情報なし"

    def _get_next_open_time(self, hospital: Hospital) -> Optional[str]:
        """次回営業開始時間を取得"""
        if self._is_hospital_open(hospital):
            return None
        
        # 簡略化実装：翌日の営業時間を返す
        tomorrow = (datetime.now().weekday() + 1) % 7
        open_time, close_time = self._get_hospital_hours_for_day(hospital, tomorrow)
        
        if open_time:
            days = ["月", "火", "水", "木", "金", "土", "日"]
            return f"{days[tomorrow]}曜日 {open_time.strftime('%H:%M')}から"
        
        return "営業時間情報なし"

    def create_hospital(self, hospital_data: dict) -> Hospital:
        """新しい病院を作成（管理者用）"""
        hospital = Hospital(
            name=hospital_data["name"],
            description=hospital_data.get("description"),
            address=hospital_data["address"],
            phone_number=hospital_data["phone_number"],
            email=hospital_data.get("email"),
            website=hospital_data.get("website"),
            latitude=hospital_data.get("latitude"),
            longitude=hospital_data.get("longitude"),
            emergency_services=hospital_data.get("emergency_services", False),
            accepts_insurance=hospital_data.get("accepts_insurance", True),
            parking_available=hospital_data.get("parking_available", True),
            wheelchair_accessible=hospital_data.get("wheelchair_accessible", True)
        )
        
        self.db.add(hospital)
        self.db.commit()
        self.db.refresh(hospital)
        return hospital

    def add_hospital_specialty(self, hospital_id: int, specialty_data: dict) -> HospitalSpecialty:
        """病院に診療科を追加"""
        specialty = HospitalSpecialty(
            hospital_id=hospital_id,
            specialty_name=specialty_data["specialty_name"],
            description=specialty_data.get("description"),
            department_phone=specialty_data.get("department_phone"),
            wait_time_avg=specialty_data.get("wait_time_avg")
        )
        
        self.db.add(specialty)
        self.db.commit()
        self.db.refresh(specialty)
        return specialty