import multiprocessing

import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import ValidationException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import UJSONResponse

from service.controllers.v1.api import router_v1
from service.controllers.v1.home import home
from service.core import settings
from service.core.celery_app import celery_app

app = FastAPI(
    title=f"{settings.PROJECT_NAME}",
    version=settings.VERSION,
    openapi_url=f"/openapi.json",
)


@app.exception_handler(ValidationException)
async def validation_exception_handler(request: Request, exc: ValidationException):
    return UJSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors()}),
    )


# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include routers
app.include_router(home.router, tags=["Home"])
app.include_router(router_v1, prefix=f"/api/v1")

# Params
max_workers_count = multiprocessing.cpu_count() * 2 + 1

# Send test task to Celery
celery_app.send_task(
    "service.tasks.delay.test_celery", args=["Backend service has started"]
)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        log_level="info",
        reload=True,
        workers=max_workers_count,
    )
