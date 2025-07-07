from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta

router = APIRouter()

class NewsItem(BaseModel):
    id: str
    title: str
    content: str
    category: str
    hospital_id: Optional[str] = None
    hospital_name: Optional[str] = None
    published_at: datetime
    priority: str  # "high", "medium", "low"
    tags: List[str]
    image_url: Optional[str] = None

class HealthAlert(BaseModel):
    id: str
    title: str
    message: str
    severity: str  # "info", "warning", "danger"
    area: Optional[str] = None
    valid_until: datetime
    action_required: bool

@router.get("/health-news", response_model=List[NewsItem])
async def get_health_news(
    category: Optional[str] = Query(None, description="ニュースカテゴリ"),
    limit: int = Query(10, description="取得件数")
):
    """
    健康情報・ニュースを取得するエンドポイント
    """
    try:
        # 実際の実装では、データベースから最新のニュースを取得
        # ここではサンプルデータを返す
        sample_news = [
            NewsItem(
                id="news_1",
                title="インフルエンザの流行状況について",
                content="今シーズンのインフルエンザが全国的に流行期に入りました。手洗い・うがいを徹底し、体調管理にお気をつけください。",
                category="感染症情報",
                hospital_id="hospital_1",
                hospital_name="市立総合病院",
                published_at=datetime.now() - timedelta(hours=2),
                priority="high",
                tags=["インフルエンザ", "予防", "感染症"],
                image_url="https://example.com/influenza-news.jpg"
            ),
            NewsItem(
                id="news_2",
                title="夏の熱中症対策について",
                content="気温が上昇する時期になりました。こまめな水分補給と適切な冷房の使用で、熱中症を予防しましょう。",
                category="季節の健康情報",
                published_at=datetime.now() - timedelta(days=1),
                priority="medium",
                tags=["熱中症", "予防", "夏", "水分補給"],
                image_url="https://example.com/heatstroke-prevention.jpg"
            ),
            NewsItem(
                id="news_3",
                title="新型コロナウイルス感染症の最新情報",
                content="新型コロナウイルスの感染状況と最新の対策についてお知らせします。マスクの着用や手指の消毒を継続してください。",
                category="感染症情報",
                published_at=datetime.now() - timedelta(days=2),
                priority="high",
                tags=["新型コロナ", "感染症", "予防", "マスク"],
                image_url="https://example.com/covid-news.jpg"
            ),
            NewsItem(
                id="news_4",
                title="健康診断の重要性について",
                content="年1回の健康診断で、生活習慣病の早期発見・早期治療を心がけましょう。定期的な検診が健康維持の鍵です。",
                category="健康管理",
                hospital_id="hospital_2",
                hospital_name="田中クリニック",
                published_at=datetime.now() - timedelta(days=3),
                priority="medium",
                tags=["健康診断", "生活習慣病", "予防"],
                image_url="https://example.com/health-checkup.jpg"
            ),
            NewsItem(
                id="news_5",
                title="花粉症対策のポイント",
                content="スギ花粉の飛散が始まっています。外出時のマスク着用、帰宅時の衣類や髪の花粉の除去を心がけましょう。",
                category="季節の健康情報",
                published_at=datetime.now() - timedelta(days=5),
                priority="medium",
                tags=["花粉症", "アレルギー", "予防", "春"],
                image_url="https://example.com/pollen-allergy.jpg"
            )
        ]
        
        # カテゴリでフィルタリング
        if category:
            sample_news = [news for news in sample_news if news.category == category]
        
        # 件数制限
        sample_news = sample_news[:limit]
        
        return sample_news
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ニュース取得中にエラーが発生しました: {str(e)}")

@router.get("/health-alerts", response_model=List[HealthAlert])
async def get_health_alerts(
    area: Optional[str] = Query(None, description="地域"),
    severity: Optional[str] = Query(None, description="重要度")
):
    """
    健康アラート・緊急情報を取得するエンドポイント
    """
    try:
        # 実際の実装では、データベースから現在有効なアラートを取得
        sample_alerts = [
            HealthAlert(
                id="alert_1",
                title="インフルエンザ流行警報",
                message="インフルエンザの感染者数が警報レベルに達しました。予防対策を徹底してください。",
                severity="warning",
                area="東京都",
                valid_until=datetime.now() + timedelta(days=14),
                action_required=True
            ),
            HealthAlert(
                id="alert_2",
                title="熱中症注意報",
                message="気温が35度を超える予報です。外出時は十分な水分補給と休憩を取ってください。",
                severity="warning",
                area="全国",
                valid_until=datetime.now() + timedelta(days=3),
                action_required=True
            ),
            HealthAlert(
                id="alert_3",
                title="花粉飛散情報",
                message="スギ花粉の飛散量が「非常に多い」予報です。花粉症の方は対策をお忘れなく。",
                severity="info",
                area="関東地方",
                valid_until=datetime.now() + timedelta(days=1),
                action_required=False
            )
        ]
        
        # 有効期限内のアラートのみを返す
        current_time = datetime.now()
        valid_alerts = [alert for alert in sample_alerts if alert.valid_until > current_time]
        
        # 地域でフィルタリング
        if area:
            valid_alerts = [alert for alert in valid_alerts if alert.area == area or alert.area == "全国"]
        
        # 重要度でフィルタリング
        if severity:
            valid_alerts = [alert for alert in valid_alerts if alert.severity == severity]
        
        # 重要度順でソート
        severity_order = {"danger": 0, "warning": 1, "info": 2}
        valid_alerts.sort(key=lambda x: severity_order.get(x.severity, 3))
        
        return valid_alerts
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"アラート取得中にエラーが発生しました: {str(e)}")

@router.get("/hospital-news/{hospital_id}", response_model=List[NewsItem])
async def get_hospital_news(
    hospital_id: str,
    limit: int = Query(5, description="取得件数")
):
    """
    特定の病院からのお知らせを取得するエンドポイント
    """
    try:
        # 実際の実装では、指定された病院のニュースを取得
        sample_hospital_news = [
            NewsItem(
                id="hospital_news_1",
                title="年末年始の診療時間変更のお知らせ",
                content="12月29日から1月3日まで休診とさせていただきます。緊急時は救急外来をご利用ください。",
                category="診療案内",
                hospital_id=hospital_id,
                hospital_name="市立総合病院",
                published_at=datetime.now() - timedelta(hours=6),
                priority="high",
                tags=["休診", "年末年始", "診療時間"]
            ),
            NewsItem(
                id="hospital_news_2",
                title="新しい診療科開設のお知らせ",
                content="4月より心療内科を新設いたします。ストレスや心の不調についてもお気軽にご相談ください。",
                category="新サービス",
                hospital_id=hospital_id,
                hospital_name="市立総合病院",
                published_at=datetime.now() - timedelta(days=2),
                priority="medium",
                tags=["新診療科", "心療内科", "メンタルヘルス"]
            ),
            NewsItem(
                id="hospital_news_3",
                title="インフルエンザ予防接種のご案内",
                content="インフルエンザ予防接種を実施しています。事前にお電話でご予約ください。",
                category="予防接種",
                hospital_id=hospital_id,
                hospital_name="市立総合病院",
                published_at=datetime.now() - timedelta(days=7),
                priority="medium",
                tags=["予防接種", "インフルエンザ", "予約"]
            )
        ]
        
        # 件数制限
        sample_hospital_news = sample_hospital_news[:limit]
        
        return sample_hospital_news
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"病院ニュース取得中にエラーが発生しました: {str(e)}")

@router.get("/categories")
async def get_news_categories():
    """
    ニュースカテゴリ一覧を取得するエンドポイント
    """
    categories = [
        {"id": "infection", "name": "感染症情報", "icon": "🦠"},
        {"id": "seasonal", "name": "季節の健康情報", "icon": "🌸"},
        {"id": "prevention", "name": "予防・健康管理", "icon": "💊"},
        {"id": "emergency", "name": "緊急情報", "icon": "🚨"},
        {"id": "hospital", "name": "病院からのお知らせ", "icon": "🏥"},
        {"id": "research", "name": "医療研究・新薬情報", "icon": "🔬"},
        {"id": "lifestyle", "name": "生活習慣病", "icon": "❤️"},
        {"id": "mental", "name": "メンタルヘルス", "icon": "🧠"},
    ]
    
    return {"categories": categories}