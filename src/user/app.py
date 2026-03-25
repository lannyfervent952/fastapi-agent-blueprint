from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from src._core.application.dtos.base_response import ErrorResponse
from src._core.application.routers.api import docs_router, health_check_router
from src._core.config import settings
from src._core.infrastructure.di.core_container import CoreContainer
from src._core.middleware.exception_middleware import ExceptionMiddleware
from src.user.infrastructure.di.user_container import UserContainer
from src.user.interface.server.bootstrap.user_bootstrap import bootstrap_user_domain


def create_container():
    """User domain DI container"""
    core_container = CoreContainer()
    container = UserContainer(core_container=core_container)
    container.wire(packages=["src.user.server.application.routers"])
    return container


def create_app():
    """User domain FastAPI app -- microservice mode"""
    container = create_container()

    app = FastAPI(
        title="User Service",
        description="User management microservice",
        version="1.0.0",
        root_path="/api",
        docs_url=settings.docs_url,
        redoc_url=settings.redoc_url,
        openapi_url=settings.openapi_url,
        responses={
            400: {"model": ErrorResponse, "description": "Bad request"},
            401: {
                "model": ErrorResponse,
                "description": "Authentication required or token mismatch",
            },
            403: {"model": ErrorResponse, "description": "Forbidden"},
            404: {"model": ErrorResponse, "description": "Resource not found"},
            500: {"model": ErrorResponse, "description": "Internal server error"},
        },
    )

    # Middleware setup
    app.add_middleware(ExceptionMiddleware)

    # TrustedHostMiddleware
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts)

    # CORSMiddleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Core routers
    app.include_router(router=health_check_router.router, tags=["status"])
    app.include_router(router=docs_router.router, tags=["docs"])

    # User domain standalone setup
    bootstrap_user_domain(
        app, database=container.core_container.database(), user_container=container
    )

    return app


app = create_app()
