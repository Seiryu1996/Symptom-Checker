// メインのJavaScriptファイル

// ユーティリティ関数
function showLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = '<div class="loading"></div> 読み込み中...';
    }
}

function hideLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = '';
    }
}

function showError(message, elementId = 'error-message') {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">${message}</div>`;
        element.style.display = 'block';
    }
}

function hideError(elementId = 'error-message') {
    const element = document.getElementById(elementId);
    if (element) {
        element.style.display = 'none';
    }
}

function showSuccess(message, elementId = 'success-message') {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `<div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">${message}</div>`;
        element.style.display = 'block';
    }
}

// 位置情報取得
function getCurrentLocation() {
    return new Promise((resolve, reject) => {
        if (!navigator.geolocation) {
            reject(new Error('位置情報がサポートされていません'));
            return;
        }

        navigator.geolocation.getCurrentPosition(
            (position) => {
                resolve({
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude
                });
            },
            (error) => {
                reject(error);
            },
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 300000
            }
        );
    });
}

// 病院へ電話をかける
function callHospital(phoneNumber) {
    if (phoneNumber) {
        window.location.href = `tel:${phoneNumber}`;
    }
}

// 病院の地図を表示
function showHospitalMap(latitude, longitude, hospitalName) {
    const mapUrl = `https://www.google.com/maps/search/?api=1&query=${latitude},${longitude}&query_place_id=${encodeURIComponent(hospitalName)}`;
    window.open(mapUrl, '_blank');
}

// フォーム送信処理
function submitForm(formId, url, onSuccess, onError) {
    const form = document.getElementById(formId);
    if (!form) return;

    const formData = new FormData(form);
    
    fetch(url, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            onError(data.error);
        } else {
            onSuccess(data);
        }
    })
    .catch(error => {
        onError('通信エラーが発生しました: ' + error.message);
    });
}

// 症状入力フォーム処理
function submitSymptomForm() {
    const form = document.getElementById('symptom-form');
    if (!form) return;

    showLoading('symptom-result');
    hideError();

    submitForm(
        'symptom-form',
        '/symptom/input',
        (data) => {
            hideLoading('symptom-result');
            displaySymptomResult(data);
        },
        (error) => {
            hideLoading('symptom-result');
            showError(error);
        }
    );
}

// 症状結果表示
function displaySymptomResult(data) {
    const resultDiv = document.getElementById('symptom-result');
    if (!resultDiv) return;

    const html = `
        <div class="card">
            <h3 class="text-lg font-semibold mb-2">症状解析結果</h3>
            <p><strong>症状:</strong> ${data.text}</p>
            <p><strong>カテゴリ:</strong> ${data.category}</p>
            ${data.severity ? `<p><strong>重症度:</strong> ${data.severity}/5</p>` : ''}
            ${data.duration ? `<p><strong>期間:</strong> ${data.duration}</p>` : ''}
            ${data.location ? `<p><strong>部位:</strong> ${data.location}</p>` : ''}
            <div class="mt-4">
                <button class="btn-primary" onclick="proceedToDiagnosis('${data.id}')">
                    診断を続ける
                </button>
            </div>
        </div>
    `;

    resultDiv.innerHTML = html;
}

// 診断処理
function proceedToDiagnosis(symptomId) {
    const symptoms = [document.getElementById('symptom-text').value];
    
    showLoading('diagnosis-result');
    hideError();

    const data = {
        symptoms: symptoms,
        patient_age: document.getElementById('patient-age') ? document.getElementById('patient-age').value : null,
        patient_gender: document.getElementById('patient-gender') ? document.getElementById('patient-gender').value : null,
        duration: document.getElementById('duration') ? document.getElementById('duration').value : null,
        severity: document.getElementById('severity') ? document.getElementById('severity').value : null
    };

    fetch('/diagnosis/analyze', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        hideLoading('diagnosis-result');
        displayDiagnosisResult(data);
    })
    .catch(error => {
        hideLoading('diagnosis-result');
        showError('診断処理中にエラーが発生しました: ' + error.message);
    });
}

// 診断結果表示
function displayDiagnosisResult(data) {
    const resultDiv = document.getElementById('diagnosis-result');
    if (!resultDiv) return;

    const urgencyClass = data.urgency_level === 'high' ? 'urgency-high' : 
                        data.urgency_level === 'medium' ? 'urgency-medium' : 'urgency-low';

    let specialtiesHtml = '';
    if (data.recommended_specialties) {
        specialtiesHtml = data.recommended_specialties.map(specialty => `
            <div class="symptom-category ${specialty.urgency === 'high' ? 'urgency-high' : ''}">
                <h4 class="font-semibold">${specialty.name}</h4>
                <p class="text-sm text-gray-600">${specialty.description}</p>
            </div>
        `).join('');
    }

    const html = `
        <div class="card">
            <h3 class="text-lg font-semibold mb-4">診断結果</h3>
            
            <div class="mb-4">
                <h4 class="font-semibold mb-2">考えられる症状・疾患</h4>
                <ul class="list-disc list-inside">
                    ${data.possible_conditions.map(condition => `<li>${condition}</li>`).join('')}
                </ul>
            </div>

            <div class="mb-4">
                <h4 class="font-semibold mb-2">推奨される診療科</h4>
                ${specialtiesHtml}
            </div>

            <div class="mb-4 p-3 rounded ${urgencyClass}">
                <h4 class="font-semibold mb-2">緊急度: ${data.urgency_level.toUpperCase()}</h4>
                <p>${data.advice}</p>
            </div>

            <div class="mt-4">
                <button class="btn-success" onclick="searchHospitals()">
                    病院を検索する
                </button>
            </div>
        </div>
    `;

    resultDiv.innerHTML = html;
}

// 病院検索
function searchHospitals() {
    window.location.href = '/hospital';
}

// 症状カテゴリ選択
function selectSymptomCategory(element, category) {
    // 他のカテゴリの選択状態を解除
    document.querySelectorAll('.symptom-category').forEach(el => {
        el.classList.remove('selected');
    });
    
    // 選択されたカテゴリを強調
    element.classList.add('selected');
    
    // 症状テキストエリアに反映
    const textArea = document.getElementById('symptom-text');
    if (textArea) {
        textArea.value = category;
    }
}

// 初期化処理
document.addEventListener('DOMContentLoaded', function() {
    // 位置情報の取得権限を確認
    if (navigator.geolocation) {
        const locationBtn = document.getElementById('get-location-btn');
        if (locationBtn) {
            locationBtn.addEventListener('click', function() {
                getCurrentLocation()
                    .then(position => {
                        document.getElementById('latitude').value = position.latitude;
                        document.getElementById('longitude').value = position.longitude;
                        showSuccess('位置情報を取得しました');
                    })
                    .catch(error => {
                        showError('位置情報の取得に失敗しました: ' + error.message);
                    });
            });
        }
    }

    // フォーム送信イベントの設定
    const symptomForm = document.getElementById('symptom-form');
    if (symptomForm) {
        symptomForm.addEventListener('submit', function(e) {
            e.preventDefault();
            submitSymptomForm();
        });
    }
});

// スムーズスクロール
function scrollToElement(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.scrollIntoView({ behavior: 'smooth' });
    }
}