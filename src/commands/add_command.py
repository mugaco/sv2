import subprocess
import os
from colorama import Fore, Style
from . import Command


class AddCommand(Command):
    def __init__(self, app):
        super().__init__(app)
        parser = app.subparsers.add_parser(
            "add",
            help="Añade archivos o carpetas al control de versiones de manera recursiva",
        )
        parser.add_argument(
            "path", help="Ruta del archivo o carpeta a añadir", nargs="?", default="."
        )
        parser.set_defaults(command="add")

    def run(self, args):
        self.add_to_version_control(args)

    def add_to_version_control(self, args):
        path = args.path
        if os.path.exists(path):
            if os.path.isdir(path):
                add_command = f"svn add {path} --force --depth infinity"
            else:
                add_command = f"svn add {path}"

            try:
                subprocess.check_output(add_command, shell=True)
                print(
                    Fore.GREEN
                    + f"'{path}' añadido con éxtio al control de versiones."
                    + Style.RESET_ALL
                )
            except subprocess.CalledProcessError as e:
                print(Fore.RED + f"Error al añadir '{path}': {e}" + Style.RESET_ALL)
        else:
            print(
                Fore.RED + f"La ruta especificada '{path}' no existe." + Style.RESET_ALL
            )
