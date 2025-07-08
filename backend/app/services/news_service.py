from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from app.models.news import HealthNews, HealthAlert

class NewsService:
    def __init__(self, db: Session):
        self.db = db

    def get_health_news(self, category: Optional[str] = None, 
                       featured_only: bool = False, limit: int = 20) -> List[HealthNews]:
        """健康ニュースを取得"""
        query = self.db.query(HealthNews).filter(HealthNews.is_published == True)
        
        if category:
            query = query.filter(HealthNews.category == category)
        
        if featured_only:
            query = query.filter(HealthNews.is_featured == True)
        
        return query.order_by(desc(HealthNews.published_date)).limit(limit).all()

    def get_news_by_id(self, news_id: int) -> Optional[HealthNews]:
        """特定のニュースを取得"""
        news = self.db.query(HealthNews).filter(
            HealthNews.id == news_id,
            HealthNews.is_published == True
        ).first()
        
        if news:
            # 閲覧数をインクリメント
            news.view_count += 1
            self.db.commit()
        
        return news

    def get_health_alerts(self, active_only: bool = True) -> List[HealthAlert]:
        """健康アラートを取得"""
        query = self.db.query(HealthAlert).filter(HealthAlert.is_public == True)
        
        if active_only:
            now = datetime.utcnow()
            query = query.filter(
                HealthAlert.is_active == True,
                HealthAlert.start_date <= now
            ).filter(
                (HealthAlert.end_date.is_(None)) | 
                (HealthAlert.end_date >= now)
            )
        
        return query.order_by(desc(HealthAlert.severity_level), 
                            desc(HealthAlert.start_date)).all()

    def get_hospital_news(self, hospital_id: int, limit: int = 10) -> List[HealthNews]:
        """特定の病院に関連するニュースを取得"""
        # 簡略化実装：病院名でニュースを検索
        return self.db.query(HealthNews).filter(
            HealthNews.is_published == True,
            HealthNews.content.ilike(f"%hospital_id_{hospital_id}%")
        ).order_by(desc(HealthNews.published_date)).limit(limit).all()

    def search_news(self, query: str, limit: int = 20) -> List[HealthNews]:
        """ニュースを検索"""
        return self.db.query(HealthNews).filter(
            HealthNews.is_published == True,
            (HealthNews.title.ilike(f"%{query}%") | 
             HealthNews.content.ilike(f"%{query}%"))
        ).order_by(desc(HealthNews.published_date)).limit(limit).all()

    def get_news_categories(self) -> List[str]:
        """ニュースカテゴリ一覧を取得"""
        categories = self.db.query(HealthNews.category).filter(
            HealthNews.is_published == True
        ).distinct().all()
        return [category[0] for category in categories if category[0]]

    def create_news(self, news_data: dict) -> HealthNews:
        """新しいニュースを作成（管理者用）"""
        news = HealthNews(
            title=news_data["title"],
            content=news_data["content"],
            summary=news_data.get("summary"),
            author=news_data.get("author"),
            source=news_data.get("source"),
            source_url=news_data.get("source_url"),
            image_url=news_data.get("image_url"),
            category=news_data["category"],
            tags=news_data.get("tags"),
            published_date=news_data.get("published_date", datetime.utcnow()),
            is_featured=news_data.get("is_featured", False)
        )
        
        self.db.add(news)
        self.db.commit()
        self.db.refresh(news)
        return news

    def create_health_alert(self, alert_data: dict) -> HealthAlert:
        """新しい健康アラートを作成（管理者用）"""
        alert = HealthAlert(
            title=alert_data["title"],
            message=alert_data["message"],
            alert_type=alert_data["alert_type"],
            severity_level=alert_data.get("severity_level", 1),
            affected_areas=alert_data.get("affected_areas"),
            start_date=alert_data.get("start_date", datetime.utcnow()),
            end_date=alert_data.get("end_date"),
            source_authority=alert_data["source_authority"],
            source_url=alert_data.get("source_url")
        )
        
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        return alert

    def get_trending_news(self, days: int = 7, limit: int = 10) -> List[HealthNews]:
        """トレンドニュースを取得（閲覧数ベース）"""
        since_date = datetime.utcnow() - timedelta(days=days)
        
        return self.db.query(HealthNews).filter(
            HealthNews.is_published == True,
            HealthNews.published_date >= since_date
        ).order_by(desc(HealthNews.view_count)).limit(limit).all()

    def get_emergency_alerts(self) -> List[HealthAlert]:
        """緊急アラートを取得"""
        return self.db.query(HealthAlert).filter(
            HealthAlert.is_active == True,
            HealthAlert.is_public == True,
            HealthAlert.alert_type == "emergency",
            HealthAlert.start_date <= datetime.utcnow()
        ).filter(
            (HealthAlert.end_date.is_(None)) | 
            (HealthAlert.end_date >= datetime.utcnow())
        ).order_by(desc(HealthAlert.severity_level)).all()