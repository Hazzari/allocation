"""
customers - клиенты
order - заказ
order reference - ссылка на заказ, состоит из нескольких товарных позиций или order line
order line - строки заказа, уникальные строки состоящие из

batch - партия товара

allocate order line - товарная позиция заказа
warehouse stock - складской запас
eta - Предполагаемый срок прибытия партии
available quantity - располагаемое количество товара

sku - Единица складского учета
qty - количество
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import List


class OutOfStock(Exception):
    pass


def allocate(line: OrderLine, batches: List[Batch]) -> str:
    try:
        batch = next(b for b in sorted(batches) if b.can_allocate(line))
        batch.allocate(line)
        return batch.reference
    except StopIteration:
        raise OutOfStock(f"Нет в наличии: артикул - {line.sku}")


def deallocate(line: OrderLine, batch: Batch) -> None:
    batch.deallocate(line)


@dataclass(unsafe_hash=True)
class OrderLine:
    """Строка (позиция) заказа.

    Уникальное значение состоящее из id артикула и количества.
    """
    orderid: str
    sku: str
    qty: int


@dataclass()
class Batch:
    """Партия.

    Идентификатор состоит из ссылки, артикула и количества.
    """

    reference: str
    sku: str
    qty: int

    eta: date | None
    _allocations: set[OrderLine] = field(default_factory=set)

    def __post_init__(self):
        self._purchased_quantity = self.qty

    def __repr__(self):
        return f"<Batch {self.reference}>"

    def __eq__(self, other):
        if not isinstance(other, Batch):
            return False
        return other.reference == self.reference

    def __hash__(self):
        return hash(self.reference)

    def __gt__(self, other):
        if self.eta is None:
            return False
        if other.eta is None:
            return True
        return self.eta > other.eta

    def allocate(self, line: OrderLine):
        """Размещение OrderLine в текущей партии."""
        if self.can_allocate(line):
            self._allocations.add(line)

    def deallocate(self, line: OrderLine):
        """Удаление OrderLine из текущей партии."""
        if line in self._allocations:
            self._allocations.remove(line)

    @property
    def allocated_quantity(self) -> int:
        """Выделенное количество товара из партии."""
        return sum(line.qty for line in self._allocations)

    @property
    def available_quantity(self) -> int:
        """Доступное количество для выделения в заказы."""
        return self._purchased_quantity - self.allocated_quantity

    def can_allocate(self, line: OrderLine) -> bool:
        """Есть ли возможность выделить часть заказа."""
        return self.sku == line.sku and self.available_quantity >= line.qty
