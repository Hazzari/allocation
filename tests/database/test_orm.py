from app.model import OrderLine


def test_orderline_mapper_can_load_lines(session):
    session.execute(
        "INSERT INTO order_lines (orderid, sku, qty) VALUES "
        "('order1','КРАСНЫЙ-СТУЛ',  12),"
        "('order1','КРАСНЫЙ-СТОЛ',  13),"
        "('order2','СИНЕЕ-ЗЕРКАЛО', 14)"
    )
    expected = [
        OrderLine('order1', 'КРАСНЫЙ-СТУЛ', 12),
        OrderLine('order1', 'КРАСНЫЙ-СТОЛ', 13),
        OrderLine('order2', 'СИНЕЕ-ЗЕРКАЛО', 14),
    ]

    assert list(session.query(OrderLine).all()) == expected
    # assert session.query(OrderLine).all() == expected
