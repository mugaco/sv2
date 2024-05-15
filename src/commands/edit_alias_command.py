import json
from colorama import Fore, Style
from . import Command
from helpers import get_repo_name, load_branch_aliases, get_branch_name_from_aliases


class EditAliasCommand(Command):
    def __init__(self, app):
        super().__init__(app)
        parser_largo = app.subparsers.add_parser(
            "edit-alias", help="Edita un alias existente para una rama"
        )
        parser_largo.add_argument(
            "alias_actual", help="Nombre del alias actual a editar"
        )

        parser_corto = app.subparsers.add_parser(
            "edal", help="Edita un alias existente para una rama"
        )
        parser_corto.add_argument(
            "alias_actual", help="Nombre del alias actual a editar"
        )
        parser_largo.add_argument(
            "-a",
            "--alias",
            action="store_true",
            help="Establece el alias",
        )
        parser_corto.add_argument(
            "-a",
            "--alias",
            action="store",
            help="Establece el alias",
        )
        parser_corto.set_defaults(command="edal")
        parser_largo.set_defaults(command="edit-alias")

    def run(self, args):
        self.edit_alias(args)

    def edit_alias(self, args):
        aliases = self.app.aliases
        branch_name = get_branch_name_from_aliases(args.alias_actual, aliases)
        if branch_name == self.app.main_name or branch_name == self.app.pre_name:
            print(
                Fore.RED
                + f"El alias '{args.alias_actual}' no es editable."
                + Style.RESET_ALL
            )
            return

        current_alias = args.alias_actual
        repo_name = get_repo_name()
        full_aliases = load_branch_aliases(self.app.config_path)
        if current_alias not in aliases:
            print(
                Fore.RED
                + f"Error: El alias '{current_alias}' no existe."
                + Style.RESET_ALL
            )
            return
        if args.alias:
            new_alias = args.alias
        else:
            new_alias = input("Escribir nuevo alias: ").strip()
        if new_alias in aliases:
            print(
                Fore.RED + f"Error: El alias '{new_alias}' ya existe." + Style.RESET_ALL
            )
            return
        if not new_alias:
            print(
                Fore.RED + "Error: No se proporcionó un nuevo alias." + Style.RESET_ALL
            )
            return

        branch_name = aliases.pop(current_alias)
        aliases[new_alias] = branch_name
        full_aliases[repo_name] = aliases
        with open(self.app.config_path, "w") as file:
            json.dump(full_aliases, file, indent=4)

        print(
            Fore.GREEN
            + f"Alias '{current_alias}' ha sido editado con éxtio a '{new_alias}'."
            + Style.RESET_ALL
        )
