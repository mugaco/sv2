# /usr/local/bin/sv2/src/commands/list_command.py

import subprocess
from colorama import Fore, Style
from tabulate import tabulate
from . import Command


class ListCommand(Command):
    def __init__(self, app):
        super().__init__(app)
        parser = app.subparsers.add_parser(
            "list", help="Mostrar la relación de ramas en el repositorio servidor"
        )
        parser.set_defaults(command="list")

    def run(self, args):
        print(
            Fore.GREEN + "Lista de ramas en el repositorio servidor" + Style.RESET_ALL
        )
        try:
            branches_url = self.app.branches
            svn_command = f"svn list {branches_url}"
            output = subprocess.check_output(svn_command, shell=True, text=True)

            # Crear la tabla de ramas
            branches_list = output.strip().split("\n")
            data = [["main", "trunk2"]]
            data.extend([[i + 1, branch] for i, branch in enumerate(branches_list)])

            print(tabulate(data, headers=["Branch", "Nombre"], tablefmt="grid"))

        except subprocess.CalledProcessError as e:
            print(Fore.RED + f"Error al listar las ramas: {e}" + Style.RESET_ALL)
