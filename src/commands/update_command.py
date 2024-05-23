import subprocess
from colorama import Fore, Style
from . import Command
from helpers import get_branch_name_from_aliases, hay_cambios


class UpdateCommand(Command):
    def __init__(self, app):
        super().__init__(app)
        # parser = app.subparsers.add_parser(
        #     "update", help="Actualiza la rama actual al estado remoto"
        # )
        # # Alias "up" para el comando "update"
        # up_parser = app.subparsers.add_parser(
        #     "up", help="Actualiza la rama actual al estado remoto"
        # )
        # parser.add_argument(
        #     "-f", "--from", dest="from_branch", help="Nombre del alias de la rama desde la cual traer los cambios", type=str, default=None
        # )
        # parser.set_defaults(command="update")

        # --------
        # Comando update
        update_parser = app.subparsers.add_parser(
            "update", help="Actualiza la rama actual al estado remoto"
        )
        update_parser.add_argument(
            "-f",
            "--from",
            dest="from_branch",
            help="Nombre del alias de la rama desde la cual traer los cambios",
            type=str,
            default=None,
        )
        update_parser.set_defaults(command="update")

        # Alias "up" para el comando "update"
        up_parser = app.subparsers.add_parser(
            "up", help="Actualiza la rama actual al estado remoto"
        )
        up_parser.add_argument(
            "-f",
            "--from",
            dest="from_branch",
            help="Nombre del alias de la rama desde la cual traer los cambios",
            type=str,
            default=None,
        )
        up_parser.set_defaults(command="up")
        # --------

    def run(self, args):
        self.custom_update(args)

    def custom_update(self, args):
        print(Fore.CYAN + "Actualizando repositorio..." + Style.RESET_ALL)
        try:
            update_command = "svn up"
            if args.from_branch:
                branch_name = get_branch_name_from_aliases(
                    args.from_branch, self.app.aliases
                )
                if branch_name == self.app.main_name:
                    branch_url = self.app.main
                elif branch_name == self.app.pre_name:
                    branch_url = self.app.pre    
                else:
                    branch_url = f"{self.app.branches}/{branch_name}"

                if not branch_url:
                    print(
                        Fore.RED
                        + f"Rama '{args.from_branch}' no encontrada."
                        + Style.RESET_ALL
                    )
                    return

                update_command = f"svn merge {branch_url}"

            output = subprocess.check_output(update_command, shell=True, text=True)

            for line in output.split("\n"):
                if "At revision" in line or "Completado" in line:
                    print(Fore.GREEN + line + Style.RESET_ALL)
                elif line.strip():
                    print(Fore.YELLOW + line + Style.RESET_ALL)

            changes_detected = hay_cambios(output)
            print(
                Fore.CYAN + f"Cambios detectados: {changes_detected}" + Style.RESET_ALL
            )

        except subprocess.CalledProcessError as e:
            print(Fore.RED + f"Error al actualizar: {e}" + Style.RESET_ALL)
