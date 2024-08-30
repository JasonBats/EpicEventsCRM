from datetime import datetime, date
from uuid import UUID
import psycopg2
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import operators
from utils import hash_password, verify_password
from view import LoginView, MainView, ConsoleView
import jwt
from models import Customer, Base, CustomerRepresentative, Contract, Event


class LoginController:

    def login(self):
        login_view = LoginView()
        host = "localhost"
        database = "test"
        # user, password = login_view.get_credentials()
        user = "test_user"  # Comment to login
        password = "admin123"  # Comment to login

        return host, database, user, password  # TODO : Login sur la bonne DB


class DataBaseController:

    def __init__(self):
        self.engine = create_engine("sqlite:///mydb.db", echo=True)
        self.Session = sessionmaker(bind=self.engine)
        self.metadata = MetaData()

    login_controller = LoginController()
    host, database, user, password = login_controller.login()

    def connect_to_database(self):

        conn = psycopg2.connect(
            host=self.host,
            database=self.database,
            user=self.user,  # postgres
            password=self.password  # aCuN2ahb*
        )

        return conn

    def delete_item(self, table, item_id):

        session = self.Session()
        object_id = UUID(item_id)

        try:
            table_class = self._get_table_class(table)
            item = session.query(table_class).get(object_id)

            if item is None:
                raise ValueError(f"L'objet avec l'ID {object_id} n'existe pas dans la table {table}.")

            session.delete(item)

            session.commit()

        except IntegrityError as error:
            session.rollback()
            print(f"Violation de contrainte de clé étrangère : {error}")
        except Exception as e:
            session.rollback()
            print(f"Une erreur est survenue : {e}")
        finally:
            session.close()

    def _get_table_class(self, table_name):
        table_mapping = {
            "customer": Customer,
            "customer_representative": CustomerRepresentative,
            "contract": Contract,
            "event": Event
        }

        return table_mapping.get(table_name)

    def list_item(self, table_name):

        session = self.Session()  # TODO : Raccourcir avec session.query(Model...)

        try:
            table = Table(table_name, self.metadata, autoload_with=self.engine)

            query = session.query(table)
            item_list = query.all()
            return item_list

        finally:
            session.close()

    def filter_unpaid_contracts(self):

        session = self.Session()

        try:
            table = Table("contract", self.metadata, autoload_with=self.engine)

            query = session.query(table).filter(table.c["amount_due"] > 0)
            item_list = query.all()
            return item_list

        finally:
            session.close()

    def filter_events(self, when):

        session = self.Session()
        now = date.today()

        operator_map = {
            ">=": operators.ge,
            "<=": operators.le
        }

        op = operator_map[when]

        try:
            table = Table("event", self.metadata, autoload_with=self.engine)

            query = session.query(table).filter(op(table.c["event_date_start"], now))
            item_list = query.all()

            return item_list

        finally:
            session.close()

    def dynamic_search(self, table_name, data_filter, value):
        session = self.Session()

        table = Table(table_name, self.metadata, autoload_with=self.engine)
        query = session.query(table).filter(table.c[data_filter].ilike(f"%{value}%"))
        dataset = query.all()

        session.close()

        return dataset


class ModelsController:

    """

    A l'initialisation : Ouvrir la db + session (pour remplacer db controller et réutiliser à chaque fonction)
    à la fin de chaque fonction : ajout en db
    (fermer la session qu'en quittant le programme ? A voir)

    """

    def __init__(self):
        engine = create_engine("sqlite:///mydb.db", echo=True)
        Base.metadata.create_all(bind=engine)

        Session = sessionmaker(bind=engine)
        self.session = Session()

    def create_customer(self, customer_infos):

        now = date.today()
        customer_representative = customer_infos["customer_representative"]
        print(customer_representative)
        customer_representative_id = UUID(customer_representative[0])
        print(customer_representative_id)
        customer_representative_object = self.session.get(CustomerRepresentative, customer_representative_id)

        customer = Customer(last_name=customer_infos["last_name"],
                            first_name=customer_infos["first_name"],
                            email=customer_infos["email"],
                            phone_number=customer_infos["phone_number"],
                            company_name=customer_infos["company_name"],
                            date_created=now,
                            date_modified=now,
                            customer_representative=customer_representative_object)

        self.session.add(customer)
        self.session.commit()

        return customer

    def create_contract(self, contract_infos):

        print(contract_infos)

        now = date.today()

        customer_representative = contract_infos["customer_representative"]
        customer_representative_id = UUID(customer_representative[0])
        customer_representative_object = self.session.get(CustomerRepresentative, customer_representative_id)

        customer = contract_infos["customer"]
        customer_id = UUID(customer[0])
        customer_object = self.session.get(Customer, customer_id)

        print(f"!!! ICI !!! {customer}")

        contract = Contract(name=contract_infos["name"],
                            total_amount=contract_infos["total_amount"],
                            amount_due=contract_infos["amount_due"],
                            status=contract_infos["status"],
                            date_created=now,
                            customer_representative=customer_representative_object,
                            customer_representative_email=customer_representative_object.email,
                            customer=customer_object,
                            customer_email=customer_object.email
                            )

        self.session.add(contract)
        self.session.commit()

    def create_event(self, event_infos, contract):

        customer_id = UUID(contract.customer_id)
        customer_representative_id = UUID(contract.customer_representative_id)
        contract_id = UUID(contract.id)

        customer = self.session.query(Customer).filter_by(id=customer_id).one()
        customer_representative = self.session.query(CustomerRepresentative).filter_by(id=customer_representative_id).one()
        contract_instance = self.session.query(Contract).filter_by(id=contract_id).one()

        event_date_start = datetime.strptime(event_infos["event_date_start"], "%Y-%m-%d").date()
        event_date_end = datetime.strptime(event_infos["event_date_end"], "%Y-%m-%d").date()

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
            contract=contract_instance
        )

        self.session.add(event)
        self.session.commit()

    def edit_customer(self, customer_to_edit):
        customer_editable_fields = {
            'last_name': customer_to_edit[1],
            'first_name': customer_to_edit[2],
            'phone_number': customer_to_edit[3],
            'company_name': customer_to_edit[4],
            # 'customer_representative': customer_to_edit[7],
            'email': customer_to_edit[8]
        }

        customer_id = UUID(customer_to_edit[0])

        customer = self.session.get(Customer, customer_id)

        if not customer:
            raise ValueError(f"Customer with ID {customer_id} does not exist.")

        for key in customer_editable_fields.keys():
            new_value = MainView.input_update_view(customer, key)
            if new_value:
                setattr(customer, key, new_value)

        customer.date_modified = datetime.today()

        self.session.commit()

    def edit_contract_object(self, contract_to_edit):
        contract_editable_fields = {
            'name': contract_to_edit[1],
            'total_amount': contract_to_edit[2],
            'amount_due': contract_to_edit[3],
            'status': contract_to_edit[4],
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
            'name': event_to_edit[0],
            'event_date_start': event_to_edit[6],
            'event_date_end': event_to_edit[7],
            'location': event_to_edit[8],
            'attendees': event_to_edit[9],
            'notes': event_to_edit[10],
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
