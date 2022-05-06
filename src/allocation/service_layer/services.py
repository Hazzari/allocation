from __future__ import annotations

from datetime import date
from typing import Optional

from src.allocation.domain import model
from src.allocation.domain.model import OrderLine
from src.allocation.service_layer.unit_of_work import AbstractUnitOfWork


class InvalidSku(Exception):
    pass


def is_valid_sku(sku, batches) -> bool:
    """Проверка валидности единицы складского учета."""
    return sku in {b.sku for b in batches}


def add_batch(ref: str, sku: str, qty: int, eta: Optional[date], uow: AbstractUnitOfWork):
    """Создание партии определенного товара."""
    with uow:
        uow.batches.add(model.Batch(ref, sku, qty, eta))
        uow.commit()


def allocate(orderid: str, sku: str, qty: int, uow: AbstractUnitOfWork) -> str:
    """Размещение в партии товара определенной позиции."""
    line = OrderLine(orderid, sku, qty)
    with uow:
        batches = uow.batches.list()
        if not is_valid_sku(line.sku, batches):
            raise InvalidSku(f"Invalid sku {line.sku}")
        batchref = model.allocate(line, batches)
        uow.commit()
    return batchref


def deallocate(reference, orderid: str, sku: str, qty: int, uow: AbstractUnitOfWork):
    """Удаление из партии товара определенной позиции."""
    line = OrderLine(orderid, sku, qty)
    with uow:
        batch = uow.batches.get(reference)
        model.deallocate(line, batch)
        uow.commit()
