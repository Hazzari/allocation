import abc
from dataclasses import dataclass
from typing import Any

from app.model import Batch


class BaseRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, batch: Batch) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, reference) -> Batch:
        raise NotImplementedError


@dataclass
class SqlAlchemyRepository(BaseRepository):
    def __init__(self, session: Any):
        self.session = session

    def add(self, batch) -> None:
        self.session.add(batch)

    def get(self, reference):
        return self.session.query(Batch).filter_by(reference=reference).one()

    def list(self):
        return self.session.query(Batch).all()
