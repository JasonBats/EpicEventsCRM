from unittest.mock import patch

from controller import DataBaseController, LoginController, ModelsController
from models import Contract, Customer, CustomerRepresentative


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

        fake_encoded_jwt = "fake_jwt_token"
        mock_jwt_encode = mocker.patch("controller.jwt.encode")
        mock_jwt_encode.return_value = fake_encoded_jwt

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

        fake_encoded_jwt = "fake_jwt_token"
        mock_jwt_encode = mocker.patch("controller.jwt.encode")
        mock_jwt_encode.return_value = fake_encoded_jwt

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

    def test_list_item(self, session, new_customer_representative, new_customer):
        controller = DataBaseController()
        controller.session = session

        item_list = controller.list_item("customer", new_customer_representative)

        assert item_list is not None
        assert item_list[0].email == new_customer.email

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

        with patch.object(session, "add") as mock_add, patch.object(
            session, "commit"
        ) as mock_commit:
            created_customer_representative = controller.create_customer_representative(
                customer_representative_infos
            )
            mock_add.assert_called_once()
            assert isinstance(created_customer_representative, CustomerRepresentative)
            mock_commit.assert_called_once()
            mock_hash_password.assert_called_once_with("1234")

    def test_create_customer(self, session, new_customer_representative):

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

        with patch.object(session, "add") as mock_add, patch.object(
            session, "commit"
        ) as mock_commit:
            created_customer = controller.create_customer(customer_infos, user)

            mock_add.assert_called_once()
            assert isinstance(created_customer, Customer)
            mock_commit.assert_called_once()

    def test_edit_customer(self, mocker, session, new_customer):
        controller = ModelsController()
        controller.session = session

        customer_to_edit = (
            str(new_customer.id),
            new_customer.first_name,
            new_customer.last_name,
            new_customer.phone_number,
            new_customer.company_name,
            new_customer.date_created,
            new_customer.date_modified,
            new_customer.customer_representative_id,
            new_customer.email,
        )

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

    def test_create_contract(self, session, new_customer_representative, new_customer):
        controller = ModelsController()
        controller.session = session

        contract_infos = {
            "name": "TestContract",
            "total_amount": 750,
            "amount_due": 700,
            "status": "En cours",
            "customer": [str(new_customer.id)],
        }
        user = new_customer_representative

        with patch.object(session, "add") as mock_add, patch.object(
            session, "commit"
        ) as mock_commit:
            created_contract = controller.create_contract(contract_infos, user)

            mock_add.assert_called_once()
            assert isinstance(created_contract, Contract)
            mock_commit.assert_called_once()

    def test_edit_ontract(self, mocker, session, new_contract):
        controller = ModelsController()
        controller.session = session

        contract_to_edit = (
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
