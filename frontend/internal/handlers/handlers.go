package handlers

import (
	"io"
	"net/http"
	"strconv"
	"strings"

	"github.com/gin-gonic/gin"
	"symptom-checker-frontend/internal/services"
)

type Handlers struct {
	apiService *services.APIService
}

func NewHandlers(apiService *services.APIService) *Handlers {
	return &Handlers{
		apiService: apiService,
	}
}

func (h *Handlers) Home(c *gin.Context) {
	c.HTML(http.StatusOK, "index.html", gin.H{
		"title": "症状チェッカー",
	})
}

func (h *Handlers) SymptomCheck(c *gin.Context) {
	categories, err := h.apiService.GetSymptomCategories()
	if err != nil {
		c.HTML(http.StatusInternalServerError, "error.html", gin.H{
			"error": "症状カテゴリの取得に失敗しました",
		})
		return
	}

	c.HTML(http.StatusOK, "symptom_check.html", gin.H{
		"title":      "症状チェック",
		"categories": categories,
	})
}

func (h *Handlers) SymptomInput(c *gin.Context) {
	var input services.SymptomInput
	
	// フォームデータから症状入力情報を取得
	input.Text = c.PostForm("text")
	if severityStr := c.PostForm("severity"); severityStr != "" {
		if severity, err := strconv.Atoi(severityStr); err == nil {
			input.Severity = &severity
		}
	}
	input.Duration = c.PostForm("duration")
	input.Location = c.PostForm("location")

	if input.Text == "" {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "症状を入力してください",
		})
		return
	}

	result, err := h.apiService.SubmitSymptom(input)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "症状の処理に失敗しました",
		})
		return
	}

	c.JSON(http.StatusOK, result)
}

func (h *Handlers) SymptomCategories(c *gin.Context) {
	categories, err := h.apiService.GetSymptomCategories()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "カテゴリの取得に失敗しました",
		})
		return
	}

	c.JSON(http.StatusOK, categories)
}

func (h *Handlers) DiagnosisResult(c *gin.Context) {
	c.HTML(http.StatusOK, "diagnosis_result.html", gin.H{
		"title": "診断結果",
	})
}

func (h *Handlers) AnalyzeSymptoms(c *gin.Context) {
	var input services.DiagnosisInput
	
	// フォームデータから診断入力情報を取得
	symptomsStr := c.PostForm("symptoms")
	if symptomsStr != "" {
		input.Symptoms = strings.Split(symptomsStr, ",")
	}
	
	if ageStr := c.PostForm("patient_age"); ageStr != "" {
		if age, err := strconv.Atoi(ageStr); err == nil {
			input.PatientAge = &age
		}
	}
	
	input.PatientGender = c.PostForm("patient_gender")
	input.Duration = c.PostForm("duration")
	
	if severityStr := c.PostForm("severity"); severityStr != "" {
		if severity, err := strconv.Atoi(severityStr); err == nil {
			input.Severity = &severity
		}
	}

	if len(input.Symptoms) == 0 {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "症状を入力してください",
		})
		return
	}

	result, err := h.apiService.AnalyzeSymptoms(input)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "診断分析に失敗しました",
		})
		return
	}

	c.JSON(http.StatusOK, result)
}

func (h *Handlers) HospitalSearch(c *gin.Context) {
	c.HTML(http.StatusOK, "hospital_search.html", gin.H{
		"title": "病院検索",
	})
}

func (h *Handlers) SearchHospitals(c *gin.Context) {
	var params services.HospitalSearchParams
	
	// フォームデータから検索パラメータを取得
	specialtiesStr := c.PostForm("specialties")
	if specialtiesStr != "" {
		params.Specialties = strings.Split(specialtiesStr, ",")
	}
	
	if latStr := c.PostForm("latitude"); latStr != "" {
		if lat, err := strconv.ParseFloat(latStr, 64); err == nil {
			if lngStr := c.PostForm("longitude"); lngStr != "" {
				if lng, err := strconv.ParseFloat(lngStr, 64); err == nil {
					params.UserLocation = &services.Location{
						Latitude:  lat,
						Longitude: lng,
						Address:   c.PostForm("address"),
					}
				}
			}
		}
	}
	
	if maxDistStr := c.PostForm("max_distance"); maxDistStr != "" {
		if maxDist, err := strconv.ParseFloat(maxDistStr, 64); err == nil {
			params.MaxDistance = &maxDist
		}
	}
	
	params.EmergencyOnly = c.PostForm("emergency_only") == "true"

	hospitals, err := h.apiService.SearchHospitals(params)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "病院検索に失敗しました",
		})
		return
	}

	c.JSON(http.StatusOK, hospitals)
}

func (h *Handlers) NearbyHospitals(c *gin.Context) {
	c.HTML(http.StatusOK, "nearby_hospitals.html", gin.H{
		"title": "近くの病院",
	})
}

func (h *Handlers) HospitalDetail(c *gin.Context) {
	hospitalID := c.Param("id")
	
	c.HTML(http.StatusOK, "hospital_detail.html", gin.H{
		"title":      "病院詳細",
		"hospitalID": hospitalID,
	})
}

func (h *Handlers) UserRegister(c *gin.Context) {
	c.HTML(http.StatusOK, "user_register.html", gin.H{
		"title": "ユーザー登録",
	})
}

func (h *Handlers) UserRegisterSubmit(c *gin.Context) {
	// ユーザー登録処理
	c.JSON(http.StatusOK, gin.H{
		"message": "ユーザー登録が完了しました",
	})
}

func (h *Handlers) UserProfile(c *gin.Context) {
	c.HTML(http.StatusOK, "user_profile.html", gin.H{
		"title": "ユーザープロフィール",
	})
}

func (h *Handlers) UserProfileUpdate(c *gin.Context) {
	// プロフィール更新処理
	c.JSON(http.StatusOK, gin.H{
		"message": "プロフィールが更新されました",
	})
}

func (h *Handlers) NewsPage(c *gin.Context) {
	c.HTML(http.StatusOK, "news.html", gin.H{
		"title": "健康情報・ニュース",
	})
}

func (h *Handlers) APIProxy(c *gin.Context) {
	path := c.Param("path")
	method := c.Request.Method
	
	var body io.Reader
	if c.Request.Body != nil {
		body = c.Request.Body
	}
	
	resp, err := h.apiService.ProxyRequest(method, path, body)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "APIリクエストに失敗しました",
		})
		return
	}
	defer resp.Body.Close()
	
	// レスポンスヘッダーをコピー
	for key, values := range resp.Header {
		for _, value := range values {
			c.Header(key, value)
		}
	}
	
	c.Status(resp.StatusCode)
	
	// レスポンスボディをコピー
	if _, err := io.Copy(c.Writer, resp.Body); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "レスポンスの処理に失敗しました",
		})
		return
	}
}