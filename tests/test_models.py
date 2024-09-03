from models import Contract, Customer, CustomerRepresentative, Event


class TestCustomerRepresentativeModel:

    def test_create_customer_representative_record(self, new_customer_representative):
        assert isinstance(new_customer_representative, CustomerRepresentative)
        assert getattr(new_customer_representative, "id")
        assert new_customer_representative.email == "rep@example.com"


class TestCustomerModel:

    def test_create_customer_record(self, new_customer, new_customer_representative):
        assert isinstance(new_customer, Customer)
        assert getattr(new_customer, "id")
        assert new_customer.email == "customer@email.test"
        assert new_customer.customer_representative.email == "rep@example.com"


class TestContractModel:

    def test_create_contract_record(self, new_contract):
        assert isinstance(new_contract, Contract)
        assert getattr(new_contract, "id")
        assert new_contract.name == "TestContractName"
        assert new_contract.customer.email == "customer@email.test"
        assert new_contract.customer_representative.email == "rep@example.com"


class TestEventModel:

    def test_create_event_record(self, new_event):
        assert isinstance(new_event, Event)
        assert getattr(new_event, "id")
        assert new_event.name == "TestEventName"
        assert new_event.contract.name == "TestContractName"
        assert new_event.customer.email == "customer@email.test"
        assert new_event.customer_representative.email == "rep@example.com"
