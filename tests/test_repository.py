from app import repository
from app.model import Batch


def test_repository_can_save_a_batch(session):
    batch = Batch('batch1', 'ИЗЫСКАННАЯ-СКАМЕЙКА', 100, eta=None)

    repo = repository.SqlAlchemyRepository(session)
    repo.add(batch)

    session.commit()

    rows = list(
        session.execute(
            'SELECT reference, sku, _purchased_quantity, eta FROM "batches"'
        )
    )
    assert rows == [('batch1', 'ИЗЫСКАННАЯ-СКАМЕЙКА', 100, None)]
