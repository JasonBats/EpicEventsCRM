from view import (MainView,
                  CustomerMenuView,
                  ContractMenuView,
                  EventMenuView,
                  ConsoleView)
from controller import ModelsController, DataBaseController
import sentry_sdk
from basemodel import BaseModel

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


class CustomerController:

    @staticmethod
    def create_new_customer():
        database_controller = DataBaseController()
        customer_menu_view = CustomerMenuView()
        model_controller = ModelsController()

        cr_list = database_controller.list_item("customer_representative")
        customer_infos = customer_menu_view.create_customer(cr_list)
        customer = model_controller.create_customer_object(customer_infos)
        customer.create()


    @staticmethod
    def edit_customer():
        database_controller = DataBaseController()
        customer_menu_view = CustomerMenuView()
        model_controller = ModelsController()

        customer_list = database_controller.list_item("customer")
        console_view = ConsoleView("Customer List")
        console_view.display_customer_list(customer_list)
        customer_to_edit = customer_menu_view.edit_customer(customer_list)
        edited_customer, edited_customer_id = model_controller.edit_customer_object(customer_to_edit)
        # database_controller.update_customer_to_database(edited_customer, edited_customer_id)
        edited_customer.update_model(edited_customer_id)

    @staticmethod
    def delete_customer():
        database_controller = DataBaseController()
        customer_menu_view = CustomerMenuView()

        customer_list = database_controller.list_item("customer")
        console_view = ConsoleView("Customer List")
        console_view.display_customer_list(customer_list)
        customer_to_delete_id = customer_menu_view.delete_customer(customer_list)
        # TODO : Reconstruire customer ici ?
        database_controller.delete_item_from_database("customer", customer_to_delete_id)

    @staticmethod
    def list_customers():
        base_model = BaseModel()
        console_view = ConsoleView("Customer List")

        customer_list = base_model.get_all("customer")
        console_view.display_customer_list(customer_list)

    @staticmethod
    def search_customer():
        database_controller = DataBaseController()
        customer_menu_view = CustomerMenuView()

        data_filter, value = customer_menu_view.customer_dynamic_search_menu()
        dataset = database_controller.dynamic_search(
            table="customer",
            data_filter=data_filter,
            value=value
        )
        console_view = ConsoleView("Customer Search Result")
        console_view.display_customer_list(dataset)


class ContractController:

    @staticmethod
    def create_new_contract():
        database_controller = DataBaseController()
        model_controller = ModelsController()
        contract_menu_view = ContractMenuView()

        cr_list = database_controller.list_item("customer_representative")
        customer_list = database_controller.list_item("customer")

        contract_infos = contract_menu_view.create_contract(cr_list, customer_list)
        contract = model_controller.create_contract_object(contract_infos)
        contract.create()

    @staticmethod
    def edit_contract():
        database_controller = DataBaseController()
        model_controller = ModelsController()
        contract_menu_view = ContractMenuView()

        contract_list = database_controller.list_item("contract")
        contract_to_edit = contract_menu_view.edit_contract(contract_list)
        edited_contract, edited_contract_id = model_controller.edit_contract_object(contract_to_edit)
        # database_controller.update_contract_to_database(edited_contract, edited_contract_id)
        edited_contract.update_model(object_id=edited_contract_id)

    @staticmethod
    def delete_contract():
        database_controller = DataBaseController()
        contract_menu_view = ContractMenuView()

        contract_list = database_controller.list_item("contract")
        console_view = ConsoleView("Contract List")
        console_view.display_contract_list(contract_list)
        contract_to_delete_id = contract_menu_view.delete_contract(contract_list)
        database_controller.delete_item_from_database("contract", contract_to_delete_id)

    @staticmethod
    def list_contracts():
        base_model = BaseModel()
        console_view = ConsoleView("Contract List")

        contract_list = base_model.get_all("contract")
        console_view.display_contract_list(contract_list)

    @staticmethod
    def list_unpaid_contracts():
        database_controller = DataBaseController()

        filtered_contract_list = database_controller.filter_unpaid_contracts()
        console_view = ConsoleView("Contract List - Unpaid DESC")
        console_view.display_contract_list(filtered_contract_list)

    @staticmethod
    def search_contracts():
        database_controller = DataBaseController()
        contract_menu_view = ContractMenuView()

        data_filter, value = contract_menu_view.contract_dynamic_search_menu()
        dataset = database_controller.dynamic_search(table="contract", data_filter=data_filter, value=value)
        console_view = ConsoleView("Contract Search Result")
        console_view.display_contract_list(dataset)


class EventController:

    @staticmethod
    def create_event():
        database_controller = DataBaseController()
        event_menu_view = EventMenuView()
        model_controller = ModelsController()

        contract_list = database_controller.list_item("contract")
        contract, event_infos = event_menu_view.create_event(contract_list)
        event = model_controller.create_event_object(event_infos, contract)
        event.create()

    @staticmethod
    def edit_event():
        database_controller = DataBaseController()
        event_menu_view = EventMenuView()
        model_controller = ModelsController()
        base_model = BaseModel()

        event_list = base_model.get_all("event")
        event_to_edit = event_menu_view.edit_event(event_list)
        print(event_to_edit)
        edited_event, edited_event_id = model_controller.edit_event_object(event_to_edit)
        # database_controller.update_event_to_database(edited_event, edited_event_id)
        edited_event.update_model(object_id=edited_event_id)

    @staticmethod
    def delete_event():
        database_controller = DataBaseController()
        event_menu_view = EventMenuView()

        event_list = database_controller.list_item("event")
        event_to_delete_id = event_menu_view.delete_event(event_list)
        database_controller.delete_item_from_database("event", event_to_delete_id)

    @staticmethod
    def list_events():
        base_model = BaseModel()
        console_view = ConsoleView("Event List")

        event_list = base_model.get_all("event")
        console_view.display_event_list(event_list)

    @staticmethod
    def list_events_to_come():
        database_controller = DataBaseController()

        filtered_events = database_controller.filter_events(">=")
        console_view = ConsoleView("Evenements à venir")
        console_view.display_event_list(filtered_events)

    @staticmethod
    def list_past_events():
        database_controller = DataBaseController()

        filtered_events = database_controller.filter_events("<=")
        console_view = ConsoleView("Evenements passés")
        console_view.display_event_list(filtered_events)

    @staticmethod
    def search_events():
        event_menu_view = EventMenuView()
        database_controller = DataBaseController()

        data_filter, value = event_menu_view.event_dynamic_search_menu()
        dataset = database_controller.dynamic_search(table="event", data_filter=data_filter, value=value)
        console_view = ConsoleView("Event Search Result")
        console_view.display_event_list(dataset)


class MainController:

    def run(self):
        while True:
            try:
                main_choice = MainView.main_menu()

                main_menu_options = {
                    1: create_client_menu_handler,
                    2: create_contract_menu_handler,
                    3: create_event_menu_handler
                }

                main_menu_options[main_choice]()

            except ValueError as e:
                print("Merci de saisir le CHIFFRE correspondant à votre choix.")
                print(e)
            except KeyError:
                print(f"Ce choix ne correspond à aucune option.")
            except IndexError:
                print("Ce choix ne correspond à aucune option.")


def create_client_menu_handler():
    client_menu = MainView.client_menu()

    customer_functions = {
        1: CustomerController.create_new_customer,
        2: CustomerController.edit_customer,
        3: CustomerController.delete_customer,
        4: CustomerController.list_customers,
        5: CustomerController.search_customer
    }

    customer_functions[client_menu]()


def create_contract_menu_handler():
    contract_menu = MainView.contract_menu()

    contract_functions = {
        1: ContractController.create_new_contract,
        2: ContractController.edit_contract,
        3: ContractController.delete_contract,
        4: ContractController.list_contracts,
        5: ContractController.list_unpaid_contracts,
        6: ContractController.search_contracts
    }

    contract_functions[contract_menu]()


def create_event_menu_handler():
    event_menu = MainView.event_menu()

    event_functions = {
        1: EventController.create_event,
        2: EventController.edit_event,
        3: EventController.delete_event,
        4: EventController.list_events,
        5: EventController.list_events_to_come,
        6: EventController.list_past_events,
        7: EventController.search_events
    }

    event_functions[event_menu]()


main_controller = MainController()
main_controller.run()
