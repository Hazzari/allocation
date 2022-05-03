# pylint: disable=redefined-outer-name
import time
from pathlib import Path

import httpx
import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.future import Engine
from sqlalchemy.orm import clear_mappers, sessionmaker

from adapters import repository
from adapters.orm import metadata, start_mappers
from config import get_config
from domain.model import Batch


@pytest.fixture()
def in_memory_db():
    engine = create_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    return engine


@pytest.fixture()
def session(in_memory_db):
    start_mappers()
    yield sessionmaker(bind=in_memory_db)()
    clear_mappers()


def wait_for_postgres_to_come_up(engine) -> Engine:
    deadline = time.time() + 10
    while time.time() < deadline:
        try:
            return engine.connect()
        except OperationalError:
            time.sleep(0.5)
    pytest.fail("Postgres never came up")


def wait_for_webapp_to_come_up() -> httpx.Response:
    deadline = time.time() + 10
    url = get_config().api_url
    while time.time() < deadline:
        try:
            return httpx.get(url)
        except httpx.ConnectError:
            time.sleep(0.5)
    pytest.fail("API never came up")


@pytest.fixture(scope="session")
def postgres_db():
    engine = create_engine(get_config().postgres_uri)
    wait_for_postgres_to_come_up(engine)
    metadata.create_all(engine)
    return engine


@pytest.fixture()
def postgres_session(postgres_db):
    start_mappers()
    yield sessionmaker(bind=postgres_db)()
    clear_mappers()


@pytest.fixture()
def _restart_api() -> None:
    (Path(__file__).parent / "../entrypoints/flask_app.py").touch()
    time.sleep(0.5)
    wait_for_webapp_to_come_up()


class FakeRepository(repository.AbstractRepository):
    def __init__(self, batches) -> None:
        self._batches = set(batches)

    def add(self, batch) -> None:
        self._batches.add(batch)

    def get(self, reference) -> 'Batch':
        return next(b for b in self._batches if b.reference == reference)

    def list(self) -> list:
        return list(self._batches)


class FakeSession:
    committed = False

    def commit(self):
        self.committed = True


@pytest.fixture()
def fake_repo():
    return FakeRepository([])


@pytest.fixture()
def fake_session():
    return FakeSession()
