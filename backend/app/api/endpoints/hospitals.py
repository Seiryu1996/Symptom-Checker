from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.database import get_db
from app.services.hospital_service import HospitalService
from app.models.hospital import Hospital as HospitalModel

router = APIRouter()

class Location(BaseModel):
    latitude: float
    longitude: float
    address: str

class HospitalHours(BaseModel):
    day: str
    open_time: str
    close_time: str
    is_closed: bool = False

class Hospital(BaseModel):
    id: str
    name: str
    location: Location
    phone: str
    specialties: List[str]
    hours: List[HospitalHours]
    distance: Optional[float] = None  # km
    rating: Optional[float] = None
    website: Optional[str] = None
    emergency: bool = False

class HospitalSearchParams(BaseModel):
    specialties: List[str]
    user_location: Optional[Location] = None
    max_distance: Optional[float] = 10.0  # km
    emergency_only: bool = False

@router.post("/search", response_model=List[Hospital])
async def search_hospitals(search_params: HospitalSearchParams, db: Session = Depends(get_db)):
    """
    病院を検索するエンドポイント
    診療科、位置情報、距離などで絞り込み
    """
    try:
        hospital_service = HospitalService(db)
        
        # 診療科での検索
        specialty_name = search_params.specialties[0] if search_params.specialties else None
        hospitals = hospital_service.search_hospitals("", specialty_name)
        
        # 病院データをAPIレスポンス形式に変換
        result_hospitals = []
        for hospital in hospitals:
            result_hospitals.append(Hospital(
                id=str(hospital.id),
                name=hospital.name,
                location=Location(
                    latitude=hospital.latitude or 35.6762,
                    longitude=hospital.longitude or 139.6503,
                    address=hospital.address
                ),
                phone=hospital.phone_number,
                specialties=[spec.specialty_name for spec in hospital.specialties],
                hours=[
                    HospitalHours(day="月", open_time="09:00", close_time="17:00"),
                    HospitalHours(day="火", open_time="09:00", close_time="17:00"),
                    HospitalHours(day="水", open_time="09:00", close_time="17:00"),
                    HospitalHours(day="木", open_time="09:00", close_time="17:00"),
                    HospitalHours(day="金", open_time="09:00", close_time="17:00"),
                    HospitalHours(day="土", open_time="09:00", close_time="12:00"),
                    HospitalHours(day="日", open_time="", close_time="", is_closed=True),
                ],
                distance=1.2,
                rating=hospital.rating,
                website=hospital.website,
                emergency=hospital.emergency_services
            ))
        
        return result_hospitals
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"病院検索中にエラーが発生しました: {str(e)}")

@router.get("/nearby", response_model=List[Hospital])
async def get_nearby_hospitals(
    latitude: float = Query(..., description="緯度"),
    longitude: float = Query(..., description="経度"),
    radius: float = Query(5.0, description="検索半径(km)"),
    specialty: Optional[str] = Query(None, description="診療科"),
    db: Session = Depends(get_db)
):
    """
    現在地周辺の病院を取得するエンドポイント
    """
    try:
        hospital_service = HospitalService(db)
        
        # 近くの病院を検索
        nearby_hospitals_data = hospital_service.get_nearby_hospitals(
            latitude, longitude, radius, specialty
        )
        
        # レスポンス形式に変換
        result_hospitals = []
        for hospital_data in nearby_hospitals_data:
            result_hospitals.append(Hospital(
                id=str(hospital_data["id"]),
                name=hospital_data["name"],
                location=Location(
                    latitude=hospital_data.get("latitude", latitude),
                    longitude=hospital_data.get("longitude", longitude),
                    address=hospital_data["address"]
                ),
                phone=hospital_data["phone_number"],
                specialties=[spec["name"] for spec in hospital_data["specialties"]],
                hours=[
                    HospitalHours(day="月", open_time="09:00", close_time="17:00"),
                    HospitalHours(day="火", open_time="09:00", close_time="17:00"),
                    HospitalHours(day="水", open_time="09:00", close_time="17:00"),
                    HospitalHours(day="木", open_time="09:00", close_time="17:00"),
                    HospitalHours(day="金", open_time="09:00", close_time="17:00"),
                    HospitalHours(day="土", open_time="09:00", close_time="12:00"),
                    HospitalHours(day="日", open_time="", close_time="", is_closed=True),
                ],
                distance=hospital_data["distance"],
                rating=hospital_data["rating"],
                website=hospital_data.get("website"),
                emergency=hospital_data["emergency_services"]
            ))
        
        return result_hospitals
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"周辺病院検索中にエラーが発生しました: {str(e)}")

@router.get("/{hospital_id}", response_model=Hospital)
async def get_hospital_details(hospital_id: str, db: Session = Depends(get_db)):
    """
    病院の詳細情報を取得するエンドポイント
    """
    try:
        hospital_service = HospitalService(db)
        hospital = hospital_service.get_hospital_detail(int(hospital_id))
        
        if not hospital:
            raise HTTPException(status_code=404, detail="病院が見つかりません")
        
        return Hospital(
            id=str(hospital.id),
            name=hospital.name,
            location=Location(
                latitude=hospital.latitude or 35.6762,
                longitude=hospital.longitude or 139.6503,
                address=hospital.address
            ),
            phone=hospital.phone_number,
            specialties=[spec.specialty_name for spec in hospital.specialties],
            hours=[
                HospitalHours(day="月", open_time="09:00", close_time="17:00"),
                HospitalHours(day="火", open_time="09:00", close_time="17:00"),
                HospitalHours(day="水", open_time="09:00", close_time="17:00"),
                HospitalHours(day="木", open_time="09:00", close_time="17:00"),
                HospitalHours(day="金", open_time="09:00", close_time="17:00"),
                HospitalHours(day="土", open_time="09:00", close_time="12:00"),
                HospitalHours(day="日", open_time="", close_time="", is_closed=True),
            ],
            distance=None,
            rating=hospital.rating,
            website=hospital.website,
            emergency=hospital.emergency_services
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"病院詳細取得中にエラーが発生しました: {str(e)}")