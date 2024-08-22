import psycopg2
from view import LoginView


class LoginController:
    def login(self):
        login_view = LoginView()
        host = "localhost"
        database = "test"
        # user, password = login_view.get_credentials()
        user = "postgres"  # Comment to login
        password = "aCuN2ahb*"  # Comment to login

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


class BaseModel:

    def create(self, model_name, **kwargs):

        database_controller = DataBaseController()

        conn = database_controller.connect_to_database()
        cur = database_controller.create_cursor(conn)

        keys = (",".join(kwargs.keys()))
        query_values = tuple(kwargs.values())

        print(f"keys : {keys}")
        print(f"query_values : {query_values}")

        query = f"INSERT INTO {model_name}({keys}) VALUES {query_values}"
        print(query)
        cur.execute(query)

        database_controller.close_cursor(cur)
        database_controller.commit_transaction(conn)
        database_controller.close_connection(conn)

    def get_all(self, model_name):

        database_controller = DataBaseController()

        conn = database_controller.connect_to_database()
        cur = database_controller.create_cursor(conn)

        query = f"SELECT * FROM {model_name}"

        cur.execute(query)
        events = cur.fetchall()

        database_controller.close_cursor(cur)
        database_controller.commit_transaction(conn)
        database_controller.close_connection(conn)

        return events

    def update(self, model_name, object_id, **kwargs):
        database_controller = DataBaseController()

        conn = database_controller.connect_to_database()
        cur = database_controller.create_cursor(conn)

        set_clause = ", ".join([f"{key} = %s" for key in kwargs.keys()])
        values = tuple(kwargs.values())

        query = f"UPDATE {model_name} SET {set_clause} WHERE id = %s"

        values += (object_id,)

        cur.execute(query, values)

        conn.commit()
        cur.close()
        conn.close()

    def delete(self, model_name, object_id):
        database_controller = DataBaseController()

        conn = database_controller.connect_to_database()
        cur = database_controller.create_cursor(conn)

        query = f"DELETE FROM {model_name} where id = {object_id}"

        print(query)
        # cur.execute(query)

        conn.commit()
        cur.close()
        conn.close()

        # TODO : Est-ce que la suppression doit-être une methode de classe ? Reconstruire l'object avant d'aller le delete ?
