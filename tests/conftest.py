# pylint: disable=redefined-outer-name
import time
from pathlib import Path
from typing import Optional

import httpx
import pytest
from httpx import ConnectError, Response
from sqlalchemy import create_engine
from sqlalchemy.engine import Connection
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import clear_mappers, sessionmaker

from src.allocation.adapters.orm import (
    mapper_registry,
    metadata,
    start_mappers,
)
from src.allocation.config import get_config


@pytest.fixture()
def in_memory_db():
    engine = create_engine("sqlite:///:memory:")
    mapper_registry.metadata.create_all(engine)
    return engine


@pytest.fixture()
def session_factory(in_memory_db):
    start_mappers()
    yield sessionmaker(bind=in_memory_db)
    clear_mappers()


@pytest.fixture()
def session(session_factory):
    return session_factory()


def wait_for_postgres_to_come_up(engine) -> Connection | None:  # type: ignore
    deadline = time.time() + 10
    while time.time() < deadline:
        try:
            return engine.connect()
        except OperationalError:
            time.sleep(0.5)
    pytest.fail("Postgres never came up")


def wait_for_webapp_to_come_up() -> Optional[Response]:  # type: ignore
    deadline = time.time() + 10
    url = get_config().api_url

    while time.time() < deadline:
        try:
            return httpx.get(url)
        except ConnectionError:
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
def _restart_api():
    (Path(__file__).parent / "../src/allocation/entrypoints/flask_app.py").touch()
    time.sleep(0.5)
    wait_for_webapp_to_come_up()


@pytest.fixture()
def health():
    try:
        httpx.get('http://127.0.0.1:5000/allocate')
        return True
    except ConnectError:
        return False
