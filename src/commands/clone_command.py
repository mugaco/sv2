import os
import subprocess
from colorama import Fore, Style
from . import Command
from helpers import get_branch_name_from_aliases,mprint
from halo import Halo

class CloneCommand(Command):
    def __init__(self, app):
        super().__init__(app)
        parser = app.subparsers.add_parser(
            "clone", help="Clona una rama remota en local"
        )
        parser.add_argument("alias", help="Alias de la rama remota a clonar")
        parser.add_argument(
            "-d",
            "--directory",
            default=".",
            help="Directorio local donde clonar la rama",
        )
        parser.add_argument(
            "-s",
            "--shallow",
            action="store_true",
            help="Realiza una clonación parcial para reducir el tamaño de descarga",
        )
        parser.set_defaults(command="clone")

    def run(self, args):
        self.clone(args)

    def clone(self, args):
        directory = args.directory
        shallow = args.shallow

        if not os.path.exists(directory):
            os.makedirs(directory)

        branch_name = get_branch_name_from_aliases(args.alias, self.app.aliases)
        if not branch_name:
            mprint(f"'{args.alias}' no es un alias válido. Consulta los alias con 'sv2 aliases'.",'e')
            return

        if branch_name == self.app.main_name:
            url = self.app.main
        elif branch_name == self.app.pre_name:
            url = self.app.pre
        else:
            url = f"{self.app.branches}/{branch_name}"

        svn_command = ["svn", "checkout", url, directory]
        if shallow:
            svn_command.extend(["--depth", "files"])

        try:
            spinner = Halo(text=f"Clonando rama {args.alias} ...", spinner="dots")
            spinner.start()
            result = subprocess.run(
                svn_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            if result.returncode != 0:
                print(
                    Fore.RED
                    + f"Error clonando la rama: {result.stderr}"
                    + Style.RESET_ALL
                )
            else:
                spinner.stop() 
                mprint(f"Rama clonada con éxtio en '{directory}'",'s')
        except Exception as e:
            print(Fore.RED + f"Error al ejecutar el comando SVN: {e}" + Style.RESET_ALL)
