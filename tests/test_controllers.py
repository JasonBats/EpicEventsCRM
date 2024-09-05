import uuid
from datetime import datetime

from controller import DataBaseController, LoginController, ModelsController
from models import Contract, Customer, CustomerRepresentative, Event


class TestLoginController:

    def test_login_success(self, mocker, session, new_customer_representative):
        controller = LoginController()
        controller.session = session

        mock_login_view = mocker.patch("controller.LoginView")
        mock_login_view_instance = mock_login_view.return_value
        mock_login_view_instance.get_credentials.return_value = (
            "rep@example.com",
            "123456",
        )

        mock_verify_password = mocker.patch("controller.verify_password")
        mock_verify_password.return_value = True

        session.add(new_customer_representative)
        session.commit()

        password_verified, user = controller.login()

        assert password_verified is True
        assert user == new_customer_representative

    def test_login_fail(self, mocker, session, new_customer_representative):
        controller = LoginController()
        controller.session = session

        mock_login_view = mocker.patch("controller.LoginView")
        mock_login_view_instance = mock_login_view.return_value
        mock_login_view_instance.get_credentials.return_value = (
            "who@is.this",
            "123456",
        )

        mock_verify_password = mocker.patch("controller.verify_password")
        mock_verify_password.return_value = True

        session.add(new_customer_representative)
        session.commit()

        password_verified, user = controller.login()

        assert password_verified is False
        assert user is None


class TestDataBaseController:
    def test_dynamic_search(self, session, new_customer_representative, new_customer):
        controller = DataBaseController()
        controller.session = session

        result = controller.dynamic_search(
            "customer", "email", "e", new_customer_representative
        )

        assert all(hasattr(record, "email") for record in result)
        assert result[0].email == new_customer.email

    def test_filter_events(self, session, new_customer_representative):
        controller = DataBaseController()
        controller.session = session

        result = controller.filter_events(">=", new_customer_representative)

        assert all(hasattr(record, "name") for record in result)
        assert all(
            record.customer_representative_id == new_customer_representative.id
            for record in result
        )

    def test_delete_item(self, session, new_event):
        controller = DataBaseController()
        controller.session = session

        deleted_item = controller.delete_item("event", str(new_event.id))
        assert deleted_item is None

    def test_delete_unknown_item(self, session, new_event):
        controller = DataBaseController()
        controller.session = session

        deleted_item = controller.delete_item("event", str(uuid.uuid1()))
        assert deleted_item is None

    def test_list_item(self, session, new_customer_representative, new_customer):
        controller = DataBaseController()
        controller.session = session

        item_list = controller.list_item(Customer, new_customer_representative)

        assert item_list is not None
        assert item_list[0].email == new_customer.email

    def test_list_customer_representatives(self, session, new_customer_representative):
        controller = DataBaseController()
        controller.session = session

        new_customer_representative.is_admin = 1

        item_list = controller.list_item(
            CustomerRepresentative, new_customer_representative
        )

        assert item_list is not None
        assert item_list[0].email == new_customer_representative.email

    def test_filter_unpaid_contracts(
        self, session, new_customer_representative, new_contract
    ):
        controller = DataBaseController()
        controller.session = session

        item_list = controller.filter_unpaid_contracts(new_customer_representative)

        assert item_list is not None
        assert item_list[0].amount_due == new_contract.amount_due


class TestModelsController:

    def test_create_customer_representative(self, mocker, session):

        controller = ModelsController()
        controller.session = session

        mock_hash_password = mocker.patch(
            "controller.hash_password", return_value=b"hashed_password"
        )

        customer_representative_infos = {
            "last_name": "CRLastName",
            "first_name": "CRFirstName",
            "email": "CREmail@test.com",
            "phone_number": int("0123456789"),
            "password": "1234",
        }

        mock_add = mocker.patch.object(session, "add")
        mock_commit = mocker.patch.object(session, "commit")

        created_customer_representative = controller.create_customer_representative(
            customer_representative_infos
        )
        mock_add.assert_called_once()
        assert isinstance(created_customer_representative, CustomerRepresentative)
        mock_commit.assert_called_once()
        mock_hash_password.assert_called_once_with("1234")

    def test_create_customer(self, mocker, session, new_customer_representative):

        controller = ModelsController()
        controller.session = session

        customer_infos = {
            "last_name": "CustomerLastName",
            "first_name": "CustomerFirstName",
            "email": "customer@email.test",
            "phone_number": int("0123456789"),
            "company_name": "CustomerCompanyName",
        }

        user = new_customer_representative

        mock_add = mocker.patch.object(session, "add")
        mock_commit = mocker.patch.object(session, "commit")

        created_customer = controller.create_customer(customer_infos, user)

        mock_add.assert_called_once()
        assert isinstance(created_customer, Customer)
        mock_commit.assert_called_once()

    def test_edit_customer(self, mocker, session, new_customer):
        controller = ModelsController()
        controller.session = session

        customer_to_edit = new_customer

        mock_input_update_view = mocker.patch(
            "controller.MainView.input_update_view",
            side_effect=lambda customer, field: {
                "last_name": "NewName",
                "first_name": "NewFirstName",
                "phone_number": "999999999",
                "company_name": "NewCompany",
                "email": "new@email.test",
            }.get(field),
        )

        customer = controller.edit_customer(customer_to_edit)
        assert customer.last_name == "NewName"
        mock_input_update_view.assert_called()

    def test_create_contract(
        self, mocker, session, new_customer_representative, new_customer
    ):
        controller = ModelsController()
        controller.session = session

        contract_infos = {
            "name": "TestContract",
            "total_amount": 750,
            "amount_due": 700,
            "status": "En cours",
            "customer": new_customer,
        }

        user = new_customer_representative

        mock_add = mocker.patch.object(session, "add")
        mock_commit = mocker.patch.object(session, "commit")
        created_contract = controller.create_contract(contract_infos, user)

        mock_add.assert_called_once()
        assert isinstance(created_contract, Contract)
        mock_commit.assert_called_once()

    def test_edit_contract(self, mocker, session, new_contract):
        controller = ModelsController()
        controller.session = session

        contract_to_edit = new_contract

        mock_input_update_view = mocker.patch(
            "controller.MainView.input_update_view",
            side_effect=lambda contract, field: {
                "name": "NewContractName",
                "total_amount": 999,
                "amount_due": 666,
                "status": "en cours",
            }.get(field),
        )

        contract = controller.edit_contract_object(contract_to_edit)
        assert contract.name == "NewContractName"
        mock_input_update_view.assert_called()

    def test_create_event(self, mocker, session, new_contract):
        controller = ModelsController()
        controller.session = session

        event_infos = {
            "name": "EventName",
            "event_date_start": "2024-10-10",
            "event_date_end": "2024-10-10",
            "location": "EventLocation",
            "attendees": "42",
            "notes": "",
        }

        mock_add = mocker.patch.object(session, "add")
        mock_commit = mocker.patch.object(session, "commit")
        event = controller.create_event(event_infos, new_contract)

        mock_add.assert_called_once()
        assert isinstance(event, Event)
        mock_commit.assert_called_once()

    def test_edit_event(self, mocker, session, new_event):
        controller = ModelsController()
        controller.session = session

        event_to_edit = new_event

        mock_input_update_view = mocker.patch(
            "controller.MainView.input_update_view",
            side_effect=lambda event, field: {
                "name": "NewEventName",
                "event_date_start": datetime.strptime("2024-11-11", "%Y-%m-%d"),
                "event_date_end": datetime.strptime("2024-11-11", "%Y-%m-%d"),
                "location": "Annecy",
                "attendees": "24",
                "notes": "Notes",
            }.get(field),
        )

        event = controller.edit_event_object(event_to_edit)

        mock_input_update_view.assert_called()
        assert event.name == "NewEventName"
        assert event.attendees == 24
        assert event.notes == "Notes"
