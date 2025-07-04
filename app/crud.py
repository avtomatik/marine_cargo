from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from . import models, schemas


def bulk_create_bills(
    db: Session,
    bills: list[schemas.BillOfLadingCreate]
) -> None:
    bill_models = [models.BillOfLading(**bill.model_dump()) for bill in bills]
    db.bulk_save_objects(bill_models)
    db.commit()


def get_coverage(db: Session, coverage_id: int):
    return db.query(models.Coverage).filter(
        models.Coverage.id == coverage_id
    ).first()


def get_all_coverage(db: Session):
    return db.query(models.Coverage).all()


def create_coverage(
    db: Session,
    coverage_data: schemas.CoverageCreate
) -> models.Coverage:
    new_coverage = models.Coverage(**coverage_data.model_dump())
    db.add(new_coverage)
    db.commit()
    db.refresh(new_coverage)
    return new_coverage


def get_entity_by_name(db: Session, name: str):
    return db.query(models.Entity).filter(models.Entity.name == name).first()


def get_entity(db: Session, entity_id: int):
    return (
        db
        .query(models.Entity)
        .filter(models.Entity.id == entity_id)
        .first()
    )


def get_entities(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Entity).offset(skip).limit(limit).all()


def create_entity(db: Session, entity: schemas.EntityCreate):
    entity_data = entity.model_dump()
    db_entity = models.Entity(**entity_data)
    db.add(db_entity)
    try:
        db.commit()
        db.refresh(db_entity)
        return db_entity
    except IntegrityError:
        db.rollback()
        raise


def upsert_entity_by_name(db: Session, entity: schemas.EntityCreate):
    """
    Either update an existing entity by name or create a new one.
    """
    existing = get_entity_by_name(db, entity.name)
    entity_data = entity.model_dump()

    if existing:
        for key, value in entity_data.items():
            setattr(existing, key, value)
        db.commit()
        db.refresh(existing)
        return existing
    else:
        return create_entity(db, entity)


def get_or_create_operator(
    db: Session,
    operator_data: schemas.OperatorCreate
) -> models.Operator:
    operator = (
        db.query(models.Operator)
        .filter(
            models.Operator.first_name == operator_data.first_name,
            models.Operator.last_name == operator_data.last_name,
        )
        .first()
    )

    if operator:
        return operator

    operator = models.Operator(**operator_data.model_dump())
    db.add(operator)
    db.commit()
    db.refresh(operator)
    return operator


def upsert_port(db: Session, port: schemas.PortCreate) -> models.Port:
    stmt = select(models.Port).where(
        models.Port.name == port.name,
        models.Port.country == port.country
    )
    db_port = db.execute(stmt).scalar_one_or_none()

    if db_port:
        return db_port  # already exists

    # Create new port
    db_port = models.Port(name=port.name, country=port.country)
    db.add(db_port)
    db.commit()
    db.refresh(db_port)
    return db_port


def create_shipment(
    db: Session,
    shipment_data: schemas.ShipmentCreate
) -> models.Shipment:
    shipment = models.Shipment(**shipment_data.model_dump())
    db.add(shipment)
    db.commit()
    db.refresh(shipment)
    return shipment


def upsert_shipment(
    db: Session,
    shipment_data: schemas.ShipmentCreate
) -> models.Shipment:
    existing = db.query(models.Shipment).filter_by(
        deal_number=shipment_data.deal_number).first()

    if existing:
        for field, value in shipment_data.model_dump().items():
            setattr(existing, field, value)
        db.commit()
        db.refresh(existing)
        return existing
    else:
        new_shipment = models.Shipment(**shipment_data.model_dump())
        db.add(new_shipment)
        db.commit()
        db.refresh(new_shipment)
        return new_shipment


def get_vessel_by_imo(db: Session, imo: int):
    return (
        db
        .query(models.Vessel)
        .filter(models.Vessel.imo == imo)
        .one_or_none()
    )


def upsert_vessel(db: Session, vessel: schemas.VesselCreate):
    db_obj = db.query(models.Vessel).filter(
        models.Vessel.imo == vessel.imo
    ).first()

    vessel_data = vessel.model_dump()

    if db_obj:
        for key, value in vessel_data.items():
            setattr(db_obj, key, value)
    else:
        db_obj = models.Vessel(**vessel_data)
        db.add(db_obj)

    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_shipment_with_totals(db: Session, shipment_id: int):
    result = (
        db.query(
            models.Shipment.id,
            models.Shipment.deal_number,
            models.Shipment.disport_eta,
            func.coalesce(
                func.sum(models.BillOfLading.quantity_mt),
                0.0
            ).label('total_weight_mt'),
            func.coalesce(
                func.sum(models.BillOfLading.quantity_bbl),
                0.0
            ).label('total_volume_bbl'),
            func.coalesce(
                func.sum(models.BillOfLading.value),
                0.0
            ).label('total_value_usd'),
        )
        .join(
            models.BillOfLading,
            models.BillOfLading.shipment_id == models.Shipment.id
        )
        .filter(models.Shipment.id == shipment_id)
        .group_by(models.Shipment.id)
        .first()
    )

    if result:
        return {
            'id': result.id,
            'deal_number': result.deal_number,
            'disport_eta': result.disport_eta,
            'total_weight_mt': result.total_weight_mt,
            'total_volume_bbl': result.total_volume_bbl,
            'total_value_usd': result.total_value_usd,
        }
    return None
