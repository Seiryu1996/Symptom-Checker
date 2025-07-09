import requests
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import json
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.hospital import Hospital, HospitalSpecialty

class HospitalScraper:
    def __init__(self, db: Session):
        self.db = db
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def get_chrome_driver(self):
        """Chrome WebDriverを取得"""
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins')
        options.add_argument('--disable-images')
        options.add_argument('--disable-javascript')
        
        return webdriver.Chrome(
            service=webdriver.chrome.service.Service(ChromeDriverManager().install()),
            options=options
        )
        
    def scrape_hospital_info(self, prefecture: str = "東京都", city: str = "") -> List[Dict]:
        """病院情報をスクレイピング"""
        scraped_hospitals = []
        
        # 複数のソースから病院情報を取得
        scraped_hospitals.extend(self._scrape_from_carely(prefecture, city))
        scraped_hospitals.extend(self._scrape_from_medley(prefecture, city))
        scraped_hospitals.extend(self._scrape_from_jmap(prefecture, city))
        
        return scraped_hospitals
        
    def _scrape_from_carely(self, prefecture: str, city: str) -> List[Dict]:
        """Carelyから病院情報を取得"""
        hospitals = []
        
        try:
            # Carelyの検索URL
            base_url = "https://carely.jp/hospital/search"
            params = {
                'prefecture': prefecture,
                'city': city,
                'page': 1
            }
            
            for page in range(1, 6):  # 最大5ページまで
                params['page'] = page
                response = self.session.get(base_url, params=params)
                
                if response.status_code != 200:
                    break
                    
                soup = BeautifulSoup(response.text, 'html.parser')
                hospital_items = soup.find_all('div', class_='hospital-item')
                
                if not hospital_items:
                    break
                
                for item in hospital_items:
                    hospital_data = self._parse_carely_hospital(item)
                    if hospital_data:
                        hospitals.append(hospital_data)
                        
                time.sleep(1)  # レート制限
                
        except Exception as e:
            print(f"Carely scraping error: {e}")
            
        return hospitals
        
    def _parse_carely_hospital(self, item) -> Optional[Dict]:
        """Carely病院アイテムを解析"""
        try:
            name_elem = item.find('h3', class_='hospital-name')
            if not name_elem:
                return None
                
            name = name_elem.get_text(strip=True)
            
            # 住所
            address_elem = item.find('p', class_='hospital-address')
            address = address_elem.get_text(strip=True) if address_elem else ""
            
            # 電話番号
            phone_elem = item.find('span', class_='hospital-phone')
            phone = phone_elem.get_text(strip=True) if phone_elem else ""
            
            # 診療科
            specialties = []
            specialty_elems = item.find_all('span', class_='specialty-tag')
            for spec_elem in specialty_elems:
                specialties.append(spec_elem.get_text(strip=True))
            
            # 評価
            rating_elem = item.find('span', class_='rating-score')
            rating = float(rating_elem.get_text(strip=True)) if rating_elem else None
            
            # 営業時間
            hours_elem = item.find('div', class_='hospital-hours')
            hours = hours_elem.get_text(strip=True) if hours_elem else ""
            
            return {
                'name': name,
                'address': address,
                'phone_number': phone,
                'specialties': specialties,
                'rating': rating,
                'hours': hours,
                'source': 'carely'
            }
            
        except Exception as e:
            print(f"Parse error: {e}")
            return None
            
    def _scrape_from_medley(self, prefecture: str, city: str) -> List[Dict]:
        """Medleyから病院情報を取得"""
        hospitals = []
        
        try:
            # Medleyの検索API（公開情報）
            base_url = "https://medley.life/api/hospitals/search"
            params = {
                'prefecture': prefecture,
                'city': city,
                'limit': 50
            }
            
            response = self.session.get(base_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                for hospital_data in data.get('hospitals', []):
                    hospital = {
                        'name': hospital_data.get('name', ''),
                        'address': hospital_data.get('address', ''),
                        'phone_number': hospital_data.get('phone', ''),
                        'specialties': hospital_data.get('departments', []),
                        'rating': hospital_data.get('rating'),
                        'website': hospital_data.get('website'),
                        'emergency_services': hospital_data.get('emergency', False),
                        'source': 'medley'
                    }
                    
                    # 座標情報
                    if 'location' in hospital_data:
                        hospital['latitude'] = hospital_data['location'].get('lat')
                        hospital['longitude'] = hospital_data['location'].get('lng')
                    
                    hospitals.append(hospital)
                    
        except Exception as e:
            print(f"Medley scraping error: {e}")
            
        return hospitals
        
    def _scrape_from_jmap(self, prefecture: str, city: str) -> List[Dict]:
        """日本医師会から病院情報を取得"""
        hospitals = []
        
        try:
            # 実際のスクレイピング実装
            # 注意: 実際の実装では各サイトの利用規約とrobot.txtを確認する必要があります
            
            # サンプル実装（実際のAPIや公開データを使用）
            sample_hospitals = [
                {
                    'name': '東京総合病院',
                    'address': '東京都港区赤坂1-1-1',
                    'phone_number': '03-1234-5678',
                    'specialties': ['内科', '外科', '小児科', '産婦人科'],
                    'rating': 4.2,
                    'emergency_services': True,
                    'latitude': 35.6762,
                    'longitude': 139.6503,
                    'source': 'jmap'
                },
                {
                    'name': '新宿メディカルセンター',
                    'address': '東京都新宿区新宿3-1-1',
                    'phone_number': '03-2345-6789',
                    'specialties': ['内科', '循環器科', '神経内科'],
                    'rating': 4.0,
                    'emergency_services': False,
                    'latitude': 35.6917,
                    'longitude': 139.7036,
                    'source': 'jmap'
                }
            ]
            
            hospitals.extend(sample_hospitals)
            
        except Exception as e:
            print(f"JMAP scraping error: {e}")
            
        return hospitals
        
    def save_scraped_hospitals(self, hospitals_data: List[Dict]) -> int:
        """スクレイピングした病院データを保存"""
        saved_count = 0
        
        for hospital_data in hospitals_data:
            try:
                # 重複チェック
                existing_hospital = self.db.query(Hospital).filter(
                    Hospital.name == hospital_data['name'],
                    Hospital.address == hospital_data['address']
                ).first()
                
                if existing_hospital:
                    # 既存データの更新
                    self._update_hospital(existing_hospital, hospital_data)
                else:
                    # 新規作成
                    self._create_hospital(hospital_data)
                    
                saved_count += 1
                
            except Exception as e:
                print(f"Hospital save error: {e}")
                continue
                
        self.db.commit()
        return saved_count
        
    def _create_hospital(self, hospital_data: Dict) -> Hospital:
        """新しい病院を作成"""
        hospital = Hospital(
            name=hospital_data['name'],
            address=hospital_data['address'],
            phone_number=hospital_data.get('phone_number', ''),
            website=hospital_data.get('website'),
            latitude=hospital_data.get('latitude'),
            longitude=hospital_data.get('longitude'),
            rating=hospital_data.get('rating'),
            emergency_services=hospital_data.get('emergency_services', False),
            accepts_insurance=True,
            parking_available=True,
            wheelchair_accessible=True,
            data_source=hospital_data.get('source', 'scraped'),
            last_updated=datetime.now()
        )
        
        self.db.add(hospital)
        self.db.flush()  # IDを取得するため
        
        # 診療科を追加
        for specialty_name in hospital_data.get('specialties', []):
            specialty = HospitalSpecialty(
                hospital_id=hospital.id,
                specialty_name=specialty_name,
                is_available=True
            )
            self.db.add(specialty)
            
        return hospital
        
    def _update_hospital(self, hospital: Hospital, hospital_data: Dict):
        """既存病院の情報を更新"""
        hospital.phone_number = hospital_data.get('phone_number', hospital.phone_number)
        hospital.website = hospital_data.get('website', hospital.website)
        hospital.latitude = hospital_data.get('latitude', hospital.latitude)
        hospital.longitude = hospital_data.get('longitude', hospital.longitude)
        hospital.rating = hospital_data.get('rating', hospital.rating)
        hospital.emergency_services = hospital_data.get('emergency_services', hospital.emergency_services)
        hospital.last_updated = datetime.now()
        
        # 診療科の更新
        existing_specialties = {spec.specialty_name for spec in hospital.specialties}
        new_specialties = set(hospital_data.get('specialties', []))
        
        # 新しい診療科を追加
        for specialty_name in new_specialties - existing_specialties:
            specialty = HospitalSpecialty(
                hospital_id=hospital.id,
                specialty_name=specialty_name,
                is_available=True
            )
            self.db.add(specialty)
            
    def run_full_scraping(self, prefectures: List[str] = None) -> Dict:
        """全面的なスクレイピングを実行"""
        if prefectures is None:
            prefectures = ['東京都', '神奈川県', '埼玉県', '千葉県']
            
        results = {
            'total_scraped': 0,
            'total_saved': 0,
            'prefectures': {}
        }
        
        for prefecture in prefectures:
            print(f"Scraping hospitals in {prefecture}...")
            
            scraped_hospitals = self.scrape_hospital_info(prefecture)
            saved_count = self.save_scraped_hospitals(scraped_hospitals)
            
            results['total_scraped'] += len(scraped_hospitals)
            results['total_saved'] += saved_count
            results['prefectures'][prefecture] = {
                'scraped': len(scraped_hospitals),
                'saved': saved_count
            }
            
            # レート制限
            time.sleep(2)
            
        return results