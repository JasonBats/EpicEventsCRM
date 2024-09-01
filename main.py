import sentry_sdk

from controller import DataBaseController, LoginController, ModelsController
from view import (
    ConsoleView,
    ContractMenuView,
    CustomerMenuView,
    CustomerRepresentativeMenuView,
    EventMenuView,
    MainView,
)

sentry_sdk.init(
    dsn="https://6db641e48c6e2039cd94eb7fc0e00d78@o4507583025446912.ingest.de."
    "sentry.io/4507583030296656",
    ignore_errors=[KeyboardInterrupt],
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
)

# sentry_test = 1 / 0


class CustomerRepresentativeController:

    def __init__(self):
        self.database_controller = DataBaseController()
        self.customer_representative_menu_view = CustomerRepresentativeMenuView()
        self.model_controller = ModelsController()

    def create_new_customer_representative(self):
        customer_representative_infos = (
            self.customer_representative_menu_view.create_customer_representative()
        )
        self.model_controller.create_customer_representative(
            customer_representative_infos
        )


class CustomerController:

    def __init__(self):
        self.database_controller = DataBaseController()
        self.customer_menu_view = CustomerMenuView()
        self.model_controller = ModelsController()
        self.console_view = ConsoleView("Customer List")

    def create_new_customer(self, user):
        customer_infos = self.customer_menu_view.create_customer()
        self.model_controller.create_customer(customer_infos, user)

    def edit_customer(self, user):
        customer_list = self.database_controller.list_item("customer", user)
        self.console_view.display_customer_list(customer_list)
        customer_to_edit = self.customer_menu_view.edit_customer(customer_list)
        self.model_controller.edit_customer(customer_to_edit)

    def delete_customer(self, user):
        customer_list = self.database_controller.list_item("customer", user)
        self.console_view.display_customer_list(customer_list)
        customer_to_delete_id = self.customer_menu_view.delete_customer(customer_list)
        self.database_controller.delete_item("customer", customer_to_delete_id)

    def list_customers(self, user):
        customer_list = self.database_controller.list_item("customer", user)
        self.console_view.display_customer_list(customer_list)

    def search_customer(self, user):
        data_filter, value = self.customer_menu_view.customer_dynamic_search_menu()
        dataset = self.database_controller.dynamic_search(
            table_name="customer", data_filter=data_filter, value=value, user=user
        )
        console_view = ConsoleView("Customer Search Result")
        console_view.display_customer_list(dataset)


class ContractController:

    def __init__(self):
        self.database_controller = DataBaseController()
        self.contract_menu_view = ContractMenuView()
        self.model_controller = ModelsController()
        self.console_view = ConsoleView("Customer List")

    def create_new_contract(self, user):
        customer_list = self.database_controller.list_item("customer", user)

        contract_infos = self.contract_menu_view.create_contract(customer_list)
        self.model_controller.create_contract(contract_infos, user)

    def edit_contract(self, user):
        contract_list = self.database_controller.list_item("contract", user)

        contract_to_edit = self.contract_menu_view.edit_contract(contract_list)
        self.model_controller.edit_contract_object(contract_to_edit)

    def delete_contract(self, user):
        contract_list = self.database_controller.list_item("contract", user)
        self.console_view.display_contract_list(contract_list)
        contract_to_delete_id = self.contract_menu_view.delete_contract(contract_list)
        self.database_controller.delete_item("contract", contract_to_delete_id)

    def list_contracts(self, user):
        contract_list = self.database_controller.list_item("contract", user)
        self.console_view.display_contract_list(contract_list)

    def list_unpaid_contracts(self, user):
        filtered_contract_list = self.database_controller.filter_unpaid_contracts(user)
        self.console_view.display_contract_list(filtered_contract_list)

    def search_contracts(self, user):
        data_filter, value = self.contract_menu_view.contract_dynamic_search_menu()
        dataset = self.database_controller.dynamic_search(
            table_name="contract", data_filter=data_filter, value=value, user=user
        )
        console_view = ConsoleView("Contract Search Result")
        console_view.display_contract_list(dataset)


class EventController:

    def __init__(self):
        self.database_controller = DataBaseController()
        self.event_menu_view = EventMenuView()
        self.model_controller = ModelsController()
        self.console_view = ConsoleView("Event List")

    def create_event(self, user):
        contract_list = self.database_controller.list_item("contract", user)
        contract, event_infos = self.event_menu_view.create_event(contract_list)
        self.model_controller.create_event(event_infos, contract)

    def edit_event(self, user):
        event_list = self.database_controller.list_item("event", user)
        event_to_edit = self.event_menu_view.edit_event(event_list)
        self.model_controller.edit_event_object(event_to_edit)

    def delete_event(self, user):
        event_list = self.database_controller.list_item("event", user)
        event_to_delete_id = self.event_menu_view.delete_event(event_list)
        self.database_controller.delete_item("event", event_to_delete_id)

    def list_events(self, user):
        event_list = self.database_controller.list_item("event", user)
        self.console_view.display_event_list(event_list)

    def list_events_to_come(self, user):
        filtered_events = self.database_controller.filter_events(">=", user)
        console_view = ConsoleView("Evenements à venir")
        console_view.display_event_list(filtered_events)

    def list_past_events(self, user):
        filtered_events = self.database_controller.filter_events("<=", user)
        console_view = ConsoleView("Evenements passés")
        console_view.display_event_list(filtered_events)

    def search_events(self, user):
        data_filter, value = self.event_menu_view.event_dynamic_search_menu()
        dataset = self.database_controller.dynamic_search(
            table_name="event", data_filter=data_filter, value=value, user=user
        )
        console_view = ConsoleView("Event Search Result")
        console_view.display_event_list(dataset)


class MainController:

    def __init__(self):
        self.login_controller = LoginController()
        self.logged, self.user = self.login_controller.login()

    def run(self):
        if self.logged:
            while True:
                try:
                    main_choice = MainView.main_menu()

                    main_menu_options = {
                        1: create_client_menu_handler,
                        2: create_contract_menu_handler,
                        3: create_event_menu_handler,
                        4: creatve_cr_menu_handler,
                    }

                    main_menu_options[main_choice](self.user)

                except ValueError as e:
                    print("Merci de saisir le CHIFFRE correspondant à votre choix.")
                    print(e)
                except KeyError:
                    print(f"Ce choix ne correspond à aucune option.")
                except IndexError:
                    print("Ce choix ne correspond à aucune option.")


def create_client_menu_handler(user):

    client_menu = MainView.client_menu()
    customer_controller = CustomerController()

    customer_functions = {
        1: customer_controller.create_new_customer,
        2: customer_controller.edit_customer,
        3: customer_controller.delete_customer,
        4: customer_controller.list_customers,
        5: customer_controller.search_customer,
    }

    customer_functions[client_menu](user)


def create_contract_menu_handler(user):

    contract_menu = MainView.contract_menu()
    contract_controller = ContractController()

    contract_functions = {
        1: contract_controller.create_new_contract,
        2: contract_controller.edit_contract,
        3: contract_controller.delete_contract,
        4: contract_controller.list_contracts,
        5: contract_controller.list_unpaid_contracts,
        6: contract_controller.search_contracts,
    }

    contract_functions[contract_menu](user)


def create_event_menu_handler(user):

    event_menu = MainView.event_menu()
    event_controller = EventController()

    event_functions = {
        1: event_controller.create_event,
        2: event_controller.edit_event,
        3: event_controller.delete_event,
        4: event_controller.list_events,
        5: event_controller.list_events_to_come,
        6: event_controller.list_past_events,
        7: event_controller.search_events,
    }

    event_functions[event_menu](user)


def creatve_cr_menu_handler():

    cr_menu = MainView.customer_representative_menu()
    cr_controller = CustomerRepresentativeController()

    cr_functions = {1: cr_controller.create_new_customer_representative}

    cr_functions[cr_menu]()


main_controller = MainController()
main_controller.run()
