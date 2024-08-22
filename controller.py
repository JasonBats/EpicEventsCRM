from datetime import datetime, date

import psycopg2
from psycopg2 import sql, errors
from model import Customer, CustomerRepresentative, Contract, Event
from utils import hash_password, verify_password
from view import LoginView


class LoginController:
    def login(self):
        login_view = LoginView()
        host = "localhost"
        database = "test"
        # user, password = login_view.get_credentials()
        user = "test_user"  # Comment to login
        password = "admin123"  # Comment to login

        return host, database, user, password


class DataBaseController:

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

    def create_cursor(self, conn):
        return conn.cursor()

    def close_cursor(self, cursor):
        cursor.close()

    def close_connection(self, conn):
        conn.close()

    def commit_transaction(self, conn):
        conn.commit()

    def search_customer_representative(self, email):
        conn = self.connect_to_database()
        cur = self.create_cursor(conn)

        cur.execute("""
        SELECT * FROM customer_representative
        WHERE email = %s
        """,
                    (email,)
                    )

        user = cur.fetchone()
        self.close_cursor(conn)
        self.close_connection(conn)
        return user

    def add_customer_to_database(self, customer_instance):
        conn = self.connect_to_database()
        cur = self.create_cursor(conn)
        try:
            cur.execute("""
            INSERT INTO customer(
            last_name,
            first_name,
            email,
            phone_number,
            company_name,
            date_created,
            date_modified,
            customer_representative
            )
            
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
                        (
                            customer_instance.last_name,
                            customer_instance.first_name,
                            customer_instance.email,
                            customer_instance.phone_number,
                            customer_instance.company_name,
                            customer_instance.date_created,
                            customer_instance.date_modified,
                            customer_instance.customer_representative
                        )
                        )

            self.close_cursor(cur)
            self.commit_transaction(conn)
            self.close_connection(conn)
        except psycopg2.errors.UniqueViolation as e:
            print(f"Valeur de clé dupliquée.\n{e}")

    def add_customer_representative_to_database(self, customer_representative_instance):
        conn = self.connect_to_database()
        cur = self.create_cursor(conn)

        cur.execute("""
        INSERT INTO customer_representative(
        last_name,
        first_name,
        email,
        phone_number,
        password
        )

        VALUES (%s, %s, %s, %s, %s)
        """,
                    (
                        customer_representative_instance.last_name,
                        customer_representative_instance.first_name,
                        customer_representative_instance.email,
                        customer_representative_instance.phone_number,
                        customer_representative_instance.password
                    )
                    )

        self.close_cursor(cur)
        self.commit_transaction(conn)
        self.close_connection(conn)

    def add_contract_to_database(self, contract_instance):
        conn = self.connect_to_database()
        cur = self.create_cursor(conn)

        customer_representative_id = contract_instance.customer_representative[0]
        customer_id = contract_instance.customer[8]

        try:
            cur.execute("""
            INSERT INTO contract(
            name,
            customer_representative,
            customer_representative_email,
            total_amount,
            amount_due,
            date_created,
            status,
            customer,
            customer_email
            )
    
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
                        (
                            contract_instance.name,
                            customer_representative_id,
                            contract_instance.customer_representative[3],
                            contract_instance.total_amount,
                            contract_instance.amount_due,
                            contract_instance.date_created,
                            contract_instance.status,
                            customer_id,
                            contract_instance.customer[7]
                        )
                        )

            self.close_cursor(cur)
            self.commit_transaction(conn)
            self.close_connection(conn)
        except psycopg2.errors.InvalidTextRepresentation as e:
            print(f"Entrée incorrecte : {e}")

    def add_event_to_database(self, event_instance, contract):
        conn = self.connect_to_database()
        cur = self.create_cursor(conn)

        customer_representative_id = contract[8]
        customer_id = contract[7]
        contract_id = contract[0]

        try:
            cur.execute("""
            INSERT INTO event(
            name,
            customer,
            customer_email,
            customer_representative,
            customer_representative_email,
            event_date_start,
            event_date_end,
            location,
            attendees,
            notes,
            contract
            )
    
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
                        (
                            event_instance.name,
                            customer_id,
                            contract[6],
                            customer_representative_id,
                            contract[9],
                            event_instance.event_date_start,
                            event_instance.event_date_end,
                            event_instance.location,
                            event_instance.attendees,
                            event_instance.notes,
                            contract_id
                        )
                        )

            self.close_cursor(cur)
            self.commit_transaction(conn)
            self.close_connection(conn)
        except (psycopg2.errors.InvalidDatetimeFormat,
                psycopg2.errors.DatetimeFieldOverflow):
            print(f"Date invalide parmi [{event_instance.event_date_end}]"
                  f" [{event_instance.event_date_start}]")

    def update_customer_to_database(self, edited_customer, edited_customer_id):

        conn = self.connect_to_database()
        cur = self.create_cursor(conn)

        try:
            cur.execute("""
                    UPDATE customer
                    SET 
                        last_name = %s,
                        first_name = %s,
                        phone_number = %s,
                        company_name = %s,
                        date_modified = %s,
                        customer_representative = %s,
                        email = %s
                    WHERE id = %s
                    """,
                        (
                            edited_customer["last_name"],
                            edited_customer["first_name"],
                            edited_customer["phone_number"],
                            edited_customer["company_name"],
                            datetime.now(),
                            edited_customer["customer_representative"],
                            edited_customer["email"],
                            edited_customer_id
                            )
                        )

            self.commit_transaction(conn)
            self.close_cursor(conn)
            self.close_connection(conn)
        except errors.ForeignKeyViolation as fk_error:
            print(f"Violation de contrainte de clé étrangère : {fk_error}")
        except errors.InvalidTextRepresentation as invalid_text_error:
            print(f"Entrée incorrecte : {invalid_text_error}")

    def update_contract_to_database(self, edited_contract, edited_contract_id):

        conn = self.connect_to_database()
        cur = self.create_cursor(conn)

        try:
            cur.execute("""
                    UPDATE contract
                    SET 
                        name = %s,
                        total_amount = %s,
                        amount_due = %s,
                        status = %s,
                        customer_email = %s,
                        customer = %s,
                        customer_representative = %s,
                        customer_representative_email = %s
                    WHERE id = %s
                    """,
                        (
                            edited_contract["name"],
                            edited_contract["total_amount"],
                            edited_contract["amount_due"],
                            edited_contract["status"],
                            edited_contract["customer_email"],
                            edited_contract["customer"],
                            edited_contract["customer_representative"],
                            edited_contract["customer_representative_email"],
                            edited_contract_id
                            )
                        )

            self.commit_transaction(conn)
            self.close_cursor(conn)
            self.close_connection(conn)
        except psycopg2.errors.InvalidTextRepresentation as e:
            print(f"Entrée incorrecte : {e}")

    def update_event_to_database(self, edited_event, edited_event_id):

        conn = self.connect_to_database()
        cur = self.create_cursor(conn)
        try:
            cur.execute("""
                    UPDATE event
                    SET 
                        name = %s,
                        event_date_start = %s,
                        event_date_end = %s,
                        location = %s,
                        attendees = %s,
                        notes = %s
                    WHERE id = %s
                    """,
                        (
                            edited_event["name"],
                            edited_event["event_date_start"],
                            edited_event["event_date_end"],
                            edited_event["location"],
                            edited_event["attendees"],
                            edited_event["notes"],
                            edited_event_id
                            )
                        )

            self.commit_transaction(conn)
            self.close_cursor(conn)
            self.close_connection(conn)
        except (psycopg2.errors.InvalidDatetimeFormat,
                psycopg2.errors.DatetimeFieldOverflow):
            print(f"Date invalide parmi [{edited_event["event_date_end"]}]"
                  f" [{edited_event["event_date_start"]}]")

    def delete_item_from_database(self, table, item_id):
        try:
            conn = self.connect_to_database()
            cur = self.create_cursor(conn)

            query = f"DELETE FROM {table} WHERE id = '{item_id}';"

            cur.execute(query)

            self.commit_transaction(conn)
            self.close_cursor(conn)
            self.close_connection(conn)
        except errors.ForeignKeyViolation as error:
            print(f"Violation de contrainte de clé étrangère : {error}")

    def list_item(self, table):
        conn = self.connect_to_database()
        cur = self.create_cursor(conn)

        query = f"SELECT * FROM {table}"
        print(query)

        cur.execute(query)

        event_list = cur.fetchall()

        self.close_cursor(cur)
        self.commit_transaction(conn)
        self.close_connection(conn)

        return event_list

    def filter_unpaid_contracts(self):
        conn = self.connect_to_database()
        cur = self.create_cursor(conn)


        query = f"SELECT * FROM contract WHERE amount_due > 0::money ORDER BY amount_due DESC"

        cur.execute(query)

        item_list = cur.fetchall()

        self.close_cursor(cur)
        self.commit_transaction(conn)
        self.close_connection(conn)

        return item_list

    def filter_events(self, when):
        conn = self.connect_to_database()
        cur = self.create_cursor(conn)

        today = datetime.now()

        query = f"SELECT * FROM event WHERE event_date_start {when} %s"

        cur.execute(query, (today,))

        event_list = cur.fetchall()

        self.close_cursor(cur)
        self.commit_transaction(conn)
        self.close_connection(conn)

        return event_list

    def dynamic_search(self, table, data_filter, value):
        conn = self.connect_to_database()
        cur = self.create_cursor(conn)

        print(f"SELECT * FROM {table} WHERE {data_filter} ILIKE '%{value}%'")

        query = f"SELECT * FROM {table} WHERE {data_filter} ILIKE '%{value}%'"

        cur.execute(query)

        item_list = cur.fetchall()

        self.close_cursor(cur)
        self.commit_transaction(conn)
        self.close_connection(conn)

        return item_list


class ModelsController:

    def create_customer_object(self, customer_infos):

        now = date.today().strftime('%Y-%m-%d')

        customer = Customer(last_name=customer_infos["last_name"],
                            first_name=customer_infos["first_name"],
                            email=customer_infos["email"],
                            phone_number=customer_infos["phone_number"],
                            company_name=customer_infos["company_name"],
                            date_created=now,
                            date_modified=now,
                            customer_representative=customer_infos["customer_representative"])

        return customer

    def create_contract_object(self, contract_infos):

        now = date.today().strftime('%Y-%m-%d')  # Stocker une fonction dans utils.py pour pas avoir à réécrire

        contract = Contract(name=contract_infos["name"],
                            total_amount=contract_infos["total_amount"],
                            amount_due=contract_infos["amount_due"],
                            status=contract_infos["status"],
                            customer_representative_id=contract_infos["customer_representative_id"],
                            customer_representative_email=contract_infos["customer_representative_email"],
                            customer_email=contract_infos["customer_email"],
                            customer_id=contract_infos["customer_id"],
                            date_created=now
                            )

        return contract

    def create_event_object(self, event_infos, contract):

        event = Event(
            name=event_infos["name"],
            customer=contract[7],
            customer_email=contract[6],
            customer_representative=contract[8],
            customer_representative_email=contract[9],
            event_date_start=event_infos["event_date_start"],
            event_date_end=event_infos["event_date_end"],
            location=event_infos["location"],
            attendees=event_infos["attendees"],
            notes=event_infos["notes"],
            contract=contract[0]
        )

        return event

    def edit_customer_object(self, customer_to_edit):
        customer_editable_fields = {
            'last_name': customer_to_edit[1],
            'first_name': customer_to_edit[0],
            'phone_number': customer_to_edit[2],
            'company_name': customer_to_edit[3],
            'customer_representative': customer_to_edit[6],
            'email': customer_to_edit[7]
        }

        customer_uneditable_fields = {
            'date_created': customer_to_edit[4],
            'date_modified': customer_to_edit[5],
        }

        customer_id = customer_to_edit[8]

        for key in customer_editable_fields.keys():
            new_value = input(f"{key} [{customer_editable_fields[key]}] : \n")
            if new_value:
                customer_editable_fields[key] = new_value

        customer = Customer(**customer_editable_fields, **customer_uneditable_fields)

        return customer, customer_id

    def edit_contract_object(self, contract_to_edit):
        contract_editable_fields = {
            'name': contract_to_edit[1],
            'total_amount': contract_to_edit[2],
            'amount_due': contract_to_edit[3],
            'status': contract_to_edit[5],
        }

        contract_uneditable_fields = {
            'date_created': contract_to_edit[4],
            'customer_email': contract_to_edit[6],
            'customer_id': contract_to_edit[7],
            'customer_representative_id': contract_to_edit[8],
            'customer_representative_email': contract_to_edit[9]
        }

        contract_id = contract_to_edit[0]

        for key in contract_editable_fields.keys():
            new_value = input(f"{key} [{contract_editable_fields[key]}] : \n")
            if new_value:
                contract_editable_fields[key] = new_value

        contract = Contract(**contract_editable_fields, **contract_uneditable_fields)

        return contract, contract_id

    def edit_event_object(self, event_to_edit):
        print(event_to_edit)
        event_editables = {
            'name': event_to_edit[0],
            'event_date_start': event_to_edit[6],
            'event_date_end': event_to_edit[7],
            'location': event_to_edit[8],
            'attendees': event_to_edit[9],
            'notes': event_to_edit[10],
        }

        event_uneditables = {
            'customer': event_to_edit[2],
            'customer_email': event_to_edit[3],
            'customer_representative': event_to_edit[4],
            'customer_representative_email': event_to_edit[5],
            'contract': event_to_edit[11]
        }

        event_id = event_to_edit[1]

        for key in event_editables.keys():
            new_value = input(f"{key} [{event_editables[key]}] : \n")
            if new_value:
                event_editables[key] = new_value

        new_event = Event(**event_editables, **event_uneditables)
        print(new_event)

        print(event_to_edit)
        return new_event, event_id


db_controller = DataBaseController()


customer_representative_test = CustomerRepresentative(
    "Pasdchute",
    "Jean-Michel",
    "jmpdc@gmail.com",
    "+33123456789",
    hash_password("Motdepasse123")
    )

# db_controller.add_customer_representative_to_database(customer_representative_test)

# search_user = db_controller.search_customer_representative("jcc@gmail.com")
#
# verify_password(bytes(search_user[5]), 'Motdepasse123')
