import subprocess
from tabulate import tabulate
from colorama import Fore, Style
from . import Command
from helpers import (
    get_parent,
    get_branch_name_from_aliases,
    info_get_lines,
    get_alias_from_branch_name,
    get_children_branches,
    print_branch_hierarchy,
)


class InfoCommand(Command):
    def __init__(self, app):
        super().__init__(app)
        parser = app.subparsers.add_parser(
            "info", help="Muestra información de la rama actual"
        )
        parser_c = app.subparsers.add_parser(
            "i", help="Muestra información de la rama actual"
        )
        parser.add_argument(
            "-v",
            "--verbose",
            action="store_true",
            help="Muestra información detallada de la rama actual",
        )
        parser_c.add_argument(
            "-v",
            "--verbose",
            action="store_true",
            help="Muestra información detallada de la rama actual",
        )
        parser.set_defaults(command="info")
        parser_c.set_defaults(command="i")

    def run(self, args):
        if args.verbose:
            self.info_verbose()
        else:
            self.info_little()

    def info_verbose(self):
        try:
            info_lines = info_get_lines()
            data = [
                [key.strip(), value.strip()]
                for key, value in (line.split(":", 1) for line in info_lines)
            ]
            print(Fore.GREEN + "Información sobre la rama actual" + Style.RESET_ALL)
            print(tabulate(data, tablefmt="grid"))

        except subprocess.CalledProcessError as e:
            print(
                Fore.RED
                + f"Error al obtener información de la rama actual: {e}"
                + Style.RESET_ALL
            )

    def info_little(self):
        try:
            info_lines = info_get_lines()
            branch_url = next(
                line.split(": ", 1)[1] for line in info_lines if line.startswith("URL:")
            )
            branch_name = branch_url.split("/")[-1]
            alias = get_alias_from_branch_name(branch_name, self.app.aliases)

            # Buscar la rama padre
            # self.app.parent_branch_alias = get_parent(self.app.ancestor,self.app.main_name)
            # self.app.parent_branch_name = get_branch_name_from_aliases(self.app.parent_branch_alias,self.app.aliases)

            parent_branch_formatted = (
                f"{self.app.parent_branch_alias} ({self.app.parent_branch_name})"
            )

            # Buscar ramas hijas
            children_branches = get_children_branches(
                branch_name, self.app.aliases, self.app.branches, self.app.ancestor
            )

            # Mostrar la información de la rama actual, padre e hijos
            if parent_branch_formatted:
                print(Fore.CYAN + f"Padre: {parent_branch_formatted}" + Style.RESET_ALL)
            print(
                Fore.GREEN + f"Rama actual: {alias} ({branch_name})" + Style.RESET_ALL
            )

            print_branch_hierarchy(children_branches)

        except subprocess.CalledProcessError as e:
            print(
                Fore.RED
                + f"Error al obtener información de la rama actual: {e}"
                + Style.RESET_ALL
            )
