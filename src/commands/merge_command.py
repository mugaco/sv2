import subprocess
from colorama import Fore, Style
from . import Command
from helpers import get_branch_name_from_aliases, get_alias_from_branch_name, get_parent,mprint,cconfirm


class MergeCommand(Command):
    def __init__(self, app):
        super().__init__(app)
        parser = app.subparsers.add_parser(
            "merge",
            help="Fusiona los cambios de la rama especificada por alias a la rama actual",
        )
        parser.add_argument("alias", help="Alias de la rama desde la cual fusionar")
        parser.set_defaults(command="merge")

    def run(self, args):
        self.merge(args)

    def merge(self, args):
        parent = get_parent(self.app.ancestor, self.app.main_name)

        if parent is None:
            mprint("Solo el administrador puede fusionar 'pre' a 'main'.","e")
            return
        # print(self.app.pre_name)
        if parent == self.app.main_name:
            mprint(f"Una rama de nivel 'proyecto' no debe fusionarse directamente a 'pre'. En su lugar hacer 'sv2 to rama-proyecto' y desde ahí solicitar un pull request con 'sv2 pr'.","i",True)
            return
        branch_name = get_branch_name_from_aliases(args.alias, self.app.aliases)

        ali = args.alias

        if not branch_name:
            mprint(f"No se encontró una rama correspondiente al alias '{args.alias}'.","e")
            return

        if branch_name == self.app.main_name:
            mprint(f"No se puede fusionar 'main' a otra rama.","i")
            return
        else:
            branch_url = f"{self.app.branches}/{branch_name}"

        try:
            merge_command = f"svn merge {branch_url} --accept postpone"
            subprocess.check_output(merge_command, shell=True)
            mprint(f"Rama '{branch_name} ({args.alias})' fusionada con éxtio en la rama actual.","s")

            # Preguntar al usuario si desea hacer commit de los cambios fusionados
            response = cconfirm(f"¿Desea hacer commit con el comentario 'merge from {branch_name}'?")

            if response:
                commit_message = f"merge from {branch_name}"
                commit_command = f'svn commit -m "{commit_message}"'
                subprocess.check_output(commit_command, shell=True)
                mprint("Commit realizado con éxtio.",'s')
                if self.app.pre_name == branch_name:
                    return
                response = cconfirm(f"¿Desea borrar la rama {branch_name} ({ali})?")
                
                if response:
                    # commit_command = f'svd branch -D {ali}'
                    commit_command = f'svn delete {branch_url} -m "Eliminada rama fusionada branch_name"'
                    # "svn delete {branch_url} -m \"Eliminada rama fusionada branch_name\""
                    # print(commit_command)
                    subprocess.check_output(commit_command, shell=True)
                    mprint("Rama borrada con éxtio.","s")
                else:
                    mprint("La rama no se borró","i")
            else:
                mprint("Commit cancelado por el usuario.","i")

        except subprocess.CalledProcessError as e:
            mprint(f"Error al fusionar la rama: {e}","e")
