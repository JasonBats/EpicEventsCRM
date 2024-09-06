from typing import Any, Tuple, Type

from rich.console import Console
from rich.table import Table

from models import Contract, Customer, Event
from utils import (validate_amount_due, validate_date, validate_email,
                   validate_end_date, validate_phone_number,
                   validate_total_amount)


class LoginView:
    def get_credentials(self) -> Tuple[str, str]:
        user = input("Login :")
        password = input("Password :")

        return user, password


class MainView:

    @staticmethod
    def main_menu() -> int:
        main_choice = int(
            input(
                "Quel menu ouvrir ?\n"
                "\n[1] - Clients"
                "\n[2] - Contrats"
                "\n[3] - Évenements\n"
                "\n[4] - Administration\n"
                "\n[5] - Déconnexion\n"
            )
        )

        return main_choice

    @staticmethod
    def client_menu() -> int:
        client_menu_choice = int(
            input(
                "-- CLIENTS --\n"
                "Souahitez-vous :"
                "\n[1] - Ajouter un client"
                "\n[2] - Modifier un client"
                "\n[3] - Supprimer un client"
                "\n ---"
                "\n[4] - Liste de tous les clients"
                "\n[5] - Rechercher un client\n"
            )
        )

        return client_menu_choice

    @staticmethod
    def contract_menu():
        contract_menu_choice = int(
            input(
                "-- CONTRATS --\n"
                "Souahitez-vous :"
                "\n[1] - Ajouter un contrat"
                "\n[2] - Modifier un contrat"
                "\n[3] - Supprimer un contrat"
                "\n ---"
                "\n[4] - Liste de tous les contrats"
                "\n[5] - Contrats non réglés"
                "\n ---"
                "\n[6] - Rechercher un contrat\n"
            )
        )

        return contract_menu_choice

    @staticmethod
    def event_menu() -> int:
        event_menu_choice = int(
            input(
                "-- ÉVÈNEMENTS --\n"
                "Souahitez-vous :"
                "\n[1] - Ajouter un évènement"
                "\n[2] - Modifier un évènement"
                "\n[3] - Supprimer un évènement"
                "\n ---"
                "\n[4] - Liste de tous les évènements"
                "\n[5] - Évènements à venir"
                "\n[6] - Évènements passés"
                "\n ---"
                "\n[7] - Rechercher un évènement\n"
            )
        )

        return event_menu_choice

    @staticmethod
    def customer_representative_menu() -> int:
        customer_representative_menu_choice = int(
            input("\n[1] - Ajouter un nouveau commercial\n")
        )

        return customer_representative_menu_choice

    @staticmethod
    def input_update_view(obj, key) -> str:

        new_value = input(f"{key} [{getattr(obj, key)}] : \n")

        return new_value

    def login_error(self, retries) -> None:
        print(f"Entrez vos identifiants. [{retries}] essais restants.")


class CustomerRepresentativeMenuView:

    def create_customer_representative(self) -> dict[str, str | int]:
        last_name = input("Nom ?\n")
        first_name = input("Prenom ?\n")
        email = input("Email ?\n")
        while not validate_email(email):
            email = input("Veuillez saisir un email valide")
        phone_number = input("Numéro de téléphone ?\n")
        while not validate_phone_number(phone_number):
            phone_number = input("Veuillez saisir un NUMERO de téléphone")
        password = input("Mot de passe commercial ?")

        return {
            "last_name": last_name,
            "first_name": first_name,
            "email": email,
            "phone_number": int(phone_number),
            "password": password,
        }


class CustomerMenuView:

    def create_customer(self) -> dict[str, str | int]:
        last_name = input("Nom du client ?\n")
        first_name = input("Prenom du client ?\n")
        email = input("Email du client ?\n")
        while not validate_email(email):
            email = input("Veuillez saisir un email valide")
        phone_number = input("Numéro de téléphone du client ?\n")
        while not validate_phone_number(phone_number):
            phone_number = input("Veuillez saisir un NUMERO de téléphone")
        company_name = input("Entreprise du client ?\n")

        return {
            "last_name": last_name,
            "first_name": first_name,
            "email": email,
            "phone_number": int(phone_number),
            "company_name": company_name,
        }

    def edit_customer(self, customer_list) -> Type[Customer]:

        which_one = int(input("Quel client souhaitez-vous modifier ?\n"))
        customer_to_edit = customer_list[which_one]

        return customer_to_edit

    def delete_customer(self, customer_list) -> str:

        which_one = int(input("Quel client souhaitez-vous supprimer ?\n"))
        customer_to_delete = customer_list[which_one]
        customer_id = customer_to_delete.id

        return customer_id

    def customer_dynamic_search_menu(self) -> Tuple[str, str]:
        filter_type = {
            1: "first_name",
            2: "last_name",
            3: "company_name",
            4: "email",
        }

        x = int(
            input(
                "Vous souhaitez rechercher un client par :"
                "\n[1] - Prénom"
                "\n[2] - Nom"
                "\n[3] - Entreprise"
                "\n[4] - Email"
            )
        )

        data_filter = filter_type[x]

        value = input(f"Que recherchez-vous comme valeur pour {data_filter}\n")

        return data_filter, value


class ContractMenuView:

    def create_contract(self, customer_list) -> dict[str, str | int]:
        name = input("Nom du contrat ?\n")
        total_amount = input("Montant du contrat ?\n")
        while not validate_total_amount(total_amount):
            total_amount = input("Saisissez en CHIFFRES le montant du contrat ?\n")
        amount_due = input("Reste à payer ?\n")
        while not validate_amount_due(total_amount, amount_due):
            amount_due = input(
                "Saisissez en CHIFFRES le montant restant à payer"
                "Le montant restant ne peut pas être superieur au"
                "montant total"
            )
        status = input("Statut ?\n")

        console_view = ConsoleView("Customers")
        console_view.display_customer_list(customer_list)

        which_customer = int(input("Quel client ?\n"))
        customer = customer_list[which_customer]

        return {
            "name": name,
            "total_amount": int(total_amount),
            "amount_due": int(amount_due),
            "status": status,
            "customer": customer,
        }

    def edit_contract(self, contract_list) -> Type[Contract]:

        console_view = ConsoleView("Contract List")
        console_view.display_contract_list(contract_list)

        which_one = int(input("Quel contrat souhaitez-vous modifier ?\n"))
        contract_to_edit = contract_list[which_one]

        return contract_to_edit

    def delete_contract(self, contract_list) -> str:

        which_one = int(input("Quel contrat souhaitez-vous supprimer ?\n"))
        contract_to_delete = contract_list[which_one]
        contract_id = contract_to_delete.id

        return contract_id

    def contract_dynamic_search_menu(self) -> Tuple[str, str]:
        filter_type = {
            1: "name",
            2: "status",
            3: "customer_email",
        }

        x = int(
            input(
                "Vous souhaitez rechercher un contrat par :"
                "\n[1] - Nom de contrat"
                "\n[2] - Status"
                "\n[3] - Client (adresse email)"
            )
        )

        data_filter = filter_type[x]

        value = input(f"Que recherchez-vous comme valeur pour {data_filter}\n")

        return data_filter, value


class EventMenuView:

    def create_event(self,
                     contract_list) -> Tuple[Any, dict[str, object]]:
        print(f"Contract list 6874684: {contract_list}")
        console_view = ConsoleView("Contracts")
        console_view.display_contract_list(contract_list)

        which_one = int(input("Pour quel contrat ?\n"))
        contract = contract_list[which_one]

        name = input("Quel est le nom de l'évènement ?\n")
        event_date_start = input("Quand commence l'évènement ? [AAAA-MM-JJ]\n")
        while not validate_date(event_date_start):
            print(
                "La date saisie est invalide."
                " Veuillez rééssayer au format AAAA-MM-JJ (Exemple: 2024-08-23)"
            )
            event_date_start = input("Quand commence l'évènement ? [AAAA-MM-JJ]\n")
        event_date_end = input("Et quand se termine-t-il ? [AAAA-MM-JJ]\n")
        while not validate_end_date(event_date_start, event_date_end):
            print(
                "La date saisie est invalide. Veuillez rééssayer au format AAAA-MM-JJ"
                " (Exemple: 2024-08-23). De plus, l'évenement ne pe pas se"
                " terminer avant d'avoir commencer."
            )
            event_date_end = input("Et quand se termine-t-il ? [AAAA-MM-JJ]\n")
        location = input("A quel endroit se tient cet évènement ?\n")
        attendees = input("Combien de personnes sont conviées à cet évènement ?\n")
        while not attendees.isnumeric():
            attendees = input("Combien de personnes sont conviées à cet évènement ?\n")
        notes = input("Notes :\n")

        event_infos = {
            "name": name,
            "event_date_start": event_date_start,
            "event_date_end": event_date_end,
            "location": location,
            "attendees": int(attendees),
            "notes": notes,
        }

        return contract, event_infos

    def edit_event(self, event_list) -> Type[Event]:

        console_view = ConsoleView("Event List")
        console_view.display_event_list(event_list)

        which_one = int(input("Quel évènement souhaitez-vous modifier ?\n"))
        event_to_edit = event_list[which_one]

        return event_to_edit

    def delete_event(self, event_list) -> str:
        console_view = ConsoleView("Event List")
        console_view.display_event_list(event_list)

        which_one = int(input("Quel évènement souhaitez-vous supprimer ?\n"))
        event_to_delete = event_list[which_one]
        event_id = event_to_delete.id

        return event_id

    def event_dynamic_search_menu(self) -> Tuple[str, str]:

        filter_type = {
            1: "name",
            2: "customer_email",
            3: "location",
            4: "notes"
        }

        x = int(
            input(
                "Vous souhaitez rechercher un évènement par :"
                "\n[1] - Nom d'évènement"
                "\n[2] - Client (adresse email)"
                "\n[3] - Endroit"
                "\n[4] - Notes\n"
            )
        )

        data_filter = filter_type[x]

        value = input(f"Que recherchez-vous comme valeur pour {data_filter}\n")

        return data_filter, value


class ConsoleView:

    def __init__(self, table_title):
        self.table = Table(
            title=table_title, width=200, header_style="bold", show_lines=True
        )
        self.console = Console(width=200)

    def display_event_list(self, event_list) -> None:

        columns = [
            "n°",
            "id",
            "name",
            "location",
            "attendees",
            "notes",
            "customer_email",
            "customer_representative_email",
            "contract_id",
            "event_date_start",
            "event_date_end",
        ]

        for column in columns:
            self.table.add_column(column)

        self.prepare_rows_for_table(event_list, columns)

        self.console.print(self.table)

    def display_customer_list(self, customer_list) -> None:

        columns = [
            "n°",
            "id",
            "first_name",
            "last_name",
            "phone_number",
            "company_name",
            "date_created",
            "date_modified",
            "customer_representative_id",
            "email",
        ]

        for column in columns:
            self.table.add_column(column)

        self.prepare_rows_for_table(customer_list, columns)

        self.console.print(self.table)

    def display_customer_representative_list(self, cr_list) -> None:

        columns = [
            "n°",
            "id",
            "last_name",
            "first_name",
            "email",
            "phone_number"
        ]

        for column in columns:
            self.table.add_column(column)

        self.prepare_rows_for_table(cr_list, columns)

        self.console.print(self.table)

    def display_contract_list(self, contract_list) -> None:

        columns = [
            "n°",
            "id",
            "name",
            "total_amount",
            "amount_due",
            "date_created",
            "status",
            "customer_email",
            "customer_representative_email",
        ]

        for column in columns:
            self.table.add_column(column)

        self.prepare_rows_for_table(contract_list, columns)

        self.console.print(self.table)

    def prepare_rows_for_table(self, item_list, columns) -> None:
        for i, item in enumerate(item_list):
            row = [str(i)]
            row.extend(
                [str(getattr(item, column))
                 for column in columns[1:]]
            )
            self.table.add_row(*row)
