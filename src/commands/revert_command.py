import subprocess
from colorama import Fore, Style
import os

from . import Command


class RevertCommand(Command):
    def __init__(self, app):
        super().__init__(app)
        parser = app.subparsers.add_parser(
            "revert", help="Revierte cambios con confirmación del usuario"
        )
        parser.add_argument(
            "files",
            nargs="*",
            help="Especifica los archivos a revertir. Si no se especifica ninguno, se revertirán todos los cambios.",
            default=None,
        )
        parser.add_argument(
            "-r",
            "--revision",
            type=int,
            help="Revierte el archivo a la revisión especificada. Si no se especifica, se revertirá al último estado en el repositorio.",
        )
        parser.set_defaults(command="revert")

    def run(self, args):
        self.super_revert(args)

    def super_revert(self, args):
        if not args.files and not args.revision:
            print(
                Fore.RED
                + "Error: Debes especificar archivos o una revisión."
                + Style.RESET_ALL
            )
            self.app.parser.print_help()
            return

        try:
            if args.revision and args.files:
                for file in args.files:
                    revert_command = f"svn update -r {args.revision} {file}"
                    subprocess.check_output(revert_command, shell=True)
                    print(
                        Fore.GREEN
                        + f"Archivo {file} revertido a la revisión {args.revision}."
                        + Style.RESET_ALL
                    )
                return

            elif args.files:
                paths_to_revert = args.files
            else:
                status_command = "svn status"
                output = subprocess.check_output(status_command, shell=True, text=True)
                paths_to_revert = [
                    line[8:] for line in output.splitlines() if line[0] in "AMDR"
                ]
                if not paths_to_revert:
                    print(
                        Fore.GREEN
                        + "No hay cambios pendientes para revertir."
                        + Style.RESET_ALL
                    )
                    return

            print(
                Fore.RED
                + "Archivos/Directorios que serán revertidos:"
                + Style.RESET_ALL
            )
            for path in paths_to_revert:
                print(
                    Fore.CYAN
                    + f"{'Directorio' if os.path.isdir(path) else 'Archivo'}: {path}"
                    + Style.RESET_ALL
                )

            print(
                Fore.YELLOW
                + "¿Desea continuar con la reversión? (y/n):"
                + Style.RESET_ALL
            )
            if input().strip().lower() == "y":
                for path in paths_to_revert:
                    revert_command = (
                        f"svn revert -R {path}"
                        if os.path.isdir(path)
                        else f"svn revert {path}"
                    )
                    subprocess.check_output(revert_command, shell=True)
                print(Fore.GREEN + "Cambios revertidos con éxtio." + Style.RESET_ALL)
            else:
                print(
                    Fore.RED + "Reversión cancelada por el usuario." + Style.RESET_ALL
                )

        except subprocess.CalledProcessError as e:
            print(Fore.RED + f"Error al ejecutar el comando: {e}" + Style.RESET_ALL)
