from datetime import date

import pytest

from domain.model import Batch, OrderLine


@pytest.mark.parametrize(
    ('quantity_of_goods', 'order_position', 'result'),
    [
        (20, 2, 18),
        (100, 50, 50),
        (0, 2, 0),
    ]
)
def test_allocating_to_a_batch_reduces_the_available_quantity(quantity_of_goods, order_position, result):
    """Размещение в партии, уменьшает доступное количество."""
    batch = Batch("BATCH-001", "СТОЛ-МАЛЕНЬКИЙ", eta=date.today(), qty=quantity_of_goods)
    line = OrderLine("ORDER-REF", "СТОЛ-МАЛЕНЬКИЙ", order_position)

    batch.allocate(line)

    assert batch.available_quantity == result


def make_batch_and_line(sku: str, bath_qty: int, line_qty: int):
    return (
        Batch('bath-001', sku, bath_qty, eta=date.today()),
        OrderLine('order-100', sku, line_qty)
    )


def test_can_allocate_if_available_greater_than_required():
    large_batch, small_line = make_batch_and_line('ЭЛЕГАНТНАЯ-ЛАМПА', 20, 2)
    assert large_batch.can_allocate(small_line)


def test_cannot_allocate_if_available_smaller_than_required():
    small_batch, large_line = make_batch_and_line('ЭЛЕГАНТНАЯ-ЛАМПА', 2, 20)
    assert small_batch.can_allocate(large_line) is False


def test_can_allocate_if_available_equal_to_required():
    batch, line = make_batch_and_line('ЭЛЕГАНТНАЯ-ЛАМПА', 2, 2)
    assert batch.can_allocate(line)


def test_cannot_allocate_if_sku_do_not_match():
    batch = Batch('batch-001', 'НЕУДОБНОЕ-КРЕСЛО', 100, eta=None)
    different_sku_line = OrderLine('order-100', 'ДОРОГОЙ-ТОСТЕР', 10)
    assert batch.can_allocate(different_sku_line) is False


def test_can_only_deallocate_allocated_lines():
    """Отмена размещения не имеет никакого влияния если ранее не была размещена в этом заказ"""
    batch, unallocated_line = make_batch_and_line('ДЕКОРАТИВНОЕ-УКРАШЕНИЕ', 20, 2)
    batch.deallocate(unallocated_line)
    assert batch.available_quantity == 20
