import subprocess
from colorama import Fore, Style
from . import Command


class RemoveCommand(Command):
    def __init__(self, app):
        super().__init__(app)
        parser = app.subparsers.add_parser(
            "rm", help="Borra archivos o directorios del repositorio SVN"
        )
        parser.add_argument("path", help="Ruta del archivo o directorio a borrar")
        parser.add_argument(
            "-m",
            "--message",
            default="Eliminando archivo o directorio",
            help="Mensaje de commit para la operación de borrado",
        )
        parser.set_defaults(command="rm")

    def run(self, args):
        if self.valid_path(args.path):
            if self.is_directory(args.path) and not self.confirm_deletion(args.path):
                print(
                    Fore.YELLOW
                    + "Operación cancelada por el usuario."
                    + Style.RESET_ALL
                )
                return
            self.delete_item(args.path)
            self.commit_changes(args.path, args.message)

    def valid_path(self, path):
        info_command = f"svn info {path}"
        try:
            subprocess.check_output(info_command, shell=True, stderr=subprocess.STDOUT)
            return True
        except subprocess.CalledProcessError:
            print(
                Fore.RED
                + f"Error: La ruta '{path}' no existe en el repositorio."
                + Style.RESET_ALL
            )
            return False

    def delete_item(self, path):
        delete_command = f"svn delete {path}"
        try:
            subprocess.check_output(delete_command, shell=True)
            print(
                Fore.GREEN
                + f"El archivo/directorio '{path}' ha sido preparado para eliminar."
                + Style.RESET_ALL
            )
        except subprocess.CalledProcessError as e:
            print(
                Fore.RED
                + f"Error al borrar el archivo/directorio '{path}': {e.output}"
                + Style.RESET_ALL
            )

    def commit_changes(self, path, message):
        commit_command = f"svn commit -m '{message}'"
        try:
            subprocess.check_output(commit_command, shell=True)
            print(
                Fore.GREEN
                + f"El archivo/directorio '{path}' ha sido eliminado exitosamente del repositorio SVN."
                + Style.RESET_ALL
            )
        except subprocess.CalledProcessError as e:
            print(
                Fore.RED
                + f"Error al commit el borrado del archivo/directorio '{path}': {e.output}"
                + Style.RESET_ALL
            )

    # def is_directory(self, path):
    #     return path.endswith('/') or any(char in path for char in ('/', '\\'))

    def is_directory(self, path):
        try:
            info_output = subprocess.check_output(
                f"svn info {path}", shell=True, text=True
            )
            for line in info_output.splitlines():
                if line.startswith("Node Kind:"):
                    return "directory" in line
        except subprocess.CalledProcessError:
            print(
                Fore.RED
                + f"Error: No se pudo obtener la información de '{path}'."
                + Style.RESET_ALL
            )
            return False  # Si no se puede obtener la información, asumir que no es un directorio.

        return False  # Por defecto, no es un directorio si no se encuentra la línea esperada.

    def confirm_deletion(self, path):
        user_input = (
            input(
                Fore.YELLOW
                + f"Estás a punto de borrar el directorio '{path}' y todo su contenido. ¿Quieres continuar? (y/n): "
                + Style.RESET_ALL
            )
            .strip()
            .lower()
        )
        return user_input == "y"
