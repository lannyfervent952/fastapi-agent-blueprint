import importlib

from taskiq import TaskiqState
from taskiq_aws import SQSBroker

from src._apps.worker.broker import container
from src._apps.worker.di.container import create_worker_container
from src._core.infrastructure.discovery import discover_domains


def bootstrap_app(app: SQSBroker) -> None:
    @app.on_event("startup")
    async def startup(state: TaskiqState):
        worker_container = create_worker_container(core_container=container)
        _bootstrap_domains(app=app, worker_container=worker_container)


def _bootstrap_domains(app: SQSBroker, worker_container) -> None:
    """Dynamically bootstrap workers for all domains detected by discover_domains()."""
    for name in discover_domains():
        module_path = f"src.{name}.interface.worker.bootstrap.{name}_bootstrap"
        module = importlib.import_module(module_path)
        bootstrap_fn = getattr(module, f"bootstrap_{name}_domain")
        domain_container = getattr(worker_container, f"{name}_container")

        bootstrap_fn(app=app, **{f"{name}_container": domain_container})
