let selectedInputMethod = 'text';
let selectedCategory = '';

function selectInputMethod(method) {
    selectedInputMethod = method;
    
    // UI更新
    document.querySelectorAll('.symptom-input-method').forEach(el => {
        el.classList.remove('border-blue-500', 'bg-blue-50');
        el.classList.add('border-gray-200');
    });
    
    const selectedElement = event.target.closest('.symptom-input-method');
    selectedElement.classList.add('border-blue-500', 'bg-blue-50');
    selectedElement.classList.remove('border-gray-200');
    
    // 入力エリア表示切り替え
    if (method === 'text') {
        document.getElementById('text-input-area').classList.remove('hidden');
        document.getElementById('category-input-area').classList.add('hidden');
    } else {
        document.getElementById('text-input-area').classList.add('hidden');
        document.getElementById('category-input-area').classList.remove('hidden');
    }
}

function selectSymptomCategory(element, category) {
    selectedCategory = category;
    
    // カテゴリ選択状態を更新
    document.querySelectorAll('.symptom-category').forEach(el => {
        el.classList.remove('selected');
    });
    element.classList.add('selected');
    
    // 詳細症状を取得
    fetchSymptomSuggestions(category);
    
    // 症状テキストを設定
    document.getElementById('symptom-text').value = category + 'の症状';
}

function fetchSymptomSuggestions(category) {
    fetch('/api/v1/symptoms/suggestions?category=' + encodeURIComponent(category))
        .then(response => response.json())
        .then(data => {
            const suggestionsContainer = document.getElementById('symptom-suggestions');
            suggestionsContainer.innerHTML = '';
            
            data.forEach(suggestion => {
                const div = document.createElement('div');
                div.className = 'symptom-suggestion border border-gray-200 rounded p-3 cursor-pointer hover:bg-gray-50';
                div.innerHTML = '<div class="flex items-center">' +
                    '<input type="checkbox" class="mr-2" value="' + suggestion.text + '" onchange="updateSymptomText()">' +
                    '<span>' + suggestion.text + '</span>' +
                    (suggestion.common ? '<span class="ml-2 text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">よくある</span>' : '') +
                    '</div>';
                suggestionsContainer.appendChild(div);
            });
            
            document.getElementById('detailed-symptoms').classList.remove('hidden');
        })
        .catch(error => {
            console.error('症状候補の取得に失敗しました:', error);
        });
}

function updateSymptomText() {
    const checkedBoxes = document.querySelectorAll('#symptom-suggestions input[type="checkbox"]:checked');
    const symptoms = Array.from(checkedBoxes).map(cb => cb.value);
    
    if (symptoms.length > 0) {
        document.getElementById('symptom-text').value = symptoms.join('、') + 'の症状があります';
    } else {
        document.getElementById('symptom-text').value = selectedCategory + 'の症状';
    }
}

function submitSymptomForm() {
    const formData = new FormData(document.getElementById('symptom-form'));
    
    showLoading('symptom-result');
    hideError();
    
    fetch('/symptom/input', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        hideLoading('symptom-result');
        if (data.error) {
            showError(data.error);
        } else {
            displaySymptomResult(data);
            // 自動的に診断を実行
            proceedToDiagnosis(data);
        }
    })
    .catch(error => {
        hideLoading('symptom-result');
        showError('症状の処理中にエラーが発生しました: ' + error.message);
    });
}

function displaySymptomResult(data) {
    const resultDiv = document.getElementById('symptom-result');
    
    let html = '<div class="card bg-blue-50 border-blue-200">' +
        '<h3 class="text-lg font-semibold mb-4 text-blue-800">症状解析結果</h3>' +
        '<div class="space-y-2">' +
        '<p><strong>症状:</strong> ' + data.text + '</p>' +
        '<p><strong>カテゴリ:</strong> ' + data.category + '</p>';
    
    if (data.severity) {
        html += '<p><strong>重症度:</strong> ' + data.severity + '／5</p>';
    }
    if (data.duration) {
        html += '<p><strong>期間:</strong> ' + data.duration + '</p>';
    }
    if (data.location) {
        html += '<p><strong>部位:</strong> ' + data.location + '</p>';
    }
    
    html += '<p><strong>キーワード:</strong> ' + data.keywords.join(', ') + '</p>' +
        '</div></div>';
    
    resultDiv.innerHTML = html;
    
    // 結果エリアにスクロール
    resultDiv.scrollIntoView({ behavior: 'smooth' });
}

function proceedToDiagnosis(symptomData) {
    showLoading('diagnosis-result');
    
    const diagnosisData = {
        symptoms: [symptomData.text],
        patient_age: document.getElementById('patient-age').value || null,
        patient_gender: document.getElementById('patient-gender').value || null,
        duration: symptomData.duration || null,
        severity: symptomData.severity || null
    };
    
    fetch('/diagnosis/analyze', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(diagnosisData)
    })
    .then(response => response.json())
    .then(data => {
        hideLoading('diagnosis-result');
        if (data.error) {
            showError(data.error);
        } else {
            displayDiagnosisResult(data);
        }
    })
    .catch(error => {
        hideLoading('diagnosis-result');
        showError('診断処理中にエラーが発生しました: ' + error.message);
    });
}

function displayDiagnosisResult(data) {
    const resultDiv = document.getElementById('diagnosis-result');
    
    const urgencyClass = data.urgency_level === 'high' ? 'urgency-high' : 
                        data.urgency_level === 'medium' ? 'urgency-medium' : 'urgency-low';
    
    const urgencyText = data.urgency_level === 'high' ? '高' : 
                       data.urgency_level === 'medium' ? '中' : '低';
    
    let specialtiesHtml = '';
    if (data.recommended_specialties && data.recommended_specialties.length > 0) {
        specialtiesHtml = data.recommended_specialties.map(specialty => 
            '<div class="bg-white border border-gray-200 rounded-lg p-4 mb-3">' +
            '<h4 class="font-semibold text-lg mb-2">' + specialty.name + '</h4>' +
            '<p class="text-gray-600 mb-3">' + specialty.description + '</p>' +
            '<button class="btn-success" onclick="searchHospitalsBySpecialty(\'' + specialty.name + '\')">' +
            specialty.name + 'の病院を検索</button></div>'
        ).join('');
    }
    
    let conditionsHtml = '';
    if (data.possible_conditions) {
        conditionsHtml = data.possible_conditions.map(condition => 
            '<li class="flex items-center"><span class="text-blue-500 mr-2">•</span>' + condition + '</li>'
        ).join('');
    }
    
    const html = '<div class="card">' +
        '<h3 class="text-xl font-bold mb-6 text-center">診断結果</h3>' +
        '<div class="mb-6">' +
        '<h4 class="font-semibold mb-3 text-lg">考えられる症状・疾患</h4>' +
        '<div class="bg-gray-50 p-4 rounded-lg"><ul class="space-y-1">' + conditionsHtml + '</ul></div></div>' +
        '<div class="mb-6"><h4 class="font-semibold mb-3 text-lg">推奨される診療科</h4>' + specialtiesHtml + '</div>' +
        '<div class="mb-6 p-4 rounded-lg ' + urgencyClass + '">' +
        '<h4 class="font-semibold mb-2 text-lg">緊急度: ' + urgencyText + '</h4>' +
        '<p class="text-sm">' + data.advice + '</p>' +
        '<p class="text-xs mt-2">信頼度: ' + Math.round(data.confidence * 100) + '%</p></div>' +
        '<div class="text-center space-y-4">' +
        '<button class="btn-success text-lg px-6 py-3" onclick="window.location.href=\'/hospital\'">病院を検索する</button>' +
        '<div class="text-sm text-gray-600">' +
        '<p>※ この診断結果は参考情報です。心配な症状がある場合は、必ず医療機関にご相談ください。</p></div></div></div>';
    
    resultDiv.innerHTML = html;
    
    // 結果エリアにスクロール
    resultDiv.scrollIntoView({ behavior: 'smooth' });
}

function searchHospitalsBySpecialty(specialty) {
    window.location.href = '/hospital?specialty=' + encodeURIComponent(specialty);
}

// 初期化
document.addEventListener('DOMContentLoaded', function() {
    selectInputMethod('text');
    
    // フォーム送信
    document.getElementById('symptom-form').addEventListener('submit', function(e) {
        e.preventDefault();
        
        const symptomText = document.getElementById('symptom-text').value;
        if (!symptomText) {
            showError('症状を入力してください');
            return;
        }
        
        // 症状解析
        submitSymptomForm();
    });
});