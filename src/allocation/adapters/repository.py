import abc

from src.allocation.domain import model
from src.allocation.domain.model import Batch


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, batch: model.Batch):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, reference) -> model.Batch:
        raise NotImplementedError

    @abc.abstractmethod
    def list(self) -> list[model.Batch]:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session) -> None:
        self.session = session

    def add(self, batch) -> None:
        self.session.add(batch)

    def get(self, reference: str) -> 'Batch':
        return self.session.query(model.Batch).filter_by(reference=reference).one()

    def list(self) -> list['Batch']:
        return self.session.query(model.Batch).all()
