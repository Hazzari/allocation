# pylint: disable=attribute-defined-outside-init
from __future__ import annotations

import abc

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.allocation.adapters import repository
from src.allocation.config import get_config

DEFAULT_SESSION_FACTORY = sessionmaker(bind=create_engine(get_config().postgres_uri))


class AbstractUnitOfWork(abc.ABC):
    batches: repository.AbstractRepository

    def __enter__(self) -> AbstractUnitOfWork:
        return self

    def __exit__(self, *args) -> None:
        self.rollback()

    @abc.abstractmethod
    def commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self) -> None:
        raise NotImplementedError


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_factory=DEFAULT_SESSION_FACTORY):
        self.session_factory = session_factory

    def __enter__(self):
        self.session = self.session_factory()
        self.batches = repository.SqlAlchemyRepository(self.session)
        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)
        self.session.close()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()
