package main

import (
	"log"
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/joho/godotenv"

	"symptom-checker-frontend/internal/config"
	"symptom-checker-frontend/internal/handlers"
	"symptom-checker-frontend/internal/middleware"
	"symptom-checker-frontend/internal/services"
)

func main() {
	// 環境変数を読み込み
	if err := godotenv.Load(); err != nil {
		log.Printf("Warning: .env file not found: %v", err)
	}

	// 設定を読み込み
	cfg := config.Load()

	// サービスを初期化
	apiService := services.NewAPIService(cfg.BackendURL)

	// ハンドラーを初期化
	handlers := handlers.NewHandlers(apiService)

	// Ginエンジンを初期化
	if cfg.Debug {
		gin.SetMode(gin.DebugMode)
	} else {
		gin.SetMode(gin.ReleaseMode)
	}

	router := gin.Default()

	// ミドルウェアを設定
	router.Use(middleware.CORS())
	router.Use(middleware.Logger())

	// 静的ファイルとテンプレートを設定
	router.Static("/static", "./static")
	router.LoadHTMLGlob("templates/*")

	// ルートを設定
	setupRoutes(router, handlers)

	// サーバーを開始
	port := cfg.Port
	if port == "" {
		port = "8080"
	}

	log.Printf("Starting server on port %s", port)
	if err := router.Run(":" + port); err != nil {
		log.Fatal("Failed to start server:", err)
	}
}

func setupRoutes(router *gin.Engine, h *handlers.Handlers) {
	// ホームページ
	router.GET("/", h.Home)

	// 健康チェック
	router.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"status": "healthy"})
	})

	// 症状チェック関連
	symptomGroup := router.Group("/symptom")
	{
		symptomGroup.GET("/", h.SymptomCheck)
		symptomGroup.POST("/input", h.SymptomInput)
		symptomGroup.GET("/categories", h.SymptomCategories)
	}

	// 診断関連
	diagnosisGroup := router.Group("/diagnosis")
	{
		diagnosisGroup.GET("/", h.DiagnosisResult)
		diagnosisGroup.POST("/analyze", h.AnalyzeSymptoms)
	}

	// 病院検索関連
	hospitalGroup := router.Group("/hospital")
	{
		hospitalGroup.GET("/", h.HospitalSearch)
		hospitalGroup.POST("/search", h.SearchHospitals)
		hospitalGroup.GET("/nearby", h.NearbyHospitals)
		hospitalGroup.GET("/:id", h.HospitalDetail)
	}

	// ユーザー関連
	userGroup := router.Group("/user")
	{
		userGroup.GET("/register", h.UserRegister)
		userGroup.POST("/register", h.UserRegisterSubmit)
		userGroup.GET("/profile", h.UserProfile)
		userGroup.PUT("/profile", h.UserProfileUpdate)
	}

	// ニュース・情報関連
	newsGroup := router.Group("/news")
	{
		newsGroup.GET("/", h.NewsPage)
	}

	// API プロキシ（バックエンドAPIへのプロキシ）
	apiGroup := router.Group("/api/v1")
	{
		apiGroup.Any("/*path", h.APIProxy)
	}
}