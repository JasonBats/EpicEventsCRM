from dataclasses import dataclass

from basemodel import BaseModel


@dataclass
class CustomerRepresentative:

    last_name: str
    first_name: str
    email: str
    phone_number: str
    password: str


@dataclass
class Customer(BaseModel):

    last_name: str
    first_name: str
    email: str
    phone_number: str
    company_name: str
    date_created: str
    date_modified: str
    customer_representative: str

    def create(self, model_name="customer"):
        super().create(model_name, **self.__dict__)

    def update_model(self, object_id, model_name="customer"):
        super().update(model_name, object_id, **self.__dict__)


@dataclass
class Contract(BaseModel):

    name: str
    customer_representative_email: str
    total_amount: float
    amount_due: float
    date_created: str
    status: str
    customer_representative_id: str
    customer_email: str
    customer_id: str

    def create(self, model_name="contract"):
        super().create(model_name, **self.__dict__)

    def update_model(self, object_id, model_name="contract"):
        super().update(model_name, object_id, **self.__dict__)


@dataclass
class Event(BaseModel):

    name: str
    customer: str
    customer_email: str
    customer_representative: str
    customer_representative_email: str
    event_date_start: str
    event_date_end: str
    location: str
    attendees: int
    notes: str
    contract: str

    def create(self, model_name="event"):
        super().create(model_name, **self.__dict__)

    def update_model(self, object_id, model_name="event"):
        super().update(model_name, object_id, **self.__dict__)
