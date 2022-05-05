from datetime import datetime

from flask import Flask, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.allocation.adapters import orm
from src.allocation.config import get_config
from src.allocation.domain import model
from src.allocation.service_layer import services, unit_of_work

orm.start_mappers()
engine = create_engine(get_config().postgres_uri)
get_session = sessionmaker(bind=engine)
app = Flask(__name__)


@app.route("/add_batch", methods=["POST"])
def add_batch():
    eta = request.json["eta"]
    if eta is not None:
        eta = datetime.fromisoformat(eta).date()
    services.add_batch(
        request.json["ref"],
        request.json["sku"],
        request.json["qty"],
        eta,
        uow=unit_of_work.SqlAlchemyUnitOfWork()
    )
    return "OK", 201


@app.route("/allocate", methods=["POST"])
def allocate_endpoint() -> tuple:
    try:
        batchref = services.allocate(
            request.json["orderid"],
            request.json["sku"],
            request.json["qty"],
            unit_of_work.SqlAlchemyUnitOfWork(),
        )
    except (model.OutOfStock, services.InvalidSku) as e:
        return {"message": str(e)}, 400

    return {"batchref": batchref}, 201
