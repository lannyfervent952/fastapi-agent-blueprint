"""User domain independent bootstrap"""

from fastapi import FastAPI
from sqladmin import Admin

from src._core.infrastructure.database.database import Database
from src.user.infrastructure.di.user_container import UserContainer
from src.user.interface.admin.views.user_view import UserView
from src.user.interface.server.routers import user_router


def create_user_container(user_container: UserContainer):
    user_container.wire(packages=["src.user.interface.server.routers"])
    return user_container


def setup_user_routes(app: FastAPI):
    """Register user domain routes"""
    app.include_router(router=user_router.router, prefix="/v1", tags=["User"])


def setup_user_admin(app: FastAPI, database: Database):
    """Register user domain admin views"""
    admin = Admin(app=app, engine=database.engine)
    admin.add_view(UserView)
    return admin


def bootstrap_user_domain(
    app: FastAPI, database: Database, user_container: UserContainer
):
    user_container = create_user_container(user_container=user_container)
    setup_user_routes(app=app)

    if database:
        setup_user_admin(app=app, database=database)
