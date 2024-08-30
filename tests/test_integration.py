from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers
from controller import ModelsController
from models import Base, CustomerRepresentative, Customer, Contract, Event
from uuid import UUID


@pytest.fixture(scope="function")
def session():
    engine = create_engine('sqlite:///:memory:')
    Session = sessionmaker(bind=engine)
    session = Session()

    Base.metadata.create_all(engine)

    yield session

    session.close()


@pytest.fixture(scope="function")
def models_controller(session):
    controller = ModelsController()
    controller.session = session
    return controller


@pytest.fixture
def customer_representative(session):
    customer_representative = CustomerRepresentative(
        id=UUID('12345678-1234-5678-1234-567812345678'),
        first_name="RepFirstName",
        last_name="RepLastName",
        email="rep@example.com",
        phone_number="0137814598",
        password="123456".encode("utf-8")
    )

    session.add(customer_representative)
    session.commit()

    return customer_representative


@pytest.fixture
def customer_test(session, customer_representative):

    now = date.today()

    customer_test = Customer(
        last_name="CustomerLastName",
        first_name="CustomerFirstName",
        email="customer@email.test",
        phone_number="0123456789",
        company_name="CompanyTest",
        date_created=now,
        date_modified=now,
        customer_representative=customer_representative
    )

    session.add(customer_test)
    session.commit()

    return customer_test


@pytest.fixture
def contract_test(session, customer_representative, customer_test):

    now = date.today()

    contract_test = Contract(
        name="TestContractName",
        total_amount=750,
        amount_due=700,
        status="En cours",
        date_created=now,
        customer_representative=customer_representative,
        customer_representative_email=customer_representative.email,
        customer=customer_test,
        customer_email=customer_test.email
        )

    session.add(contract_test)
    session.commit()

    return contract_test


def test_presence_of_customer_representative(session, customer_representative):
    customer_representative_id = customer_representative.id
    retrieved_representative = session.get(CustomerRepresentative, customer_representative_id)

    assert retrieved_representative.first_name == "RepFirstName"


def test_presence_of_customer(session, customer_test):
    customer_test_id = customer_test.id
    retrieved_customer = session.get(Customer, customer_test_id)

    assert retrieved_customer.first_name == "CustomerFirstName"


def test_presence_of_contract(session, contract_test):
    contract_test_id = contract_test.id
    retrieved_contract = session.get(Contract, contract_test_id)

    assert retrieved_contract.name == "TestContractName"


def test_create_customer(session, customer_representative, models_controller):

    customer_infos = {
        'last_name': "CreatedLastName",
        'first_name': "CreatedFirstName",
        'email': "create@email.test",
        'phone_number': "01234567",
        'company_name': "CreatedCompanyName",
        'customer_representative': (str(customer_representative.id),)
    }

    customer_instance = models_controller.create_customer(customer_infos)

    customer = session.query(Customer).filter_by(email="create@email.test").one()

    assert customer.first_name == "CreatedFirstName"
    assert customer.customer_representative == customer_representative


def test_create_contract(session, customer_representative, customer_test, models_controller):

    customer_representative_attrs = (str(customer_representative.id), customer_representative.last_name, customer_representative.first_name, customer_representative.email, customer_representative.phone_number, customer_representative.password)

    customer_attrs = (str(customer_test.id), customer_test.first_name, customer_test.last_name, customer_test.phone_number, customer_test.company_name, customer_test.date_modified, customer_test.date_created, customer_test.customer_representative_id, customer_test.email)

    contract_infos = {
            'name': "CreatedContractName",
            'total_amount': 1000,
            'amount_due': 500,
            'status': "En cours",
            'customer_representative': customer_representative_attrs,
            'customer': customer_attrs
        }

    contract_instance = models_controller.create_contract(contract_infos)

    contract = session.query(Contract).filter_by(name="CreatedContractName").one()

    assert contract.name == "CreatedContractName"
    assert contract.customer_representative == customer_representative


# def test_create_event(session, customer_representative, customer_test, contract_test, models_controller):

