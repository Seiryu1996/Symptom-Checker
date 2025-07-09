from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.hospital_scraper import HospitalScraper
from app.services.news_scraper import HealthNewsScraper
from typing import List, Dict
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class ScrapingResult(BaseModel):
    status: str
    message: str
    data: Dict
    timestamp: str

class HospitalScrapingRequest(BaseModel):
    prefectures: List[str] = ["東京都", "神奈川県", "埼玉県", "千葉県"]
    cities: List[str] = []

@router.post("/hospitals/scrape", response_model=ScrapingResult)
async def scrape_hospitals(
    request: HospitalScrapingRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    病院情報をスクレイピングするエンドポイント
    """
    try:
        scraper = HospitalScraper(db)
        
        # バックグラウンドタスクとして実行
        background_tasks.add_task(
            run_hospital_scraping_task,
            scraper,
            request.prefectures
        )
        
        return ScrapingResult(
            status="started",
            message="病院情報のスクレイピングを開始しました",
            data={"prefectures": request.prefectures},
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"スクレイピングの開始に失敗しました: {str(e)}"
        )

@router.post("/hospitals/scrape/immediate", response_model=ScrapingResult)
async def scrape_hospitals_immediate(
    request: HospitalScrapingRequest,
    db: Session = Depends(get_db)
):
    """
    病院情報を即座にスクレイピングするエンドポイント（テスト用）
    """
    try:
        scraper = HospitalScraper(db)
        
        # 最初の都道府県のみをテスト
        test_prefecture = request.prefectures[0] if request.prefectures else "東京都"
        
        # 少量のデータをスクレイピング
        hospitals_data = scraper.scrape_hospital_info(test_prefecture)
        saved_count = scraper.save_scraped_hospitals(hospitals_data[:5])  # 最初の5件のみ
        
        return ScrapingResult(
            status="completed",
            message=f"{test_prefecture}の病院情報をスクレイピングしました",
            data={
                "prefecture": test_prefecture,
                "scraped": len(hospitals_data),
                "saved": saved_count
            },
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"スクレイピングに失敗しました: {str(e)}"
        )

@router.post("/news/scrape", response_model=ScrapingResult)
async def scrape_health_news(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    健康ニュースをスクレイピングするエンドポイント
    """
    try:
        scraper = HealthNewsScraper(db)
        
        # バックグラウンドタスクとして実行
        background_tasks.add_task(run_news_scraping_task, scraper)
        
        return ScrapingResult(
            status="started",
            message="健康ニュースのスクレイピングを開始しました",
            data={},
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"スクレイピングの開始に失敗しました: {str(e)}"
        )

@router.post("/news/scrape/immediate", response_model=ScrapingResult)
async def scrape_health_news_immediate(db: Session = Depends(get_db)):
    """
    健康ニュースを即座にスクレイピングするエンドポイント（テスト用）
    """
    try:
        scraper = HealthNewsScraper(db)
        results = scraper.run_full_scraping()
        
        return ScrapingResult(
            status="completed",
            message="健康ニュースのスクレイピングが完了しました",
            data=results,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"スクレイピングに失敗しました: {str(e)}"
        )

@router.post("/all/scrape", response_model=ScrapingResult)
async def scrape_all_data(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    すべてのデータ（病院情報・健康ニュース）をスクレイピングするエンドポイント
    """
    try:
        hospital_scraper = HospitalScraper(db)
        news_scraper = HealthNewsScraper(db)
        
        # バックグラウンドタスクとして実行
        background_tasks.add_task(run_full_scraping_task, hospital_scraper, news_scraper)
        
        return ScrapingResult(
            status="started",
            message="全データのスクレイピングを開始しました",
            data={},
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"スクレイピングの開始に失敗しました: {str(e)}"
        )

@router.get("/status", response_model=Dict)
async def get_scraping_status(db: Session = Depends(get_db)):
    """
    スクレイピングの状態を確認するエンドポイント
    """
    try:
        # データベースから最新のスクレイピング結果を取得
        from app.models.hospital import Hospital
        from app.models.news import HealthNews, HealthAlert
        
        hospital_count = db.query(Hospital).count()
        news_count = db.query(HealthNews).count()
        alert_count = db.query(HealthAlert).count()
        
        # 最新のデータ取得日時
        latest_hospital = db.query(Hospital).order_by(Hospital.last_updated.desc()).first()
        latest_news = db.query(HealthNews).order_by(HealthNews.created_at.desc()).first()
        
        return {
            "hospitals": {
                "total": hospital_count,
                "last_updated": latest_hospital.last_updated.isoformat() if latest_hospital else None
            },
            "news": {
                "total": news_count,
                "last_updated": latest_news.created_at.isoformat() if latest_news else None
            },
            "alerts": {
                "total": alert_count
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"ステータス取得に失敗しました: {str(e)}"
        )

# バックグラウンドタスク関数
async def run_hospital_scraping_task(scraper: HospitalScraper, prefectures: List[str]):
    """病院スクレイピングをバックグラウンドで実行"""
    try:
        results = scraper.run_full_scraping(prefectures)
        print(f"Hospital scraping completed: {results}")
    except Exception as e:
        print(f"Hospital scraping failed: {e}")

async def run_news_scraping_task(scraper: HealthNewsScraper):
    """ニューススクレイピングをバックグラウンドで実行"""
    try:
        results = scraper.run_full_scraping()
        print(f"News scraping completed: {results}")
    except Exception as e:
        print(f"News scraping failed: {e}")

async def run_full_scraping_task(hospital_scraper: HospitalScraper, news_scraper: HealthNewsScraper):
    """全データスクレイピングをバックグラウンドで実行"""
    try:
        # 病院データのスクレイピング
        hospital_results = hospital_scraper.run_full_scraping()
        print(f"Hospital scraping completed: {hospital_results}")
        
        # ニュースデータのスクレイピング
        news_results = news_scraper.run_full_scraping()
        print(f"News scraping completed: {news_results}")
        
        print("All scraping tasks completed successfully")
        
    except Exception as e:
        print(f"Full scraping failed: {e}")