import subprocess
from colorama import Fore, Style
from tabulate import tabulate
from . import Command


class StatusCommand(Command):
    def __init__(self, app):
        super().__init__(app)
        parser = app.subparsers.add_parser(
            "st", help="Muestra el estado del repositorio"
        )
        parser.set_defaults(command="st")

        parser_l = app.subparsers.add_parser(
            "status", help="Muestra el estado del repositorio"
        )
        parser_l.set_defaults(command="status")

    def run(self, args):
        self.custom_status()

    def custom_status(self):
        print(Fore.CYAN + "Verificando el estado del repositorio..." + Style.RESET_ALL)
        try:
            status_command = "svn st"
            output = subprocess.check_output(status_command, shell=True, text=True)
            if output.strip() == "":
                print(Fore.GREEN + "No hay cambios pendientes." + Style.RESET_ALL)
            else:
                output_lines = output.split("\n")
                data = [line.split(maxsplit=1) for line in output_lines if line.strip()]
                print(tabulate(data, headers=["Estado", "Archivo"], tablefmt="grid"))
        except subprocess.CalledProcessError as e:
            print(Fore.RED + f"Error al verificar el estado: {e}" + Style.RESET_ALL)
