import pytest

from service_layer import services


def test_add_batch(fake_repo, fake_session):
    services.add_batch("b1", "СКРИПУЧЕЕ-КРЕСЛО", 100, None, fake_repo, fake_session)
    assert fake_repo.get("b1") is not None
    assert fake_session.committed


def test_allocate_returns_allocation(fake_repo, fake_session):
    services.add_batch("batch1", "КРУТАЯ-ЛАМПА", 100, None, fake_repo, fake_session)
    result = services.allocate("o1", "КРУТАЯ-ЛАМПА", 10, fake_repo, fake_session)
    assert result == "batch1"


def test_allocate_errors_for_invalid_sku(fake_repo, fake_session):
    services.add_batch("b1", "НЕДОПУСТИМЫЙ-SKU", 100, None, fake_repo, fake_session)

    with pytest.raises(services.InvalidSku, match="Invalid sku НЕСУЩЕСТВУЮЩИЙ"):
        services.allocate("o1", "НЕСУЩЕСТВУЮЩИЙ-SKU", 10, fake_repo, fake_session)


def test_commits(fake_repo, fake_session):
    services.add_batch("b1", "ЗЛОВЕЩЕЕ-ЗЕРКАЛО", 100, None, fake_repo, fake_session)
    services.allocate("o1", "ЗЛОВЕЩЕЕ-ЗЕРКАЛО", 10, fake_repo, fake_session)
    assert fake_session.committed is True


def test_deallocate_decrements_available_quantity(fake_repo, fake_session):
    batch_id = "batch001"
    services.add_batch(batch_id, "СИНИЙ-ПЛИНТУС", 100, None, fake_repo, fake_session)
    services.allocate('line001', 'СИНИЙ-ПЛИНТУС', 10, repo=fake_repo, session=fake_session)
    batch = fake_repo.get(reference=batch_id)
    assert batch.available_quantity == 90
    services.deallocate('line001', 'СИНИЙ-ПЛИНТУС', 10, batch=batch, session=fake_session)
    assert batch.available_quantity == 100


def test_deallocate_decrements_correct_quantity(fake_repo, fake_session):
    batch_id = "batch001"
    services.add_batch(batch_id, "КРАСНЫЙ-КОВЕР", 100, None, fake_repo, fake_session)

    services.allocate("line001", "КРАСНЫЙ-КОВЕР", 10, repo=fake_repo, session=fake_session)
    services.allocate("line002", "КРАСНЫЙ-КОВЕР", 20, repo=fake_repo, session=fake_session)
    services.allocate("line003", "КРАСНЫЙ-КОВЕР", 30, repo=fake_repo, session=fake_session)
    batch = fake_repo.get(reference=batch_id)
    assert batch.available_quantity == 40
    services.deallocate("line001", "КРАСНЫЙ-КОВЕР", 10, batch=batch, session=fake_session)
    services.deallocate("line002", "КРАСНЫЙ-КОВЕР", 20, batch=batch, session=fake_session)
    services.deallocate("line003", "КРАСНЫЙ-КОВЕР", 30, batch=batch, session=fake_session)
    assert batch.available_quantity == 100


@pytest.mark.parametrize(
    'unallocated_order',
    [
        ({'orderid': "line1", 'sku': "ВИНТАЖНАЯ-СОФА", 'qty': 30}),
        ({'orderid': "line2", 'sku': "БЕЛАЯ-ПОЛКА", 'qty': 40}),
        ({'orderid': "line3", 'sku': "ПУШИСТЫЙ-ПУФИК", 'qty': 90}),
    ]
)
def test_trying_to_deallocate_unallocated_batch(fake_repo, fake_session, unallocated_order):
    batch_id = "batch001"
    orderid, sku, qty = unallocated_order.values()
    services.add_batch(batch_id, "КРАСНЫЙ-КОВЕР", 100, None, fake_repo, fake_session)
    batch = fake_repo.get(reference=batch_id)
    assert batch.available_quantity == 100
    services.deallocate(orderid=orderid, sku=sku, qty=qty, batch=batch, session=fake_session)
    assert batch.available_quantity == 100
