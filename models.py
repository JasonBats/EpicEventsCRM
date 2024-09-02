from datetime import datetime
from uuid import UUID, uuid1

from sqlalchemy import Date, ForeignKey, Integer, LargeBinary, Numeric, String, Boolean
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, relationship


Base = declarative_base()


class CustomerRepresentative(Base):

    __tablename__ = "customer_representative"

    id: Mapped[UUID] = mapped_column(
        primary_key=True, unique=True, nullable=False, default=uuid1
    )
    last_name: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    phone_number: Mapped[str] = mapped_column(String(15), nullable=False)
    password: Mapped[bytes] = mapped_column(LargeBinary(), nullable=False)
    customers: Mapped[list["Customer"]] = relationship(
        "Customer", back_populates="customer_representative"
    )
    contracts: Mapped[list["Contract"]] = relationship(
        "Contract",
        back_populates="customer_representative",
        foreign_keys="[Contract.customer_representative_id]",
    )
    events: Mapped[list["Event"]] = relationship(
        "Event",
        back_populates="customer_representative",
        foreign_keys="[Event.customer_representative_id]",
    )
    is_admin: Mapped[bool] = mapped_column(Boolean, nullable=False)


class Customer(Base):

    __tablename__ = "customer"

    id: Mapped[UUID] = mapped_column(
        primary_key=True, unique=True, nullable=False, default=uuid1
    )
    first_name: Mapped[str] = mapped_column(String(255))
    last_name: Mapped[str] = mapped_column(String(255))
    phone_number: Mapped[str] = mapped_column(String(15))
    company_name: Mapped[str] = mapped_column(String(255))
    date_created: Mapped[datetime] = mapped_column(Date(), nullable=False)
    date_modified: Mapped[datetime] = mapped_column(Date(), nullable=False)
    customer_representative_id: Mapped[str] = mapped_column(
        ForeignKey("customer_representative.id")
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    customer_representative: Mapped["CustomerRepresentative"] = relationship(
        "CustomerRepresentative", back_populates="customers"
    )
    contracts: Mapped[list["Contract"]] = relationship(
        "Contract", back_populates="customer", foreign_keys="[Contract.customer_id]"
    )
    events: Mapped[list["Event"]] = relationship(
        "Event", back_populates="customer", foreign_keys="[Event.customer_id]"
    )


class Contract(Base):
    __tablename__ = "contract"

    id: Mapped[UUID] = mapped_column(
        primary_key=True, unique=True, nullable=False, default=uuid1
    )
    name: Mapped[str] = mapped_column(String(255))
    total_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    amount_due: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    date_created: Mapped[datetime] = mapped_column(Date(), nullable=False)
    status: Mapped[str] = mapped_column(String(255))
    customer_email: Mapped[str] = mapped_column(ForeignKey("customer.email"))
    customer_id: Mapped[str] = mapped_column(ForeignKey("customer.id"))
    customer_representative_id: Mapped[str] = mapped_column(
        ForeignKey("customer_representative.id")
    )
    customer_representative_email: Mapped[str] = mapped_column(
        ForeignKey("customer_representative.email")
    )
    customer: Mapped["Customer"] = relationship(
        "Customer", back_populates="contracts", foreign_keys="[Contract.customer_id]"
    )
    customer_representative: Mapped["CustomerRepresentative"] = relationship(
        "CustomerRepresentative",
        back_populates="contracts",
        foreign_keys="[Contract.customer_representative_id]",
    )
    events: Mapped[list["Event"]] = relationship(
        "Event", back_populates="contract", foreign_keys="[Event.contract_id]"
    )


class Event(Base):

    __tablename__ = "event"

    name: Mapped[str] = mapped_column(String(255))
    id: Mapped[UUID] = mapped_column(
        primary_key=True, unique=True, nullable=False, default=uuid1
    )
    customer_id: Mapped[str] = mapped_column(ForeignKey("customer.id"), nullable=False)
    customer_email: Mapped[str] = mapped_column(
        ForeignKey("customer.email"), nullable=False
    )
    customer_representative_id: Mapped[str] = mapped_column(
        ForeignKey("customer_representative.id"), nullable=False
    )
    customer_representative_email: Mapped[str] = mapped_column(
        ForeignKey("customer_representative.email"), nullable=False
    )
    event_date_start: Mapped[datetime] = mapped_column(Date(), nullable=False)
    event_date_end: Mapped[datetime] = mapped_column(Date(), nullable=False)
    location: Mapped[str] = mapped_column(String(255))
    attendees: Mapped[int] = mapped_column(Integer(), nullable=False)
    notes: Mapped[str] = mapped_column(String(255))
    contract_id: Mapped[str] = mapped_column(ForeignKey("contract.id"))
    customer: Mapped["Customer"] = relationship(
        "Customer", back_populates="events", foreign_keys="[Event.customer_id]"
    )
    customer_representative: Mapped["CustomerRepresentative"] = relationship(
        "CustomerRepresentative",
        back_populates="events",
        foreign_keys="[Event.customer_representative_id]",
    )
    contract: Mapped["Contract"] = relationship(
        "Contract", back_populates="events", foreign_keys="[Event.contract_id]"
    )
