from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.database import init_db, close_db_connection
from core.config import settings
from routes.admin import router as AdminRouter
from routes.user import router as UserRouter
from routes.project import router as ProjectRouter
from routes.achievement import router as AchievementRouter
from routes.about_us import router as AboutUsRouter
from routes.contact import router as ContactRouter
from routes.utils import router as UtilsRouter

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend API for Chapters Portfolio",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Set up CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Database event handlers
@app.on_event("startup")
async def startup_db_client():
    await init_db()
    # Make it obvious in the logs whether the contact form will work.
    # If you change CONTACT_TO_EMAIL in .env, the running process won't pick
    # the new value up until you restart uvicorn -- this log confirms what
    # got loaded.
    if settings.CONTACT_TO_EMAIL:
        provider = "resend" if settings.RESEND_API_KEY else (
            "smtp" if settings.CONTACT_SMTP_HOST else "none"
        )
        print(
            f"[contact] delivery configured via '{provider}' "
            f"-> to={settings.CONTACT_TO_EMAIL} from={settings.CONTACT_FROM_EMAIL}"
        )
    else:
        print("[contact] WARNING: CONTACT_TO_EMAIL is empty -- form will return 503")

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_db_connection()

# Include routers
app.include_router(AdminRouter, prefix="/admin", tags=["Admin"])
app.include_router(UserRouter, prefix="/user", tags=["User"])
app.include_router(ProjectRouter, prefix="/projects", tags=["Projects"])
app.include_router(AchievementRouter, prefix="/achievements", tags=["Achievements"])
app.include_router(AboutUsRouter, prefix="/about-us", tags=["AboutUs"])
app.include_router(ContactRouter, prefix="/contact", tags=["Contact"])
app.include_router(UtilsRouter, prefix="/utils", tags=["Utils"])

@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "docs": "/docs",
        "version": "1.0.0"
    }
