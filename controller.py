import datetime
from uuid import UUID

from sqlalchemy import MetaData, Table, create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import operators

from models import Contract, Customer, CustomerRepresentative, Event
from utils import hash_password, verify_password
from view import LoginView, MainView


class LoginController:

    def __init__(self):
        self.engine = create_engine("sqlite:///mydb.db", echo=True)
        self.Session = sessionmaker(bind=self.engine)
        self.metadata = MetaData()
        self.session = self.Session()

    def login(self):

        login_view = LoginView()
        email, password = login_view.get_credentials()
        user = self.session.query(CustomerRepresentative).filter_by(email=email).one()
        password_verified = verify_password(password, user.password)

        return password_verified, user


class DataBaseController:

    def __init__(self):
        self.engine = create_engine("sqlite:///mydb.db", echo=True)
        self.Session = sessionmaker(bind=self.engine)
        self.metadata = MetaData()
        self.session = self.Session()

    def delete_item(self, table, item_id):

        object_id = UUID(item_id)

        try:
            table_class = self._get_table_class(table)
            item = self.session.query(table_class).get(object_id)

            if item is None:
                raise ValueError(
                    f"L'objet avec l'ID {object_id} n'existe pas dans la table {table}."
                )

            self.session.delete(item)

            self.session.commit()

        except IntegrityError as error:
            self.session.rollback()
            print(f"Violation de contrainte de clé étrangère : {error}")
        except Exception as e:
            self.session.rollback()
            print(f"Une erreur est survenue : {e}")
        finally:
            self.session.close()

    def _get_table_class(self, table_name):
        table_mapping = {
            "customer": Customer,
            "customer_representative": CustomerRepresentative,
            "contract": Contract,
            "event": Event,
        }

        return table_mapping.get(table_name)

    def list_item(self, table_name, user):

        try:
            table = Table(table_name, self.metadata, autoload_with=self.engine)

            if table_name == "customer_representative":
                query = self.session.query(table).filter(table.c.id == user.id)
            else:
                query = self.session.query(table).filter(
                    table.c.customer_representative_id == user.id
                )

            item_list = query.all()
            return item_list

        finally:
            self.session.close()

    def filter_unpaid_contracts(self, user):

        try:
            table = Table("contract", self.metadata, autoload_with=self.engine)

            query = (
                self.session.query(table)
                .filter(table.c["amount_due"] > 0)
                .filter(table.c["customer_representative_email"] == user.email)
            )
            item_list = query.all()
            return item_list

        finally:
            self.session.close()

    def filter_events(self, when, user):

        now = datetime.date.today()

        operator_map = {">=": operators.ge, "<=": operators.le}

        op = operator_map[when]

        try:
            table = Table("event", self.metadata, autoload_with=self.engine)

            query = (
                self.session.query(table)
                .filter(op(table.c["event_date_start"], now))
                .filter(table.c["customer_representative_id"] == user.id)
            )
            item_list = query.all()

            return item_list

        finally:
            self.session.close()

    def dynamic_search(self, table_name, data_filter, value, user):

        table = Table(table_name, self.metadata, autoload_with=self.engine)
        query = (
            self.session.query(table)
            .filter(table.c[data_filter].ilike(f"%{value}%"))
            .filter(table.c.customer_representative_id == user.id)
        )
        dataset = query.all()

        self.session.close()

        return dataset


class ModelsController:

    def __init__(self):
        self.database_controller = DataBaseController()
        self.session = self.database_controller.session

    def create_customer_representative(self, customer_representative_infos):

        hashed_password = hash_password(customer_representative_infos["password"])

        customer_representative = CustomerRepresentative(
            last_name=customer_representative_infos["last_name"],
            first_name=customer_representative_infos["first_name"],
            email=customer_representative_infos["email"],
            phone_number=customer_representative_infos["phone_number"],
            password=hashed_password,
        )

        self.database_controller.session.add(customer_representative)
        self.session.commit()

        return customer_representative

    def create_customer(self, customer_infos, user):

        now = datetime.date.today()
        customer_representative_object = self.session.get(
            CustomerRepresentative, user.id
        )

        customer = Customer(
            last_name=customer_infos["last_name"],
            first_name=customer_infos["first_name"],
            email=customer_infos["email"],
            phone_number=customer_infos["phone_number"],
            company_name=customer_infos["company_name"],
            date_created=now,
            date_modified=now,
            customer_representative=customer_representative_object,
        )

        self.session.add(customer)
        self.session.commit()

        return customer

    def create_contract(self, contract_infos, user):

        print(contract_infos)

        now = datetime.date.today()

        customer_representative_object = self.session.get(
            CustomerRepresentative, user.id
        )

        customer = contract_infos["customer"]
        customer_id = UUID(customer[0])
        customer_object = self.session.get(Customer, customer_id)

        print(f"!!! ICI !!! {customer}")

        contract = Contract(
            name=contract_infos["name"],
            total_amount=contract_infos["total_amount"],
            amount_due=contract_infos["amount_due"],
            status=contract_infos["status"],
            date_created=now,
            customer_representative=customer_representative_object,
            customer_representative_email=customer_representative_object.email,
            customer=customer_object,
            customer_email=customer_object.email,
        )

        self.session.add(contract)
        self.session.commit()

    def create_event(self, event_infos, contract):

        customer_id = UUID(contract.customer_id)
        customer_representative_id = UUID(contract.customer_representative_id)
        contract_id = UUID(contract.id)

        customer = self.session.query(Customer).filter_by(id=customer_id).one()
        customer_representative = (
            self.session.query(CustomerRepresentative)
            .filter_by(id=customer_representative_id)
            .one()
        )
        contract_instance = self.session.query(Contract).filter_by(id=contract_id).one()

        event_date_start = datetime.datetime.strptime(
            event_infos["event_date_start"], "%Y-%m-%d"
        ).date()
        event_date_end = datetime.datetime.strptime(
            event_infos["event_date_end"], "%Y-%m-%d"
        ).date()

        event = Event(
            name=event_infos["name"],
            customer=customer,
            customer_email=customer.email,
            customer_representative=customer_representative,
            customer_representative_email=customer_representative.email,
            event_date_start=event_date_start,
            event_date_end=event_date_end,
            location=event_infos["location"],
            attendees=event_infos["attendees"],
            notes=event_infos["notes"],
            contract=contract_instance,
        )

        self.session.add(event)
        self.session.commit()

    def edit_customer(self, customer_to_edit):
        customer_editable_fields = {
            "last_name": customer_to_edit[1],
            "first_name": customer_to_edit[2],
            "phone_number": customer_to_edit[3],
            "company_name": customer_to_edit[4],
            # 'customer_representative': customer_to_edit[7],
            "email": customer_to_edit[8],
        }

        customer_id = UUID(customer_to_edit[0])

        customer = self.session.get(Customer, customer_id)

        if not customer:
            raise ValueError(f"Customer with ID {customer_id} does not exist.")

        for key in customer_editable_fields.keys():
            new_value = MainView.input_update_view(customer, key)
            if new_value:
                setattr(customer, key, new_value)

        customer.date_modified = datetime.datetime.today()

        self.session.commit()

    def edit_contract_object(self, contract_to_edit):
        contract_editable_fields = {
            "name": contract_to_edit[1],
            "total_amount": contract_to_edit[2],
            "amount_due": contract_to_edit[3],
            "status": contract_to_edit[4],
        }

        contract_id = UUID(contract_to_edit[0])

        contract = self.session.get(Contract, contract_id)

        if not contract:
            raise ValueError(f"Contract with ID {contract_id} does not exist.")

        for key in contract_editable_fields.keys():
            new_value = MainView.input_update_view(contract, key)
            if new_value:
                setattr(contract, key, new_value)

        self.session.commit()

    def edit_event_object(self, event_to_edit):
        event_editables = {
            "name": event_to_edit[0],
            "event_date_start": event_to_edit[6],
            "event_date_end": event_to_edit[7],
            "location": event_to_edit[8],
            "attendees": event_to_edit[9],
            "notes": event_to_edit[10],
        }

        event_id = UUID(event_to_edit[1])
        event = self.session.get(Event, event_id)

        if not event:
            raise ValueError(f"Event with ID {event_id} does not exist.")

        for key in event_editables.keys():
            new_value = MainView.input_update_view(event, key)
            if new_value:
                setattr(event, key, new_value)

        self.session.commit()
