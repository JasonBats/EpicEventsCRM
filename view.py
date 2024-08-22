from rich import print
from rich.console import Console
from rich.table import Table


class LoginView:
    def get_credentials(self):
        user = input("Login :")
        password = input("Password :")

        return user, password


class MainView:

    @staticmethod
    def main_menu():
        main_choice = int(input("Quel menu ouvrir ?"
                                "\n[1] - Clients"
                                "\n[2] - Contrats"
                                "\n[3] - Évenements\n"))

        return main_choice

    @staticmethod
    def client_menu():
        client_menu_choice = int(input("-- CLIENTS --\n"
                                       "Souahitez-vous :"
                                       "\n[1] - Ajouter un client"
                                       "\n[2] - Modifier un client"
                                       "\n[3] - Supprimer un client"
                                       "\n ---"
                                       "\n[4] - Liste de tous les clients"
                                       "\n[5] - Rechercher un client\n"))

        return client_menu_choice

    @staticmethod
    def contract_menu():
        contract_menu_choice = int(input("-- CONTRATS --\n"
                                         "Souahitez-vous :"
                                         "\n[1] - Ajouter un contrat"
                                         "\n[2] - Modifier un contrat"
                                         "\n[3] - Supprimer un contrat"
                                         "\n ---"
                                         "\n[4] - Liste de tous les contrats"
                                         "\n[5] - Contrats non réglés"
                                         "\n ---"
                                         "\n[6] - Rechercher un contrat\n"))

        return contract_menu_choice

    @staticmethod
    def event_menu():
        event_menu_choice = int(input("-- ÉVÈNEMENTS --\n"
                                      "Souahitez-vous :"
                                      "\n[1] - Ajouter un évènement"
                                      "\n[2] - Modifier un évènement"
                                      "\n[3] - Supprimer un évènement"
                                      "\n ---"
                                      "\n[4] - Liste de tous les évènements"
                                      "\n[5] - Évènements à venir"
                                      "\n[6] - Évènements passés"
                                      "\n ---"
                                      "\n[7] - Rechercher un évènement\n"))

        return event_menu_choice


class CustomerMenuView:

    def create_customer(self, cr_list):
        last_name = input("Nom du client ?\n")
        first_name = input("Prenom du client ?\n")
        email = input("Email du client ?\n")
        phone_number = int(input("Numéro de téléphone du client ?\n"))
        company_name = input("Entreprise du client ?\n")
        console_view = ConsoleView("Customer Representatives")
        console_view.display_customer_representative_list(cr_list)
        which_one = input("Client attribué à ?\n")
        customer_representative = cr_list[int(which_one)][3]

        return {'last_name': last_name,
                'first_name': first_name,
                'email': email,
                'phone_number': phone_number,
                'company_name': company_name,
                'customer_representative': customer_representative}

    def edit_customer(self, customer_list):

        which_one = int(input("Quel client souhaitez-vous modifier ?\n"))
        customer_to_edit = customer_list[which_one]
        print(customer_to_edit)

        return customer_to_edit

    def delete_customer(self, customer_list):

        which_one = int(input("Quel client souhaitez-vous supprimer ?\n"))
        customer_to_delete = customer_list[which_one]
        customer_id = customer_to_delete[8]

        return customer_id

    def customer_dynamic_search_menu(self):
        filter_type = {
            1: "first_name",
            2: "last_name",
            3: "company_name",
            4: "email",
            5: "customer_representative",
        }

        x = int(input("Vous souhaitez rechercher un évènement par :"
                      "\n[1] - Prénom"
                      "\n[2] - Nom"
                      "\n[3] - Entreprise"
                      "\n[4] - Email"
                      "\n[5] - Représentant commercial (email)"))

        data_filter = filter_type[x]

        value = input(f"Que recherchez-vous comme valeur pour {data_filter}\n")

        return data_filter, value


class ContractMenuView:

    def create_contract(self, cr_list, customer_list):
        name = input("Nom du contrat ?\n")
        total_amount = float(input("Montant du contrat ?\n"))
        amount_due = float(input("Reste à payer ?\n"))
        status = input("Statut ?\n")

        console_view = ConsoleView("Customer Representatives")
        console_view.display_customer_representative_list(cr_list)
        which_cr = int(input("Quel commercial ?\n"))
        customer_representative_id = cr_list[which_cr][0]
        print(customer_representative_id)
        customer_representative_email = cr_list[which_cr][3]

        console_view = ConsoleView("Customers")
        console_view.display_customer_list(customer_list)

        which_customer = int(input("Quel client ?\n"))
        customer_email = customer_list[which_customer][7]
        customer_id = customer_list[which_customer][8]

        return {
            'name': name,
            'total_amount': total_amount,
            'amount_due': amount_due,
            'status': status,
            'customer_representative_id': customer_representative_id,
            'customer_representative_email': customer_representative_email,
            'customer_email': customer_email,
            'customer_id': customer_id
        }

    def edit_contract(self, contract_list):

        console_view = ConsoleView("Contract List")
        console_view.display_contract_list(contract_list)

        which_one = int(input("Quel contrat souhaitez-vous modifier ?\n"))
        contract_to_edit = contract_list[which_one]

        return contract_to_edit

    def delete_contract(self, contract_list):

        which_one = int(input("Quel contrat souhaitez-vous supprimer ?\n"))
        contract_to_delete = contract_list[which_one]
        contract_id = contract_to_delete[0]

        return contract_id

    def contract_dynamic_search_menu(self):
        filter_type = {
            1: "name",
            2: "status",
            3: "customer_email",
            4: "customer_representative_email",
        }

        x = int(input("Vous souhaitez rechercher un contrat par :"
                      "\n[1] - Nom de contrat"
                      "\n[2] - Status"
                      "\n[3] - Client (adresse email)"
                      "\n[4] - Commercial (adresse email)\n"))

        data_filter = filter_type[x]

        value = input(f"Que recherchez-vous comme valeur pour {data_filter}\n")

        return data_filter, value


class EventMenuView:

    def create_event(self, contract_list):
        console_view = ConsoleView("Contracts")
        console_view.display_contract_list(contract_list)

        which_one = int(input("Pour quel contrat ?\n"))
        contract = contract_list[which_one]

        name = input("Quel est le nom de l'évènement ?\n")
        event_date_start = input("Quand commence l'évènement ? [AAAA-MM-JJ]\n")
        event_date_end = input("Et quand se termine-t-il ? [AAAA-MM-JJ]\n")
        location = input("A quel endroit se tient cet évènement ?\n")
        attendees = int(input("Combien de personnes sont conviées à cet évènement ?\n"))
        notes = input("Notes :\n")

        event_infos = {
            "name": name,
            "event_date_start": event_date_start,
            "event_date_end": event_date_end,
            "location": location,
            "attendees": attendees,
            "notes": notes
        }

        return contract, event_infos

    def edit_event(self, event_list):

        console_view = ConsoleView("Event List")
        console_view.display_event_list(event_list)

        which_one = int(input("Quel évènement souhaitez-vous modifier ?\n"))
        event_to_edit = event_list[which_one]

        return event_to_edit

    def delete_event(self, event_list):
        console_view = ConsoleView("Event List")
        console_view.display_event_list(event_list)

        which_one = int(input("Quel évènement souhaitez-vous supprimer ?\n"))
        event_to_delete = event_list[which_one]
        event_id = event_to_delete[1]

        return event_id

    def event_dynamic_search_menu(self):

        filter_type = {
            1: "name",
            2: "customer_email",
            3: "customer_representative_email",
            4: "location",
            5: "notes"
        }

        x = int(input("Vous souhaitez rechercher un évènement par :"
                      "\n[1] - Nom d'évènement"
                      "\n[2] - Client (adresse email)"
                      "\n[3] - Commercial (adresse email)"
                      "\n[4] - Endroit"
                      "\n[5] - Notes\n"))

        data_filter = filter_type[x]

        value = input(f"Que recherchez-vous comme valeur pour {data_filter}\n")

        return data_filter, value


class ConsoleView:

    def __init__(self, table_title):
        self.table = Table(title=table_title,
                           width=200,
                           header_style="bold",
                           show_lines=True)
        self.console = Console(width=200)

    def display_event_list(self, event_list):

        columns = ["n°", "id", "name", "location", "attendees", "notes",
                   "customer_email", "customer_representative_email", "dates", "contract"]

        for column in columns:
            self.table.add_column(column)

        for i, event in enumerate(event_list):
            self.table.add_row(
                str(i),
                str(event[1]),
                event[0],
                event[8],
                str(event[9]),
                event[10],
                event[3],
                event[5],
                f"{event[6]} -> {event[7]}",
                event[11]
            )

        self.console.print(self.table)

    def display_customer_list(self, customer_list):

        columns = ["n°", "first_name", "last_name", "phone_number", "company_name",
                   "date_created", "date_modified", "customer_representative",
                   "email", "id"]

        for column in columns:
            self.table.add_column(column)

        for i, customer in enumerate(customer_list):
            self.table.add_row(str(i), *[str(item) for item in customer])

        self.console.print(self.table)

    def display_customer_representative_list(self, cr_list):

        columns = ["n°", "id", "last_name", "first_name", "email",
                   "phone_number"]

        for column in columns:
            self.table.add_column(column)

        for i, customer in enumerate(cr_list):
            self.table.add_row(str(i), *[str(item) for item in customer])

        self.console.print(self.table)

    def display_contract_list(self, contract_list):

        columns = ["n°", "id", "name", "total_amount", "amount_due",
                   "date_created", "status", "customer_email",
                   "customer_representative_email"]

        for column in columns:
            self.table.add_column(column)

        for i, contract in enumerate(contract_list):
            self.table.add_row(
                str(i),
                contract[0],
                contract[1],
                str(contract[2]),
                str(contract[3]),
                str(contract[4]),
                contract[5],
                contract[6],
                contract[9]
            )

        self.console.print(self.table)
