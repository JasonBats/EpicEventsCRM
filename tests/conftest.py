import os
from datetime import date, datetime
from uuid import UUID

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from models import Base, CustomerRepresentative, Customer, Contract, Event


@pytest.fixture
def engine():
    engine = create_engine("sqlite:///test.db", echo=True)
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def session(engine):
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def new_customer_representative(session):
    customer_representative = CustomerRepresentative(
        id=UUID("12345678-1234-5678-1234-567812345678"),
        first_name="RepFirstName",
        last_name="RepLastName",
        email="rep@example.com",
        phone_number="0137814598",
        password="123456".encode("utf-8"),
        is_admin=0,
    )

    session.add(customer_representative)
    session.commit()
    session.refresh(customer_representative)

    return customer_representative


@pytest.fixture
def new_customer(session, new_customer_representative):
    now = date.today()

    customer = Customer(
        last_name="CustomerLastName",
        first_name="CustomerFirstName",
        email="customer@email.test",
        phone_number="0123456789",
        company_name="CompanyTest",
        date_created=now,
        date_modified=now,
        customer_representative=new_customer_representative,
    )

    session.add(customer)
    session.commit()
    session.refresh(customer)

    return customer


@pytest.fixture
def new_contract(session, new_customer_representative, new_customer):
    now = date.today()

    contract = Contract(
        name="TestContractName",
        total_amount=750,
        amount_due=700,
        status="En cours",
        date_created=now,
        customer_representative=new_customer_representative,
        customer_representative_email=new_customer_representative.email,
        customer=new_customer,
        customer_email=new_customer.email,
    )

    session.add(contract)
    session.commit()
    session.refresh(contract)

    return contract


@pytest.fixture
def new_event(session, new_contract):

    event = Event(
        name="TestEventName",
        customer=new_contract.customer,
        customer_email=new_contract.customer.email,
        customer_representative=new_contract.customer_representative,
        customer_representative_email=new_contract.customer_representative.email,
        event_date_start=datetime.strptime("2025-09-09", "%Y-%m-%d"),
        event_date_end=datetime.strptime("2025-09-09", "%Y-%m-%d"),
        location="TestEventLocation",
        attendees=42,
        notes="",
        contract=new_contract,
    )

    session.add(event)
    session.commit()
    session.refresh(event)

    return event


@pytest.fixture(autouse=True)
def drop_db(engine):
    yield
    # Ensure the engine is disposed of before removing the file
    engine.dispose()
    try:
        os.remove("test.db")
    except FileNotFoundError:
        pass
