from __future__ import annotations

from datetime import date
from typing import Optional

from adapters.repository import AbstractRepository
from domain import model
from domain.model import OrderLine


class InvalidSku(Exception):
    pass


def is_valid_sku(sku, batches) -> bool:
    return sku in {b.sku for b in batches}


def add_batch(
    ref: str, sku: str, qty: int, eta: Optional[date],
    repo: AbstractRepository, session,
) -> None:
    repo.add(model.Batch(ref, sku, qty, eta))
    session.commit()


def allocate(orderid: str, sku: str, qty: int, repo: AbstractRepository, session) -> str:
    line = OrderLine(orderid, sku, qty)
    batches = repo.list()
    if not is_valid_sku(line.sku, batches):
        raise InvalidSku(f"Invalid sku {line.sku}")
    batchref = model.allocate(line, batches)
    session.commit()
    return batchref


def deallocate(orderid: str, sku: str, qty: int, batch, session):
    line = OrderLine(orderid, sku, qty)
    model.deallocate(line, batch)
    session.commit()
