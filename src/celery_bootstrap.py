from celery import Celery

from src._shared.infrastructure.di.server_container import ServerContainer
from src.user.interface.consumer.bootstrap.user_bootstrap import bootstrap_user


def bootstrap_celery_app(app: Celery) -> None:
    server_container = ServerContainer()

    bootstrap_user(app=app, user_container=server_container.user_container)
