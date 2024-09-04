from datetime import date

from view import (
    CustomerRepresentativeMenuView,
    CustomerMenuView,
    ContractMenuView,
    EventMenuView,
)


class TestCustomerRepresentativeMenuView:

    def test_create_customer_representative(self, mocker):
        view = CustomerRepresentativeMenuView()

        mocker.patch(
            "builtins.input",
            side_effect=[
                "LastName",
                "FirstName",
                "email@mail.com",
                "0123456789",
                "123456",
            ],
        )

        customer_representative_infos = view.create_customer_representative()

        assert customer_representative_infos == {
            "last_name": "LastName",
            "first_name": "FirstName",
            "email": "email@mail.com",
            "phone_number": 123456789,
            "password": "123456",
        }


class TestCustomerMenuView:
    def test_create_customer(self, mocker):
        view = CustomerMenuView()

        mocker.patch(
            "builtins.input",
            side_effect=[
                "LastName",
                "FirstName",
                "email@mail.com",
                "0123456789",
                "CompanyName",
            ],
        )

        customer_infos = view.create_customer()

        assert customer_infos == {
            "last_name": "LastName",
            "first_name": "FirstName",
            "email": "email@mail.com",
            "phone_number": 123456789,
            "company_name": "CompanyName",
        }

    def test_customer_dynamic_search_menu(self, mocker):
        view = CustomerMenuView()

        mocker.patch("builtins.input", side_effect=["1", "Michel"])

        details = view.customer_dynamic_search_menu()

        assert details == ("first_name", "Michel")


class TestContractMenuView:

    def test_create_contract(self, mocker, new_customer):
        view = ContractMenuView()

        customer_list = [
            (
                new_customer.id,
                new_customer.first_name,
                new_customer.last_name,
                new_customer.phone_number,
                new_customer.company_name,
                date(2024, 9, 4),
                date(2024, 9, 4),
                new_customer.customer_representative_id,
                new_customer.email,
            )
        ]

        mocker.patch(
            "builtins.input", side_effect=["ContractName", "750", "700", "En cours", 0]
        )

        details = view.create_contract(customer_list)
        print(f"&&&&&&&&&&&{details}")

        assert details["name"] == "ContractName"
        assert details["total_amount"] == 750
        assert details["amount_due"] == 700
        assert details["status"] == "En cours"

    def test_contract_dynamic_search_menu(self, mocker):
        view = ContractMenuView()

        mocker.patch("builtins.input", side_effect=["1", "Contrat"])

        details = view.contract_dynamic_search_menu()

        assert details == ("name", "Contrat")


class TestEventMenuView:

    def test_create_event(self, mocker, new_contract):
        view = EventMenuView()

        contract_list = [
            (
                str(new_contract.id),
                new_contract.name,
                new_contract.total_amount,
                new_contract.amount_due,
                new_contract.status,
                new_contract.customer_email,
                new_contract.customer_id,
                new_contract.customer_representative_id,
                new_contract.customer_representative_email,
                new_contract.date_created,
            )
        ]

        mocker.patch(
            "builtins.input",
            side_effect=[
                0,
                "EventName",
                "2025-09-09",
                "2025-09-09",
                "EventLocation",
                "42",
                ".",
            ],
        )

        contract, details = view.create_event(contract_list)
        print(f"qserzgsedrfg{details}")
        print(f"uhidgdiufrothgderx{contract_list[0]}")

        assert details["name"] == "EventName"
        assert details["location"] == "EventLocation"

    def test_event_dynamic_search_menu(self, mocker):
        view = ContractMenuView()

        mocker.patch("builtins.input", side_effect=["1", "EventNameResearch"])

        details = view.contract_dynamic_search_menu()

        assert details == ("name", "EventNameResearch")
