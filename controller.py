import datetime
from typing import Type, Tuple, Optional

from dotenv import load_dotenv
from sqlalchemy import MetaData, Table, create_engine, select
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import operators

from models import Contract, Customer, CustomerRepresentative, Event
from utils import hash_password, verify_password, save_token_in_file
from view import LoginView, MainView

load_dotenv()


class LoginController:

    def __init__(self):
        self.engine = create_engine("sqlite:///mydb.db")
        self.Session = sessionmaker(bind=self.engine)
        self.metadata = MetaData()
        self.session = self.Session()

    def login(self) -> Tuple[bool, Optional[Type[CustomerRepresentative]]]:  # TODO : Généraliser ça
        """
        Authenticates a user by verifying their email and password, and
        generates a JWT token for session management.

        This method prompts the user for their email and password through the
        `LoginView` interface. It then attempts to find a
        `CustomerRepresentative` in the database with the provided email.
        If a user is found, it verifies the provided password against the
        stored hashed password. Upon successful authentication, it generates
        a JSON Web Token (JWT) containing the user ID and an expiration date,
        which is saved to a file named “.credentials” for session management.
        :return: password_verified (Boolean), user (CustomerRepresentative)
        """
        login_view = LoginView()
        email, password = login_view.get_credentials()
        try:
            user = self.session.query(CustomerRepresentative).filter_by(
                email=email).one()
            password_verified = verify_password(password, user.password)
            save_token_in_file(user)
        except NoResultFound:
            user = None
            password_verified = False

        return password_verified, user


class DataBaseController:

    def __init__(self):
        self.engine = create_engine("sqlite:///mydb.db")
        self.Session = sessionmaker(bind=self.engine)
        self.metadata = MetaData()
        self.session = self.Session()

    def delete_item(self, table, item_id):
        """
        Deletes an item from a specified table in the database by its ID.

        This method attempts to delete an item identified by `item_id` from
        the specified `table`. It first retrieves the table class using
        `_get_table_class()` and then queries for the item with the given ID.
        If the item exists, it is deleted from the session and changes are
        committed to the database. If the item is not found or a constraint
        violation occurs, appropriate error messages are printed, and the
        session is rolled back to maintain data integrity.

        :param table
        :param item_id
        """
        try:
            item = self.session.execute(
                select(table).where(table.id == item_id)
            ).scalars().one_or_none()
            if item is None:
                raise ValueError(
                    f"L'objet avec l'ID {item_id} n'existe pas dans la table {table}."
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
        """
        Retrieves the SQLAlchemy model class associated with the specified
        table name.

        This method provides a mapping between table names and their
        corresponding SQLAlchemy model classes. It returns the model class
        for the given `table_name` from the `table_mapping` dictionary.
        """
        table_mapping = {
            "customer": Customer,
            "customer_representative": CustomerRepresentative,
            "contract": Contract,
            "event": Event,
        }

        return table_mapping.get(table_name)

    def list_item(self, table_name, user):
        """
        Retrieves a list of items from the specified table based on user
        permissions.

        This method queries the specified table to return a list of items.
        The results returned depend on the user's role:
        — If the user is an admin, all items from the table are retrieved.
        — If the user is not an admin, the items are filtered based on the
        user's ID.
        :param table_name
        :param user
        :return: item_list
        """

        try:
            if user.is_admin:
                query = select(table_name)
            else:
                if table_name == CustomerRepresentative:
                    query = select(table_name).where(id == user.id)
                else:
                    query = select(table_name).filter(
                        table_name.customer_representative_id == user.id
                    )

            item_list = self.session.scalars(query).all()
            return item_list

        finally:
            self.session.close()

    def filter_unpaid_contracts(self, user):
        """
        Retrieves a list of unpaid contracts based on the user's role and
        permissions.
        :param user
        :return: item_list
        """
        try:
            table = Table("contract", self.metadata, autoload_with=self.engine)

            if user.is_admin:
                query = self.session.query(table)
            else:
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
        """
        Retrieves a list of events based on the date and user's role and
        permissions.
        :param user
        :param when
        :return: item_list
        """
        now = datetime.date.today()

        operator_map = {">=": operators.ge, "<=": operators.le}

        op = operator_map[when]

        try:
            if user.is_admin:
                query = select(Event).where(op(Event.event_date_start, now))
            else:
                query = select(Event).join(
                    CustomerRepresentative,
                    Event.customer_representative_id == CustomerRepresentative.id
                ).where(
                    op(Event.event_date_start, now),
                    CustomerRepresentative.id == user.id
                )

            item_list = self.session.scalars(query).all()

            return item_list

        finally:
            self.session.close()

    def dynamic_search(self, table_name, data_filter, value, user):
        """
        Performs a dynamic search on a specified table based on a filter and
        value, considering the user's role.

        This method queries the specified table using the provided filter and
        value. The results depend on the user's role:
        — If the user is an admin, the search is performed across all records
        in the table.
        — If the user is not an admin, the search is restricted to records
        associated with the user's ID.
        """
        table = Table(table_name, self.metadata, autoload_with=self.engine)
        if user.is_admin:
            query = select(table).where(table.c[data_filter].ilike(f"%{value}%"))
        else:
            query = select(table).where(
                table.c[data_filter].ilike(f"%{value}%"),
                table.c['customer_representative_id'] == user.id
            )

        dataset = self.session.execute(query)
        self.session.close()

        return dataset.fetchall()


class ModelsController:

    def __init__(self):
        self.database_controller = DataBaseController()
        self.session = self.database_controller.session

    def create_customer_representative(self, customer_representative_infos):
        """
        Creates and stores a new CustomerRepresentative in the database.

        This method takes a dictionary of information for a new customer representative,
        hashes the password, and then creates and saves an instance of the
        `CustomerRepresentative` class with the provided details. The new instance
        is added to the session and committed to the database.
        :param customer_representative_infos:
        :return: CustomerRepresentative: The newly created
        CustomerRepresentative's instance
        """

        hashed_password = hash_password(customer_representative_infos["password"])

        customer_representative = CustomerRepresentative(
            last_name=customer_representative_infos["last_name"],
            first_name=customer_representative_infos["first_name"],
            email=customer_representative_infos["email"],
            phone_number=customer_representative_infos["phone_number"],
            password=hashed_password,
            is_admin=0,
        )

        self.session.add(customer_representative)
        self.session.commit()

        return customer_representative

    def create_customer(self, customer_infos, user):
        """
        Creates and stores a new Customer in the database.

        This method takes a dictionary of customer information and the user
        creating the customer. It then creates a new `Customer` instance using
        the provided details, associates it with the customer representative,
        and saves it to the database.
        :param customer_infos:
        :param user:
        :return: Customer: The newly created Customer's instance.
        """

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
        """
        Creates and stores a new Contract in the database.

        This method takes a dictionary of contract information and the user
        object of the customer representative creating the contract. It then
        creates a new `Contract` instance using the provided details,
        associates it with the customer representative and customer, and saves
        it to the database.
        :param contract_infos
        :param user
        :return: Contract: The newly created Contract's instance.
        """

        now = datetime.date.today()

        customer_representative_object = self.session.get(
            CustomerRepresentative, user.id
        )

        customer = contract_infos["customer"]
        customer_id = customer.id
        customer_object = self.session.get(Customer, customer_id)

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

        return contract

    def create_event(self, event_infos, contract):
        """
        Creates and stores a new Event in the database.

        This method takes a dictionary of event information and a `Contract`
        object, retrieves related `Customer` and `CustomerRepresentative` from
        the database, and creates a new `Event` instance with the provided
        details. The event is then saved to the database.
        :param event_infos:
        :param contract:
        :return: Event: The newly created Event's instance.
        """
        customer_id = contract.customer_id
        customer_representative_id = contract.customer_representative_id
        contract_id = contract.id

        customer = self.session.query(Customer).filter_by(id=customer_id).one()
        customer_representative = (
            self.session.query(CustomerRepresentative)
            .filter_by(id=customer_representative_id)
            .one()
        )
        result = self.session.execute(select(Contract).where(
            Contract.id == contract_id)
        )
        contract_instance = result.scalar_one_or_none()

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

        return event

    def edit_customer(self, customer_to_edit):
        """
        Updates the details of an existing customer in the database.

        This method allows for editing specific fields of a `Customer` record
        based on the provided data. It retrieves the customer using the
        customer ID, updates the customer fields with new values provided by
        the user, and commits the changes to the database.
        :param customer_to_edit:
        """
        customer_editable_fields = {
            "last_name": customer_to_edit.last_name,
            "first_name": customer_to_edit.first_name,
            "phone_number": customer_to_edit.phone_number,
            "company_name": customer_to_edit.company_name,
            "email": customer_to_edit.email,
        }

        customer_id = customer_to_edit.id

        customer = self.session.get(Customer, customer_id)

        if not customer:
            raise ValueError(f"Customer with ID {customer_id} does not exist.")

        for key in customer_editable_fields.keys():
            new_value = MainView.input_update_view(customer, key)
            if new_value:
                setattr(customer, key, new_value)

        customer.date_modified = datetime.datetime.today()

        self.session.commit()

        return customer

    def edit_contract_object(self, contract_to_edit):
        """
        Updates the details of an existing contract in the database.

        This method allows for editing specific fields of a `Contract` record
        based on the provided data. It retrieves the contract using the
        contract ID, updates the contract fields with new values provided by
        the user, and commits the changes to the database.
        :param contract_to_edit:
        """
        contract_editable_fields = {
            "name": contract_to_edit.name,
            "total_amount": contract_to_edit.total_amount,
            "amount_due": contract_to_edit.amount_due,
            "status": contract_to_edit.status,
        }

        contract_id = contract_to_edit.id

        contract = self.session.get(Contract, contract_id)

        if not contract:
            raise ValueError(f"Contract with ID {contract_id} does not exist.")

        for key in contract_editable_fields.keys():
            new_value = MainView.input_update_view(contract, key)
            if new_value:
                setattr(contract, key, new_value)

        self.session.commit()

        return contract

    def edit_event_object(self, event_to_edit):
        """
        Updates the details of an existing event in the database.

        This method allows for editing specific fields of a `Event` record
        based on the provided data. It retrieves the event using the
        event ID, updates the event fields with new values provided by
        the user, and commits the changes to the database.
        :param event_to_edit:
        """
        event_editables = {
            "name": event_to_edit.name,
            "event_date_start": event_to_edit.event_date_start,
            "event_date_end": event_to_edit.event_date_end,
            "location": event_to_edit.location,
            "attendees": event_to_edit.attendees,
            "notes": event_to_edit.notes,
        }

        event_id = event_to_edit.id
        event = self.session.get(Event, event_id)

        if not event:
            raise ValueError(f"Event with ID {event_id} does not exist.")

        for key in event_editables.keys():
            new_value = MainView.input_update_view(event, key)
            if new_value:
                setattr(event, key, new_value)

        self.session.commit()

        return event
