import subprocess
from colorama import Fore, Style
from . import Command
from helpers import (
    is_not_alias,
    get_alias_from_branch_name,
    add_alias,
    remove_alias,
    has_children,
    info_get_lines,
)


class BranchCommand(Command):
    def __init__(self, app):
        super().__init__(app)
        parser = app.subparsers.add_parser(
            "branch", help="Realiza operaciones con ramas en el repositorio SVN"
        )
        parser_c = app.subparsers.add_parser(
            "br", help="Realiza operaciones con ramas en el repositorio SVN"
        )
        parser.add_argument("verbose_alias", help="Alias de la rama para operar")
        parser_c.add_argument("verbose_alias", help="Alias de la rama para operar")
        parser.add_argument(
            "-d",
            "--delete",
            action="store_true",
            help="Borra una rama del repositorio SVN después de verificar si ha sido fusionada",
        )
        parser.add_argument(
            "-D",
            action="store_true",
            help="Borra una rama del repositorio SVN incondicionalmente",
        )
        parser_c.add_argument(
            "-d",
            "--delete",
            action="store_true",
            help="Borra una rama del repositorio SVN después de verificar si ha sido fusionada",
        )
        parser_c.add_argument(
            "-a",
            "--alias",
            action="store",
            help="Establece un alias",
        )
        parser.add_argument(
            "-a",
            "--alias",
            action="store_true",
            help="Establece un alias",
        )
        parser_c.add_argument(
            "-D",
            action="store_true",
            help="Borra una rama del repositorio SVN incondicionalmente",
        )
        parser.set_defaults(command="branch")
        parser_c.set_defaults(command="br")

    def valid_alias(self, alias):
        if is_not_alias(alias, self.app.aliases):
            print(
                Fore.RED
                + f"El alias '{alias}' no es válido. Use 'sv2 aliases' para ver los alias válidos."
                + Style.RESET_ALL
            )
            return False
        return True

    def allowed(self, alias):
        name = self.app.aliases.get(alias, None)
        if name == self.app.main_name:
            print(Fore.RED + f"No se puede borrar 'main'" + Style.RESET_ALL)
            return False
        if name == self.app.pre_name:
            print(Fore.RED + f"No se puede borrar 'pre'" + Style.RESET_ALL)
            return False
        return True

    def run(self, args):
        if args.delete:
            if self.allowed(args.verbose_alias):
                if self.valid_alias(args.verbose_alias):
                    self.delete_branch(args.verbose_alias, check_merged=True)
        elif args.D:
            if self.allowed(args.verbose_alias):
                if self.valid_alias(args.verbose_alias):
                    self.delete_branch(args.verbose_alias, check_merged=False)
        else:
            self.create_branch(args.verbose_alias, args.alias)

    def create_branch(self, alias, a):
        if "_" in alias:
            print(
                Fore.RED
                + "Error: El uso de guiones bajos (_) en el alias está prohibido. Utilice guiones medios (-) en su lugar."
                + Style.RESET_ALL
            )
            return
        try:
            if self.app.current_branch_name == self.app.main_name:
                print(
                    Fore.RED
                    + f"No se pueden crear ramas de proyecto desde trunk2 (main). Debe hacerse desde 'pre'. Usar 'sv2 to pre' para cambiar de rama"
                    + Style.RESET_ALL
                )
                return
            if self.app.current_branch_name == self.app.pre_name:
                branch_url_copy = f"{self.app.base}/{self.app.current_branch_name}"
            else:
                branch_url_copy = f"{self.app.branches}/{self.app.current_branch_name}"

            branch_name = f"{self.app.current_branch_name}{self.app.ancestor}{alias}"
            branch_url = f"{self.app.branches}/{branch_name}"
            # vamos a comprobar, antes de intentar crear la rama, si exista ya
            exist_command = f"svn info {branch_url}"
            exist = True
            try:
                # Lanzara error si la rama no existe
                subprocess.check_output(
                    exist_command, shell=True, stderr=subprocess.STDOUT
                )
            except subprocess.CalledProcessError as e:
                # así
                exist = False
            if exist:
                print(
                    Fore.RED
                    + f"La rama '{alias}' ya existe en el repositorio."
                    + Style.RESET_ALL
                )
                return
            svn_command = f"svn copy {branch_url_copy} {branch_url} -m 'Creando nueva rama {alias}'"
            subprocess.check_output(svn_command, shell=True)
            add_alias(alias, branch_name, self.app.config_path)
            if a:
                comando = f"svd edal {alias} -a {a}"
                print(comando)
                subprocess.check_output(comando, shell=True)

            print(Fore.GREEN + f"Rama '{alias}' creada con éxtio." + Style.RESET_ALL)
        except subprocess.CalledProcessError as e:
            print(Fore.RED + f"Error al crear la rama '{alias}': {e}" + Style.RESET_ALL)

    def delete_branch(self, alias, check_merged):
        deleting_branch_name = self.app.aliases.get(alias, None)
        deleting_branch_url = f"{self.app.branches}/{deleting_branch_name}"
        parent_name = self.get_parent_name(deleting_branch_name)
        parent_url = f"{self.app.branches}/{parent_name}"

        if check_merged:
            try:
                merge_info_command = f"svn mergeinfo --show-revs eligible {deleting_branch_url} {parent_url}"
                print(merge_info_command)
                result = subprocess.check_output(
                    merge_info_command, shell=True, text=True
                )
                if not result:
                    print(
                        Fore.GREEN
                        + f"Rama '{alias}' ya fusionada completamente. Procediendo a borrar."
                        + Style.RESET_ALL
                    )
                    user_input = (
                        input(
                            Fore.YELLOW
                            + f"¿Borrar la rama '{alias}' (y/n)? "
                            + Style.RESET_ALL
                        )
                        .strip()
                        .lower()
                    )
                    if user_input == "y":
                        self.force_delete_branch(
                            deleting_branch_url, deleting_branch_name, alias
                        )
                    else:
                        print(
                            Fore.RED
                            + f"Eliminación de la rama '{alias}' cancelada."
                            + Style.RESET_ALL
                        )
                else:
                    parent_alias = get_alias_from_branch_name(
                        parent_name, self.app.aliases
                    )
                    print(
                        Fore.YELLOW
                        + f"Rama '{alias}' no ha sido completamente fusionada en '{parent_alias}'. No se ha borrado."
                        + Style.RESET_ALL
                    )
                    print(
                        Fore.BLUE
                        + f"Debería antes hacerse 'sv2 to {parent_alias}' y después 'sv2 merge {alias}'."
                        + Style.RESET_ALL
                    )
            except subprocess.CalledProcessError as e:
                print(
                    Fore.RED
                    + f"Error al verificar si la rama '{alias}' ha sido fusionada: {e}"
                    + Style.RESET_ALL
                )
        else:
            self.force_delete_branch(deleting_branch_url, deleting_branch_name, alias)

    def force_delete_branch(self, branch_url, branch_name, alias):
        if branch_url == self.get_url_full_current():
            print(
                Fore.YELLOW
                + f"La rama '{branch_name}' no se puede borrar desde ella misma."
                + Style.RESET_ALL
            )
            return
        if has_children(branch_url, self.app.branches, self.app.ancestor):
            print(
                Fore.YELLOW
                + f"La rama '{branch_name}' tiene ramas hijas y no será borrada."
                + Style.RESET_ALL
            )
            return

        try:
            delete_command = (
                f"svn delete {branch_url} -m 'Eliminando rama {branch_name}'"
            )
            subprocess.check_output(delete_command, shell=True)
            remove_alias(alias, self.app.config_path)
            print(
                Fore.GREEN
                + f"Rama '{branch_name}' eliminada con éxtio."
                + Style.RESET_ALL
            )
        except subprocess.CalledProcessError as e:
            print(
                Fore.RED
                + f"Error al eliminar la rama '{branch_name}': {e}"
                + Style.RESET_ALL
            )

    def get_parent(self):
        info_lines = info_get_lines()
        url_line = next(line for line in info_lines if line.startswith("URL:"))
        branch_url = url_line.split("URL: ")[1].strip()
        branch_name = branch_url.split("/")[-1]
        return branch_name

    def get_parent_name(self, branch_name):
        if branch_name == self.app.main_name:
            return None
        if branch_name == self.app.pre_name:
            return self.app.main_name
        parts = branch_name.split(self.app.ancestor)
        parts.pop()
        return self.app.ancestor.join(parts)

    def get_url_full_current(self):
        info_lines = info_get_lines()
        url_line = next(line for line in info_lines if line.startswith("URL:"))
        return url_line.split("URL: ")[1].strip()
