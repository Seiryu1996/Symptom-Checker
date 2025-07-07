from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from decouple import config
import uvicorn

from app.api.routes import router as api_router

app = FastAPI(
    title="Symptom Checker API",
    description="症状チェッカーサービスのAPI",
    version="1.0.0",
)

# CORS設定
origins = config("CORS_ORIGINS", default="http://localhost:8080,http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# APIルートの追加
app.include_router(api_router, prefix="/api/v1")

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <head>
            <title>Symptom Checker API</title>
        </head>
        <body>
            <h1>Symptom Checker API</h1>
            <p>API is running! Visit <a href="/docs">/docs</a> for interactive documentation.</p>
        </body>
    </html>
    """

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "symptom-checker-api"}

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=config("FASTAPI_HOST", default="0.0.0.0"),
        port=config("FASTAPI_PORT", default=8000, cast=int),
        reload=config("DEBUG", default=False, cast=bool)
    )