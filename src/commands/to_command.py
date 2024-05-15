import subprocess
from colorama import Fore, Style
from . import Command
from helpers import get_branch_name_from_aliases


class ToCommand(Command):
    def __init__(self, app):
        super().__init__(app)
        parser = app.subparsers.add_parser(
            "to", help="Cambia a una rama especificada por alias"
        )
        parser.add_argument("alias", help="Alias de la rama a la cual cambiar")
        parser.add_argument(
            "-f",
            "--force",
            action="store_true",
            help="Ignora los cambios sin confirmar en la rama actual y cambia de rama",
        )
        parser.set_defaults(command="to")

    def run(self, args):
        self.switch_to_branch(args)

    def switch_to_branch(self, args):
        alias = args.alias
        branch_name = get_branch_name_from_aliases(alias, self.app.aliases)
        if not branch_name:
            print(
                Fore.RED
                + f"No se encontró una rama correspondiente al alias '{alias}'."
                + Style.RESET_ALL
            )
            return

        # branch_url = self.app.main if branch_name == self.app.main_name else f"{self.app.branches}/{branch_name}"
        if branch_name == self.app.main_name or branch_name == self.app.pre_name:
            branch_url = f"{self.app.base}/{branch_name}"
        else:
            branch_url = f"{self.app.branches}/{branch_name}"

        if not args.force:
            try:
                status_output = subprocess.check_output(
                    "svn status", shell=True, text=True
                )
                if status_output.strip():
                    print(
                        Fore.RED
                        + "Hay cambios sin confirmar en la rama actual"
                        + Style.RESET_ALL
                    )
                    print(
                        Fore.GREEN
                        + "Por favor, haga commit o revert antes de cambiar de rama."
                        + Style.RESET_ALL
                    )
                    return
            except subprocess.CalledProcessError as e:
                print(Fore.RED + f"Error al cambiar a la rama: {e}" + Style.RESET_ALL)
                return

        try:
            svn_command = f"svn switch {branch_url}"
            subprocess.check_output(svn_command, shell=True)
            print(
                Fore.GREEN
                + f"Cambiado con éxtio a la rama '{branch_name}'."
                + Style.RESET_ALL
            )
        except subprocess.CalledProcessError as e:
            print(Fore.RED + f"Error al cambiar a la rama: {e}" + Style.RESET_ALL)
