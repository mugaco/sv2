import subprocess
from colorama import Fore, Style
from . import Command
from halo import Halo
from helpers import dialog, mprint

class CommitCommand(Command):
    def __init__(self, app):
        super().__init__(app)
        parser = app.subparsers.add_parser(
            "commit", help="Realiza una confirmación de cambios en el repositorio SVN"
        )
        parser_c = app.subparsers.add_parser(
            "c", help="Realiza una confirmación de cambios en el repositorio SVN"
        )
        parser.add_argument(
            "-m",
            "--message",
            help="Mensaje descriptivo del commit",
            type=str,
            default=None,
        )
        parser_c.add_argument(
            "-m",
            "--message",
            help="Mensaje descriptivo del commit",
            type=str,
            default=None,
        )
        parser.add_argument(
            "files", nargs="*", help="Archivos específicos a comprometer"
        )
        parser_c.add_argument(
            "files", nargs="*", help="Archivos específicos a comprometer"
        )
        parser.set_defaults(command="commit")
        parser_c.set_defaults(command="c")

    def run(self, args):
        self.commit(args)

    def commit(self, args):

        message = args.message
        if not message:
            message = dialog("Por favor, añade un comentario para el commit")
            spinner = Halo(text="Realizando commit...", spinner="dots")
            spinner.start()
            if not message:
                mprint("Commit cancelado: No se proporcionó un mensaje.",'e')
                return

        if args.files:
            files_to_commit = " ".join(args.files)
            commit_command = f'svn commit {files_to_commit} -m "{message}"'
        else:
            commit_command = f'svn commit -m "{message}"'

        try:
            output = subprocess.check_output(commit_command, shell=True, text=True)
            if output.strip():
                # spinner = Halo(text="Realizando commit...", spinner="dots")
                # spinner.start()
                # print(Fore.GREEN + "Commit realizado con éxtio." + Style.RESET_ALL)
                spinner.stop() 
                print()
                # print(output)
                for line in output.strip().split('\n'):
                    spinner.succeed(line)
                spinner.succeed("Commit realizado con éxtio.")
            else:
                spinner.warn("No había cambios para confirmar. Puedes comprobar que no haya archivos sin añadir con 'sv2 st'.")
        except subprocess.CalledProcessError as e:
            print(Fore.RED + f"Error al realizar el commit: {e}" + Style.RESET_ALL)
