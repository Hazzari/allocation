import pytest

from src.allocation.adapters import repository
from src.allocation.adapters.repository import AbstractRepository
from src.allocation.domain.model import Batch
from src.allocation.service_layer import services, unit_of_work


class FakeRepository(repository.AbstractRepository):
    def __init__(self, batches: list[Batch]):
        self._batches = set(batches)

    def add(self, batch):
        self._batches.add(batch)

    def get(self, reference):
        return next(b for b in self._batches if b.reference == reference)

    def list(self):
        return list(self._batches)


class FakeUnitOfWork(unit_of_work.AbstractUnitOfWork):
    def __init__(self) -> None:
        self.batches: 'AbstractRepository' = FakeRepository([])
        self.committed = False

    def commit(self):
        self.committed = True

    def rollback(self):
        pass


def test_add_batch():
    uow = FakeUnitOfWork()

    services.add_batch("b1", "СКРИПУЧЕЕ-КРЕСЛО", 100, None, uow)

    assert uow.batches.get("b1") is not None
    assert uow.committed


def test_allocate_returns_allocation():
    uow = FakeUnitOfWork()
    services.add_batch("batch1", "КРУТАЯ-ЛАМПА", 100, None, uow)
    result = services.allocate("o1", "КРУТАЯ-ЛАМПА", 10, uow)
    assert result == "batch1"


def test_allocate_errors_for_invalid_sku():
    uow = FakeUnitOfWork()
    services.add_batch("b1", "НЕДОПУСТИМЫЙ-SKU", 100, None, uow)

    with pytest.raises(services.InvalidSku, match="Invalid sku НЕСУЩЕСТВУЮЩИЙ"):
        services.allocate("o1", "НЕСУЩЕСТВУЮЩИЙ-SKU", 10, uow)


def test_commits():
    uow = FakeUnitOfWork()
    services.add_batch("b1", "ЗЛОВЕЩЕЕ-ЗЕРКАЛО", 100, None, uow)
    services.allocate("o1", "ЗЛОВЕЩЕЕ-ЗЕРКАЛО", 10, uow)
    assert uow.committed is True


def test_deallocate_decrements_available_quantity():
    uow: FakeUnitOfWork = FakeUnitOfWork()
    batch_id = "batch001"
    services.add_batch(batch_id, "СИНИЙ-ПЛИНТУС", 100, None, uow)
    services.allocate('line001', 'СИНИЙ-ПЛИНТУС', 10, uow)
    batch = uow.batches.get(reference=batch_id)
    assert batch.available_quantity == 90
    services.deallocate(batch_id, 'line001', 'СИНИЙ-ПЛИНТУС', 10, uow)
    assert batch.available_quantity == 100


def test_deallocate_decrements_correct_quantity():
    uow = FakeUnitOfWork()

    batch_id = "batch001"
    services.add_batch(batch_id, "КРАСНЫЙ-КОВЕР", 100, None, uow)

    services.allocate("line001", "КРАСНЫЙ-КОВЕР", 10, uow)
    services.allocate("line002", "КРАСНЫЙ-КОВЕР", 20, uow)
    services.allocate("line003", "КРАСНЫЙ-КОВЕР", 30, uow)
    batch = uow.batches.get(reference=batch_id)
    assert batch.available_quantity == 40
    services.deallocate(batch_id, "line001", "КРАСНЫЙ-КОВЕР", 10, uow)
    services.deallocate(batch_id, "line002", "КРАСНЫЙ-КОВЕР", 20, uow)
    services.deallocate(batch_id, "line003", "КРАСНЫЙ-КОВЕР", 30, uow)
    assert batch.available_quantity == 100


@pytest.mark.parametrize(
    'unallocated_order',
    [
        ({'orderid': "line1", 'sku': "ВИНТАЖНАЯ-СОФА", 'qty': 30}),
        ({'orderid': "line2", 'sku': "БЕЛАЯ-ПОЛКА", 'qty': 40}),
        ({'orderid': "line3", 'sku': "ПУШИСТЫЙ-ПУФИК", 'qty': 90}),
    ]
)
def test_trying_to_deallocate_unallocated_batch(unallocated_order):
    uow = FakeUnitOfWork()
    batch_id = "batch001"
    orderid, sku, qty = unallocated_order.values()
    services.add_batch(batch_id, "КРАСНЫЙ-КОВЕР", 100, None, uow)
    batch = uow.batches.get(reference=batch_id)
    assert batch.available_quantity == 100
    services.deallocate(batch_id, orderid, sku, qty, uow)
    assert batch.available_quantity == 100
