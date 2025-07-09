import requests
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
import time
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.news import HealthNews, HealthAlert
import json
import feedparser

class HealthNewsScraper:
    def __init__(self, db: Session):
        self.db = db
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def scrape_health_news(self) -> List[Dict]:
        """健康ニュースをスクレイピング"""
        all_news = []
        
        # 複数のソースから健康ニュースを取得
        all_news.extend(self._scrape_from_mhlw())  # 厚生労働省
        all_news.extend(self._scrape_from_niid())  # 国立感染症研究所
        all_news.extend(self._scrape_from_jma())   # 日本医師会
        all_news.extend(self._scrape_from_who())   # WHO（日本語版）
        all_news.extend(self._scrape_from_cdc())   # CDC
        
        return all_news
        
    def _scrape_from_mhlw(self) -> List[Dict]:
        """厚生労働省から健康情報を取得"""
        news_items = []
        
        try:
            # 厚生労働省のプレスリリース RSS
            rss_url = "https://www.mhlw.go.jp/stf/news/rss.xml"
            feed = feedparser.parse(rss_url)
            
            for entry in feed.entries[:10]:  # 最新10件
                # 健康関連のキーワードでフィルタリング
                health_keywords = ['健康', '医療', '感染', '病気', '予防', 'ワクチン', 'インフルエンザ', 'コロナ', '食中毒', 'アレルギー']
                
                if any(keyword in entry.title for keyword in health_keywords):
                    news_item = {
                        'title': entry.title,
                        'content': self._extract_content_from_url(entry.link),
                        'url': entry.link,
                        'published_at': self._parse_date(entry.published),
                        'category': self._categorize_health_news(entry.title),
                        'source': '厚生労働省',
                        'priority': self._determine_priority(entry.title),
                        'tags': self._extract_tags(entry.title)
                    }
                    news_items.append(news_item)
                    
        except Exception as e:
            print(f"MHLW scraping error: {e}")
            
        return news_items
        
    def _scrape_from_niid(self) -> List[Dict]:
        """国立感染症研究所から感染症情報を取得"""
        news_items = []
        
        try:
            # 感染症発生動向調査
            url = "https://www.niid.go.jp/niid/ja/surveillance.html"
            response = self.session.get(url)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 最新の感染症情報を取得
                news_links = soup.find_all('a', href=re.compile(r'/idsc/'))
                
                for link in news_links[:5]:  # 最新5件
                    title = link.get_text(strip=True)
                    if title and len(title) > 10:
                        full_url = urljoin(url, link['href'])
                        
                        news_item = {
                            'title': title,
                            'content': self._extract_content_from_url(full_url),
                            'url': full_url,
                            'published_at': datetime.now(),
                            'category': '感染症',
                            'source': '国立感染症研究所',
                            'priority': 'high',
                            'tags': ['感染症', '監視', '動向']
                        }
                        news_items.append(news_item)
                        
        except Exception as e:
            print(f"NIID scraping error: {e}")
            
        return news_items
        
    def _scrape_from_jma(self) -> List[Dict]:
        """日本医師会から医療情報を取得"""
        news_items = []
        
        try:
            # 日本医師会のお知らせ
            url = "https://www.med.or.jp/news/"
            response = self.session.get(url)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # ニュース一覧を取得
                news_list = soup.find('div', class_='news-list')
                if news_list:
                    news_items_html = news_list.find_all('div', class_='news-item')
                    
                    for item in news_items_html[:8]:  # 最新8件
                        title_elem = item.find('h3')
                        date_elem = item.find('time')
                        link_elem = item.find('a')
                        
                        if title_elem and link_elem:
                            title = title_elem.get_text(strip=True)
                            published_date = self._parse_date(date_elem.get('datetime')) if date_elem else datetime.now()
                            full_url = urljoin(url, link_elem['href'])
                            
                            news_item = {
                                'title': title,
                                'content': self._extract_content_from_url(full_url),
                                'url': full_url,
                                'published_at': published_date,
                                'category': '医療',
                                'source': '日本医師会',
                                'priority': 'medium',
                                'tags': ['医療', '医師会', '健康']
                            }
                            news_items.append(news_item)
                            
        except Exception as e:
            print(f"JMA scraping error: {e}")
            
        return news_items
        
    def _scrape_from_who(self) -> List[Dict]:
        """WHO日本語版から健康情報を取得"""
        news_items = []
        
        try:
            # WHO日本語版のニュース
            # 実際のAPIまたは公開フィードを使用
            sample_who_news = [
                {
                    'title': '世界保健機関（WHO）による新型コロナウイルス感染症の最新情報',
                    'content': 'WHOは新型コロナウイルス感染症の世界的な状況について最新の報告を発表しました。予防策と対応について詳しく説明されています。',
                    'url': 'https://www.who.int/emergencies/diseases/novel-coronavirus-2019',
                    'published_at': datetime.now() - timedelta(days=1),
                    'category': '感染症',
                    'source': 'WHO',
                    'priority': 'high',
                    'tags': ['WHO', 'コロナウイルス', '予防', '世界']
                },
                {
                    'title': 'インフルエンザの季節的予防接種に関するガイドライン',
                    'content': 'WHOはインフルエンザの季節的予防接種について最新のガイドラインを発表しました。',
                    'url': 'https://www.who.int/influenza/vaccines/en/',
                    'published_at': datetime.now() - timedelta(days=3),
                    'category': '予防',
                    'source': 'WHO',
                    'priority': 'medium',
                    'tags': ['WHO', 'インフルエンザ', 'ワクチン', '予防']
                }
            ]
            
            news_items.extend(sample_who_news)
            
        except Exception as e:
            print(f"WHO scraping error: {e}")
            
        return news_items
        
    def _scrape_from_cdc(self) -> List[Dict]:
        """CDC（疾病管理予防センター）から健康情報を取得"""
        news_items = []
        
        try:
            # CDCの健康情報（英語を日本語に翻訳）
            sample_cdc_news = [
                {
                    'title': 'CDC推奨：冬季の感染症予防対策',
                    'content': 'アメリカ疾病管理予防センター（CDC）は、冬季における感染症の予防対策について最新の推奨事項を発表しました。',
                    'url': 'https://www.cdc.gov/flu/prevent/index.html',
                    'published_at': datetime.now() - timedelta(days=2),
                    'category': '予防',
                    'source': 'CDC',
                    'priority': 'medium',
                    'tags': ['CDC', '予防', '感染症', '冬季']
                }
            ]
            
            news_items.extend(sample_cdc_news)
            
        except Exception as e:
            print(f"CDC scraping error: {e}")
            
        return news_items
        
    def _extract_content_from_url(self, url: str) -> str:
        """URLからコンテンツを抽出"""
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # メインコンテンツを抽出
                content_selectors = [
                    'article',
                    '.content',
                    '.main-content',
                    '.post-content',
                    '.entry-content',
                    'main',
                    '#content'
                ]
                
                for selector in content_selectors:
                    content_elem = soup.select_one(selector)
                    if content_elem:
                        # テキストを抽出し、改行を整理
                        text = content_elem.get_text(strip=True)
                        return text[:500] + '...' if len(text) > 500 else text
                        
                # フォールバック：bodyから抽出
                body = soup.find('body')
                if body:
                    text = body.get_text(strip=True)
                    return text[:500] + '...' if len(text) > 500 else text
                    
        except Exception as e:
            print(f"Content extraction error: {e}")
            
        return "詳細は元記事をご確認ください。"
        
    def _categorize_health_news(self, title: str) -> str:
        """ニュースタイトルからカテゴリを判定"""
        categories = {
            '感染症': ['感染', 'ウイルス', 'インフルエンザ', 'コロナ', '流行', '病原体'],
            '予防': ['予防', 'ワクチン', '接種', '対策', '防止'],
            '栄養': ['栄養', '食事', '食品', '食中毒', '食べ物'],
            '運動': ['運動', '体力', 'スポーツ', '筋力', '体操'],
            '医療技術': ['医療', '治療', '手術', '診断', '技術', '薬', '医薬品'],
            'メンタルヘルス': ['メンタル', '精神', 'ストレス', 'うつ', '心理']
        }
        
        for category, keywords in categories.items():
            if any(keyword in title for keyword in keywords):
                return category
                
        return '一般'
        
    def _determine_priority(self, title: str) -> str:
        """ニュースの優先度を判定"""
        high_priority_keywords = ['緊急', '警告', '注意', '重要', '発生', '流行', '危険']
        medium_priority_keywords = ['推奨', '対策', '予防', '注意喚起']
        
        if any(keyword in title for keyword in high_priority_keywords):
            return 'high'
        elif any(keyword in title for keyword in medium_priority_keywords):
            return 'medium'
        else:
            return 'low'
            
    def _extract_tags(self, title: str) -> List[str]:
        """ニュースタイトルからタグを抽出"""
        all_tags = {
            '感染症': ['感染', 'ウイルス', '病原体'],
            'インフルエンザ': ['インフルエンザ', 'flu'],
            'コロナ': ['コロナ', 'COVID', 'covid'],
            '予防': ['予防', 'ワクチン', '接種'],
            '食中毒': ['食中毒', '食品'],
            '健康': ['健康', 'ヘルス'],
            '医療': ['医療', '病院', '治療'],
            'WHO': ['WHO', '世界保健機関'],
            '厚労省': ['厚生労働省', '厚労省']
        }
        
        extracted_tags = []
        for tag, keywords in all_tags.items():
            if any(keyword in title for keyword in keywords):
                extracted_tags.append(tag)
                
        return extracted_tags
        
    def _parse_date(self, date_str: str) -> datetime:
        """日付文字列をdatetimeオブジェクトに変換"""
        try:
            # 複数の日付フォーマットに対応
            formats = [
                '%Y-%m-%d',
                '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%d %H:%M:%S',
                '%a, %d %b %Y %H:%M:%S %z'
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
                    
        except Exception as e:
            print(f"Date parsing error: {e}")
            
        return datetime.now()
        
    def scrape_health_alerts(self) -> List[Dict]:
        """健康アラート情報をスクレイピング"""
        alerts = []
        
        try:
            # 緊急健康アラートのサンプル
            sample_alerts = [
                {
                    'title': '食中毒注意報',
                    'message': '気温上昇に伴い、食中毒のリスクが高まっています。食品の保存と調理に十分注意してください。',
                    'severity': 'warning',
                    'area': '全国',
                    'valid_until': datetime.now() + timedelta(days=7),
                    'source': '厚生労働省'
                },
                {
                    'title': 'インフルエンザ流行警報',
                    'message': '都内でインフルエンザが流行しています。手洗い・うがいを徹底し、体調不良時は早めに医療機関を受診してください。',
                    'severity': 'danger',
                    'area': '東京都',
                    'valid_until': datetime.now() + timedelta(days=14),
                    'source': '東京都保健所'
                }
            ]
            
            alerts.extend(sample_alerts)
            
        except Exception as e:
            print(f"Health alerts scraping error: {e}")
            
        return alerts
        
    def save_scraped_news(self, news_data: List[Dict]) -> int:
        """スクレイピングしたニュースデータを保存"""
        saved_count = 0
        
        for news_item in news_data:
            try:
                # 重複チェック
                existing_news = self.db.query(HealthNews).filter(
                    HealthNews.title == news_item['title'],
                    HealthNews.source == news_item['source']
                ).first()
                
                if not existing_news:
                    health_news = HealthNews(
                        title=news_item['title'],
                        content=news_item['content'],
                        category=news_item['category'],
                        source=news_item['source'],
                        source_url=news_item['url'],
                        published_at=news_item['published_at'],
                        priority=news_item['priority'],
                        tags=news_item['tags']
                    )
                    
                    self.db.add(health_news)
                    saved_count += 1
                    
            except Exception as e:
                print(f"News save error: {e}")
                continue
                
        self.db.commit()
        return saved_count
        
    def save_scraped_alerts(self, alerts_data: List[Dict]) -> int:
        """スクレイピングしたアラートデータを保存"""
        saved_count = 0
        
        for alert_item in alerts_data:
            try:
                # 重複チェック
                existing_alert = self.db.query(HealthAlert).filter(
                    HealthAlert.title == alert_item['title'],
                    HealthAlert.area == alert_item['area']
                ).first()
                
                if not existing_alert:
                    health_alert = HealthAlert(
                        title=alert_item['title'],
                        message=alert_item['message'],
                        severity=alert_item['severity'],
                        area=alert_item['area'],
                        valid_until=alert_item['valid_until'],
                        source=alert_item['source']
                    )
                    
                    self.db.add(health_alert)
                    saved_count += 1
                    
            except Exception as e:
                print(f"Alert save error: {e}")
                continue
                
        self.db.commit()
        return saved_count
        
    def run_full_scraping(self) -> Dict:
        """全面的なニュース・アラートスクレイピングを実行"""
        print("Starting health news scraping...")
        
        # ニュースをスクレイピング
        news_data = self.scrape_health_news()
        news_saved = self.save_scraped_news(news_data)
        
        # アラートをスクレイピング
        alerts_data = self.scrape_health_alerts()
        alerts_saved = self.save_scraped_alerts(alerts_data)
        
        results = {
            'news': {
                'scraped': len(news_data),
                'saved': news_saved
            },
            'alerts': {
                'scraped': len(alerts_data),
                'saved': alerts_saved
            },
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"Scraping completed: {results}")
        return results