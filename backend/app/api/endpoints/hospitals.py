from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel

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
async def search_hospitals(search_params: HospitalSearchParams):
    """
    病院を検索するエンドポイント
    診療科、位置情報、距離などで絞り込み
    """
    try:
        # 実際の実装では、病院データベースから検索
        # ここではサンプルデータを返す
        sample_hospitals = [
            Hospital(
                id="hospital_1",
                name="市立総合病院",
                location=Location(
                    latitude=35.6762,
                    longitude=139.6503,
                    address="東京都渋谷区"
                ),
                phone="03-1234-5678",
                specialties=["内科", "外科", "小児科", "整形外科"],
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
                rating=4.2,
                website="https://hospital1.example.com",
                emergency=True
            ),
            Hospital(
                id="hospital_2",
                name="田中クリニック",
                location=Location(
                    latitude=35.6754,
                    longitude=139.6492,
                    address="東京都渋谷区"
                ),
                phone="03-2345-6789",
                specialties=["内科", "皮膚科"],
                hours=[
                    HospitalHours(day="月", open_time="09:00", close_time="18:00"),
                    HospitalHours(day="火", open_time="09:00", close_time="18:00"),
                    HospitalHours(day="水", open_time="09:00", close_time="18:00"),
                    HospitalHours(day="木", open_time="09:00", close_time="18:00"),
                    HospitalHours(day="金", open_time="09:00", close_time="18:00"),
                    HospitalHours(day="土", open_time="09:00", close_time="13:00"),
                    HospitalHours(day="日", open_time="", close_time="", is_closed=True),
                ],
                distance=0.8,
                rating=4.5,
                website="https://tanaka-clinic.example.com",
                emergency=False
            ),
            Hospital(
                id="hospital_3",
                name="専門整形外科病院",
                location=Location(
                    latitude=35.6745,
                    longitude=139.6515,
                    address="東京都渋谷区"
                ),
                phone="03-3456-7890",
                specialties=["整形外科", "リハビリテーション科"],
                hours=[
                    HospitalHours(day="月", open_time="08:30", close_time="17:30"),
                    HospitalHours(day="火", open_time="08:30", close_time="17:30"),
                    HospitalHours(day="水", open_time="08:30", close_time="17:30"),
                    HospitalHours(day="木", open_time="08:30", close_time="17:30"),
                    HospitalHours(day="金", open_time="08:30", close_time="17:30"),
                    HospitalHours(day="土", open_time="08:30", close_time="12:30"),
                    HospitalHours(day="日", open_time="", close_time="", is_closed=True),
                ],
                distance=1.5,
                rating=4.0,
                website="https://orthopedic-hospital.example.com",
                emergency=False
            ),
        ]
        
        # 診療科でフィルタリング
        filtered_hospitals = []
        for hospital in sample_hospitals:
            if any(specialty in hospital.specialties for specialty in search_params.specialties):
                filtered_hospitals.append(hospital)
        
        # 緊急対応のみでフィルタリング
        if search_params.emergency_only:
            filtered_hospitals = [h for h in filtered_hospitals if h.emergency]
        
        # 距離でフィルタリング
        if search_params.max_distance:
            filtered_hospitals = [h for h in filtered_hospitals if h.distance and h.distance <= search_params.max_distance]
        
        # 距離順でソート
        filtered_hospitals.sort(key=lambda x: x.distance or float('inf'))
        
        return filtered_hospitals
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"病院検索中にエラーが発生しました: {str(e)}")

@router.get("/nearby", response_model=List[Hospital])
async def get_nearby_hospitals(
    latitude: float = Query(..., description="緯度"),
    longitude: float = Query(..., description="経度"),
    radius: float = Query(5.0, description="検索半径(km)"),
    specialty: Optional[str] = Query(None, description="診療科")
):
    """
    現在地周辺の病院を取得するエンドポイント
    """
    try:
        # 実際の実装では、位置情報を使って近くの病院を検索
        # ここではサンプルデータを返す
        nearby_hospitals = [
            Hospital(
                id="nearby_1",
                name="近くの病院1",
                location=Location(
                    latitude=latitude + 0.001,
                    longitude=longitude + 0.001,
                    address="最寄りの住所1"
                ),
                phone="03-1111-2222",
                specialties=["内科", "外科"],
                hours=[
                    HospitalHours(day="月", open_time="09:00", close_time="17:00"),
                    HospitalHours(day="火", open_time="09:00", close_time="17:00"),
                    HospitalHours(day="水", open_time="09:00", close_time="17:00"),
                    HospitalHours(day="木", open_time="09:00", close_time="17:00"),
                    HospitalHours(day="金", open_time="09:00", close_time="17:00"),
                    HospitalHours(day="土", open_time="09:00", close_time="12:00"),
                    HospitalHours(day="日", open_time="", close_time="", is_closed=True),
                ],
                distance=0.5,
                rating=4.3,
                emergency=True
            ),
        ]
        
        # 診療科でフィルタリング
        if specialty:
            nearby_hospitals = [h for h in nearby_hospitals if specialty in h.specialties]
        
        return nearby_hospitals
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"周辺病院検索中にエラーが発生しました: {str(e)}")

@router.get("/{hospital_id}", response_model=Hospital)
async def get_hospital_details(hospital_id: str):
    """
    病院の詳細情報を取得するエンドポイント
    """
    try:
        # 実際の実装では、データベースから特定の病院を検索
        # ここではサンプルデータを返す
        if hospital_id == "hospital_1":
            return Hospital(
                id="hospital_1",
                name="市立総合病院",
                location=Location(
                    latitude=35.6762,
                    longitude=139.6503,
                    address="東京都渋谷区渋谷1-2-3"
                ),
                phone="03-1234-5678",
                specialties=["内科", "外科", "小児科", "整形外科", "神経内科"],
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
                rating=4.2,
                website="https://hospital1.example.com",
                emergency=True
            )
        else:
            raise HTTPException(status_code=404, detail="病院が見つかりません")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"病院詳細取得中にエラーが発生しました: {str(e)}")