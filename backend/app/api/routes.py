from fastapi import APIRouter

from app.api.endpoints import symptoms, diagnosis, hospitals, users, news

router = APIRouter()

router.include_router(symptoms.router, prefix="/symptoms", tags=["症状"])
router.include_router(diagnosis.router, prefix="/diagnosis", tags=["診断"])
router.include_router(hospitals.router, prefix="/hospitals", tags=["病院"])
router.include_router(users.router, prefix="/users", tags=["ユーザー"])
router.include_router(news.router, prefix="/news", tags=["ニュース・情報"])