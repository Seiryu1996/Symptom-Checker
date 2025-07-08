let currentCategory = '';
let currentPage = 1;
const itemsPerPage = 10;

// 初期化
document.addEventListener('DOMContentLoaded', function() {
    loadNewsCategories();
    loadHealthAlerts();
    loadNews();
    
    // リフレッシュボタンのイベント
    document.getElementById('refresh-news').addEventListener('click', function() {
        loadNews();
        loadHealthAlerts();
    });
    
    addNewsStyles();
});

function loadNewsCategories() {
    // カテゴリのサンプルデータ
    const categories = [
        { name: '予防', icon: '🛡️' },
        { name: '感染症', icon: '🦠' },
        { name: '栄養', icon: '🥗' },
        { name: '運動', icon: '🏃‍♂️' },
        { name: '医療技術', icon: '🔬' },
        { name: 'メンタルヘルス', icon: '🧠' }
    ];
    
    displayNewsCategories(categories);
}

function displayNewsCategories(categories) {
    const container = document.getElementById('news-categories');
    
    let html = '<div class="category-item ' + (!currentCategory ? 'selected' : '') + '" onclick="selectCategory(\'\')"><span class="mr-2">📰</span><span>すべて</span></div>';
    
    categories.forEach(category => {
        html += '<div class="category-item ' + (currentCategory === category.name ? 'selected' : '') + '" onclick="selectCategory(\'' + category.name + '\')">' +
                '<span class="mr-2">' + category.icon + '</span>' +
                '<span>' + category.name + '</span></div>';
    });
    
    container.innerHTML = html;
}

function selectCategory(category) {
    currentCategory = category;
    currentPage = 1;
    
    // カテゴリ選択状態を更新
    document.querySelectorAll('.category-item').forEach(el => {
        el.classList.remove('selected');
    });
    event.target.classList.add('selected');
    
    loadNews();
}

function loadHealthAlerts() {
    fetch('/api/v1/news/health-alerts')
        .then(response => response.json())
        .then(alerts => {
            displayHealthAlerts(alerts);
        })
        .catch(error => {
            console.error('アラート取得エラー:', error);
        });
}

function displayHealthAlerts(alerts) {
    const container = document.getElementById('health-alerts');
    
    if (alerts.length === 0) {
        container.innerHTML = '';
        return;
    }
    
    let html = '';
    alerts.forEach(alert => {
        const severityClass = 
            alert.severity === 'danger' ? 'bg-red-100 border-red-400 text-red-700' :
            alert.severity === 'warning' ? 'bg-yellow-100 border-yellow-400 text-yellow-700' :
            'bg-blue-100 border-blue-400 text-blue-700';
        
        const severityIcon = 
            alert.severity === 'danger' ? '🚨' :
            alert.severity === 'warning' ? '⚠️' : 'ℹ️';
        
        html += '<div class="alert-item ' + severityClass + ' border rounded-lg p-4 mb-3">' +
                '<div class="flex items-start">' +
                '<span class="text-2xl mr-3">' + severityIcon + '</span>' +
                '<div class="flex-1">' +
                '<h4 class="font-semibold mb-1">' + alert.title + '</h4>' +
                '<p class="text-sm mb-2">' + alert.message + '</p>' +
                '<div class="flex justify-between items-center text-xs">' +
                '<span>' + (alert.area ? '対象地域: ' + alert.area : '') + '</span>' +
                '<span>有効期限: ' + new Date(alert.valid_until).toLocaleDateString() + '</span>' +
                '</div></div></div></div>';
    });
    
    container.innerHTML = html;
}

function loadNews(append = false) {
    const params = new URLSearchParams();
    if (currentCategory) {
        params.append('category', currentCategory);
    }
    params.append('limit', itemsPerPage);
    
    fetch('/api/v1/news/health-news?' + params)
        .then(response => response.json())
        .then(news => {
            displayNews(news, append);
        })
        .catch(error => {
            console.error('ニュース取得エラー:', error);
            if (!append) {
                document.getElementById('news-list').innerHTML = 
                    '<p class="text-red-600 text-center">ニュースの読み込みに失敗しました</p>';
            }
        });
}

function displayNews(news, append = false) {
    const container = document.getElementById('news-list');
    const loadMoreContainer = document.getElementById('load-more-container');
    
    if (news.length === 0 && !append) {
        container.innerHTML = '<div class="text-center py-8 text-gray-500">' +
            '<div class="text-4xl mb-4">📰</div>' +
            '<p>該当するニュースが見つかりませんでした</p></div>';
        loadMoreContainer.classList.add('hidden');
        return;
    }
    
    let html = '';
    news.forEach(item => {
        const priorityBadge = 
            item.priority === 'high' ? '<span class="bg-red-100 text-red-800 text-xs px-2 py-1 rounded">重要</span>' :
            item.priority === 'medium' ? '<span class="bg-yellow-100 text-yellow-800 text-xs px-2 py-1 rounded">注意</span>' :
            '';
        
        const publishedDate = new Date(item.published_at).toLocaleDateString('ja-JP');
        const hospitalInfo = item.hospital_name ? '<span class="text-blue-600">' + item.hospital_name + '</span>' : '';
        
        const tagsHtml = item.tags ? item.tags.map(tag => 
            '<span class="bg-gray-100 text-gray-700 text-xs px-2 py-1 rounded">#' + tag + '</span>'
        ).join('') : '';
        
        html += '<div class="news-item border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">' +
                '<div class="flex items-start justify-between mb-3">' +
                '<div class="flex items-center space-x-2">' +
                '<span class="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">' + item.category + '</span>' +
                priorityBadge + '</div>' +
                '<span class="text-sm text-gray-500">' + publishedDate + '</span></div>' +
                '<h3 class="text-lg font-semibold mb-3 text-gray-800">' + item.title + '</h3>' +
                '<p class="text-gray-600 mb-4 leading-relaxed">' + item.content + '</p>' +
                '<div class="flex justify-between items-center">' +
                '<div class="flex items-center space-x-4 text-sm text-gray-500">' +
                hospitalInfo + '<div class="flex flex-wrap gap-1">' + tagsHtml + '</div></div>' +
                '<button class="text-blue-600 hover:text-blue-800 text-sm font-medium" onclick="shareNews(\'' + item.id + '\', \'' + item.title + '\')">' +
                '📤 共有</button></div></div>';
    });
    
    if (append) {
        container.innerHTML += html;
    } else {
        container.innerHTML = html;
    }
    
    // もっと読むボタンの表示制御
    if (news.length === itemsPerPage) {
        loadMoreContainer.classList.remove('hidden');
    } else {
        loadMoreContainer.classList.add('hidden');
    }
}

function shareNews(newsId, title) {
    if (navigator.share) {
        navigator.share({
            title: title,
            text: '症状チェッカーの健康情報をチェック！',
            url: window.location.href
        }).catch(console.error);
    } else {
        // フォールバック: URLをクリップボードにコピー
        navigator.clipboard.writeText(window.location.href).then(() => {
            alert('URLをクリップボードにコピーしました');
        }).catch(() => {
            alert('共有機能はサポートされていません');
        });
    }
}

function addNewsStyles() {
    const style = document.createElement('style');
    style.textContent = 
        '.category-item { display: flex; align-items: center; padding: 0.75rem; border-radius: 0.375rem; cursor: pointer; transition: all 0.2s; border: 1px solid transparent; }' +
        '.category-item:hover { background-color: #f3f4f6; }' +
        '.category-item.selected { background-color: #dbeafe; border-color: #3b82f6; color: #1e40af; font-weight: 500; }' +
        '.alert-item { animation: fadeIn 0.3s ease-in; }' +
        '.news-item { animation: slideUp 0.3s ease-out; }' +
        '@keyframes fadeIn { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }' +
        '@keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }';
    document.head.appendChild(style);
}