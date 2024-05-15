from tabulate import tabulate
from colorama import Fore, Style
from . import Command


class AliasesCommand(Command):
    def __init__(self, app):
        super().__init__(app)
        parser = app.subparsers.add_parser(
            "aliases", help="Mostrar la relación entre alias y nombres de ramas"
        )
        parser.set_defaults(command="aliases")

    def run(self, args):
        print(Fore.GREEN + "Relación entre alias y nombres de ramas" + Style.RESET_ALL)
        data = [[key, value] for key, value in self.app.aliases.items()]
        print(tabulate(data, headers=["Alias", "Rama"], tablefmt="grid"))
