// 管理画面の初期化
document.addEventListener('DOMContentLoaded', function() {
    loadStats();
    setupEventListeners();
});

function loadStats() {
    fetch('/api/v1/scraping/status')
        .then(response => response.json())
        .then(data => {
            displayStats(data);
        })
        .catch(error => {
            console.error('Statistics loading error:', error);
        });
}

function displayStats(data) {
    // 病院統計
    const hospitalStats = document.getElementById('hospital-stats');
    hospitalStats.innerHTML = 
        '<div class="text-3xl font-bold text-blue-600">' + data.hospitals.total + '</div>' +
        '<div class="text-sm text-gray-600">登録病院数</div>' +
        '<div class="text-xs text-gray-500">最終更新: ' + 
        (data.hospitals.last_updated ? new Date(data.hospitals.last_updated).toLocaleString() : '未更新') + '</div>';

    // ニュース統計
    const newsStats = document.getElementById('news-stats');
    newsStats.innerHTML = 
        '<div class="text-3xl font-bold text-green-600">' + data.news.total + '</div>' +
        '<div class="text-sm text-gray-600">ニュース記事数</div>' +
        '<div class="text-xs text-gray-500">最終更新: ' + 
        (data.news.last_updated ? new Date(data.news.last_updated).toLocaleString() : '未更新') + '</div>';

    // アラート統計
    const alertStats = document.getElementById('alert-stats');
    alertStats.innerHTML = 
        '<div class="text-3xl font-bold text-red-600">' + data.alerts.total + '</div>' +
        '<div class="text-sm text-gray-600">アクティブアラート数</div>' +
        '<div class="text-xs text-gray-500">リアルタイム</div>';
}

function setupEventListeners() {
    // 病院データスクレイピング
    document.getElementById('scrape-hospitals-test').addEventListener('click', function() {
        scrapHospitals(true);
    });

    document.getElementById('scrape-hospitals-full').addEventListener('click', function() {
        scrapHospitals(false);
    });

    // ニュースデータスクレイピング
    document.getElementById('scrape-news-test').addEventListener('click', function() {
        scrapNews(true);
    });

    document.getElementById('scrape-news-full').addEventListener('click', function() {
        scrapNews(false);
    });

    // 全データスクレイピング
    document.getElementById('scrape-all-data').addEventListener('click', function() {
        scrapAllData();
    });
}

function scrapHospitals(isTest) {
    const prefectures = Array.from(document.getElementById('prefecture-select').selectedOptions)
        .map(option => option.value);
    
    if (prefectures.length === 0) {
        alert('都道府県を選択してください');
        return;
    }

    const endpoint = isTest ? '/api/v1/scraping/hospitals/scrape/immediate' : '/api/v1/scraping/hospitals/scrape';
    const button = isTest ? document.getElementById('scrape-hospitals-test') : document.getElementById('scrape-hospitals-full');
    
    button.disabled = true;
    button.textContent = isTest ? 'スクレイピング中...' : 'バックグラウンド実行中...';

    fetch(endpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            prefectures: prefectures
        })
    })
    .then(response => response.json())
    .then(data => {
        displayScrapingResult('病院データスクレイピング', data);
        if (isTest) {
            loadStats(); // テストの場合は即座に統計を更新
        }
    })
    .catch(error => {
        console.error('Hospital scraping error:', error);
        displayScrapingResult('病院データスクレイピング', {
            status: 'error',
            message: 'エラーが発生しました: ' + error.message
        });
    })
    .finally(() => {
        button.disabled = false;
        button.textContent = isTest ? 'テストスクレイピング（少量）' : '本格スクレイピング（バックグラウンド）';
    });
}

function scrapNews(isTest) {
    const endpoint = isTest ? '/api/v1/scraping/news/scrape/immediate' : '/api/v1/scraping/news/scrape';
    const button = isTest ? document.getElementById('scrape-news-test') : document.getElementById('scrape-news-full');
    
    button.disabled = true;
    button.textContent = isTest ? 'スクレイピング中...' : 'バックグラウンド実行中...';

    fetch(endpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        displayScrapingResult('健康ニュースクレイピング', data);
        if (isTest) {
            loadStats(); // テストの場合は即座に統計を更新
        }
    })
    .catch(error => {
        console.error('News scraping error:', error);
        displayScrapingResult('健康ニュースクレイピング', {
            status: 'error',
            message: 'エラーが発生しました: ' + error.message
        });
    })
    .finally(() => {
        button.disabled = false;
        button.textContent = isTest ? 'テストスクレイピング' : '本格スクレイピング（バックグラウンド）';
    });
}

function scrapAllData() {
    const button = document.getElementById('scrape-all-data');
    
    if (!confirm('全データのスクレイピングを実行しますか？この処理には時間がかかります。')) {
        return;
    }

    button.disabled = true;
    button.textContent = 'バックグラウンド実行中...';

    fetch('/api/v1/scraping/all/scrape', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        displayScrapingResult('全データスクレイピング', data);
    })
    .catch(error => {
        console.error('Full scraping error:', error);
        displayScrapingResult('全データスクレイピング', {
            status: 'error',
            message: 'エラーが発生しました: ' + error.message
        });
    })
    .finally(() => {
        button.disabled = false;
        button.textContent = '全データスクレイピング実行';
    });
}

function displayScrapingResult(title, result) {
    const resultsContent = document.getElementById('results-content');
    
    const statusClass = 
        result.status === 'completed' ? 'bg-green-100 border-green-400 text-green-700' :
        result.status === 'started' ? 'bg-blue-100 border-blue-400 text-blue-700' :
        'bg-red-100 border-red-400 text-red-700';

    const statusIcon = 
        result.status === 'completed' ? '✅' :
        result.status === 'started' ? '⏳' : '❌';

    let dataDetails = '';
    if (result.data && typeof result.data === 'object') {
        dataDetails = '<pre class="text-xs mt-2 bg-gray-100 p-2 rounded overflow-x-auto">' + 
                     JSON.stringify(result.data, null, 2) + '</pre>';
    }

    const resultHtml = 
        '<div class="border rounded-lg p-4 ' + statusClass + '">' +
        '<div class="flex items-center mb-2">' +
        '<span class="text-2xl mr-2">' + statusIcon + '</span>' +
        '<div>' +
        '<h4 class="font-semibold">' + title + '</h4>' +
        '<p class="text-sm">' + result.message + '</p>' +
        '</div></div>' +
        dataDetails +
        '<div class="text-xs mt-2">実行時刻: ' + new Date(result.timestamp).toLocaleString() + '</div>' +
        '</div>';

    // 最新の結果を先頭に追加
    resultsContent.innerHTML = resultHtml + resultsContent.innerHTML;
}

// 定期的に統計を更新
setInterval(function() {
    loadStats();
}, 30000); // 30秒ごと