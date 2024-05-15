import subprocess
from colorama import Fore, Style
from . import Command
from helpers import get_branch_name_from_aliases, get_alias_from_branch_name, get_parent


class MergeCommand(Command):
    def __init__(self, app):
        super().__init__(app)
        parser = app.subparsers.add_parser(
            "merge",
            help="Fusiona los cambios de la rama especificada por alias a la rama actual",
        )
        parser.add_argument("alias", help="Alias de la rama desde la cual fusionar")
        parser.set_defaults(command="merge")

    def run(self, args):
        self.merge(args)

    def merge(self, args):
        parent = get_parent(self.app.ancestor, self.app.main_name)

        if parent is None:
            print(
                Fore.RED
                + f"Solo el administrador debería fusionar pre a main."
                + Style.RESET_ALL
            )
            return
        # print(self.app.pre_name)
        if parent == self.app.main_name:
            print(
                Fore.RED
                + f"Una rama de nivel 'proyecto' no debe fusionarse directamente a 'pre'. En su lugar hacer 'sv2 to rama-proyecto' y desde ahí solicitar un pull request con 'sv2 pr'."
                + Style.RESET_ALL
            )
            return
        branch_name = get_branch_name_from_aliases(args.alias, self.app.aliases)
        # print(self.app.aliases)
        # print(branch_name)

        ali = args.alias

        if not branch_name:
            print(
                Fore.RED
                + f"No se encontró una rama correspondiente al alias '{args.alias}'."
                + Style.RESET_ALL
            )
            return

        if branch_name == self.app.main_name:
            print(
                Fore.RED
                + f"No se debe fusionar 'main' en ninguna rama."
                + Style.RESET_ALL
            )
            return
        else:
            branch_url = f"{self.app.branches}/{branch_name}"
        # print(branch_url)
        # return
        try:
            merge_command = f"svn merge {branch_url} --accept postpone"
            subprocess.check_output(merge_command, shell=True)
            print(
                Fore.GREEN
                + f"Rama {branch_name} ({args.alias}) fusionada con éxtio en la rama actual."
                + Style.RESET_ALL
            )

            # Preguntar al usuario si desea hacer commit de los cambios fusionados
            print(
                Fore.YELLOW
                + f"¿Desea hacer commit con el comentario 'merge from {branch_name}'? (y/n):"
                + Style.RESET_ALL
            )
            response = input().strip().lower()
            if response == "y":
                commit_message = f"merge from {branch_name}"
                commit_command = f'svn commit -m "{commit_message}"'
                subprocess.check_output(commit_command, shell=True)
                print(Fore.GREEN + "Commit realizado con éxtio." + Style.RESET_ALL)
                if self.app.pre_name == branch_name:
                    return
                print(
                    Fore.YELLOW
                    + f"¿Desea borrar la rama {branch_name} ({ali})? (y/n):"
                    + Style.RESET_ALL
                )
                response = input().strip().lower()
                if response == "y":
                    # commit_command = f'svd branch -D {ali}'
                    commit_command = f'svn delete {branch_url} -m "Eliminada rama fusionada branch_name"'
                    # "svn delete {branch_url} -m \"Eliminada rama fusionada branch_name\""
                    # print(commit_command)
                    subprocess.check_output(commit_command, shell=True)
                    print(Fore.GREEN + "Rama borrada con éxtio." + Style.RESET_ALL)
                else:
                    print(Fore.CYAN + "La rama no se borró" + Style.RESET_ALL)
            else:
                print(Fore.CYAN + "Commit cancelado por el usuario." + Style.RESET_ALL)

        except subprocess.CalledProcessError as e:
            print(Fore.RED + f"Error al fusionar la rama: {e}" + Style.RESET_ALL)
