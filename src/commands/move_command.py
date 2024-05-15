import subprocess
from colorama import Fore, Style
from tabulate import tabulate
from . import Command
from helpers import info_get_lines, get_branch_name_from_aliases
from spinner import start_spinner


class MoveCommand(Command):
    def __init__(self, app):
        super().__init__(app)
        parser = app.subparsers.add_parser(
            "move",
            help="Renombra una rama",
        )
        parser_c = app.subparsers.add_parser(
            "mv",
            help="Renombra una rama",
        )
        parser_c.add_argument(
            "aliases",
            help="Alias de la rama a mover y nuevo alieas; por ejemplo alias-actual:nuevo-alias",
        )

        parser.set_defaults(command="move")
        parser_c.set_defaults(command="mv")

    def run(self, args):
        self.move(args)

    def move(self, args):
        if ":" not in args.aliases:
            print(Fore.RED + 'Los alias deben separarse con ":"' + Style.RESET_ALL)
            return
        aliases = args.aliases.split(":")
        desde = get_branch_name_from_aliases(aliases[0], self.app.aliases)
        if desde is None:
            print(
                Fore.RED
                + "El alias de la rama que se quiere renombrar no existe"
                + Style.RESET_ALL
            )
            return
        if desde == self.app.pre_name or desde == self.app.main_name:
            print(Fore.RED + f"La rama {desde} no se puede renombrar" + Style.RESET_ALL)
            return

        desde_url = f"{self.app.branches}/{desde}"
        hasta_url = f"{self.app.branches}/{aliases[1]}"

        mv_command = f'svn move {desde_url} {hasta_url} -m"movida rama de {desde_url} a{hasta_url}"'

        try:
            stop_spinner = start_spinner()  # Inicia el spinner

            subprocess.check_output(mv_command, shell=True, text=True)
            if self.app.env == "DEV":
                subprocess.check_output("svd build-aliases", shell=True, text=True)
                na = aliases[1].split(self.app.ancestor)
                a = na.pop()
                cc = f"svd edal {a} -a {aliases[0]}"
                subprocess.check_output(cc, shell=True, text=True)
            else:
                subprocess.check_output("sv2 build-aliases", shell=True, text=True)
                na = aliases[1].split(self.app.ancestor)
                a = na.pop()
                cc = f"sv2 edal {a} -a {aliases[0]}"
                subprocess.check_output(cc, shell=True, text=True)

            print(Fore.GREEN + f"Rama renombrada a {aliases[1]}" + Style.RESET_ALL)

        except subprocess.CalledProcessError as e:
            print(Fore.RED + f"Error al ejecutar svn move: {e}" + Style.RESET_ALL)
        finally:
            stop_spinner()  # Detiene el spinner una vez que la operación ha terminado
