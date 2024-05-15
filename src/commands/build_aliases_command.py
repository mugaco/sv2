import subprocess
import json
from colorama import Fore, Style
from . import Command
from helpers import get_repo_name, load_branch_aliases


class BuildAliasesCommand(Command):
    def __init__(self, app):
        super().__init__(app)
        parser = app.subparsers.add_parser(
            "build-aliases",
            help="Reconstruye la relación aliases a partir de las ramas actuales en el servidor",
        )
        parser.set_defaults(command="build-aliases")

    def run(self, args):
        self.build_aliases()

    def build_aliases(self):
        try:
            svn_command = f"svn list {self.app.branches}"
            output = subprocess.check_output(svn_command, shell=True, text=True)
            current_branches = [
                branch.rstrip("/") for branch in output.strip().split("\n")
            ]
            repo_name = get_repo_name()

            aliases = load_branch_aliases(self.app.config_path)

            existing_aliases = aliases.get(repo_name, {})
            values = self.build_value(existing_aliases, current_branches)
            aliases[repo_name] = values
            with open(self.app.config_path, "w") as file:
                json.dump(aliases, file, indent=4)

            print(
                Fore.GREEN
                + "El archivo svnAliases.json ha sido actualizado con éxtio."
                + Style.RESET_ALL
            )
            return

        except subprocess.CalledProcessError as e:
            print(
                Fore.RED
                + f"Error al reconstruir el archivo svnAliases.json: {e}"
                + Style.RESET_ALL
            )

    def build_value(self, existing_aliases, current_branches):
        try:
            current_branches.remove(self.app.pre_name)
        except ValueError:
            pass  # No hacer nada si el valor no se encuentra en la lista
        try:
            branch_to_alias = {v: k for k, v in existing_aliases.items()}

            new_aliases = {
                "main": self.app.main_name,
                "pre": self.app.pre_name,
            }

            for branch in current_branches:
                if branch in branch_to_alias:
                    new_aliases[branch_to_alias[branch]] = branch
                else:
                    new_alias = branch.replace(self.app.prefijo_rama, "").split(
                        self.app.ancestor
                    )[-1]
                    new_aliases[new_alias] = branch

            return new_aliases

        except subprocess.CalledProcessError as e:
            print(
                Fore.RED
                + f"Error al reconstruir aliases para la key: {e}"
                + Style.RESET_ALL
            )
