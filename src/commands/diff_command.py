# import subprocess
# from colorama import Fore, Style
# from . import Command
# from helpers import get_branch_name_from_aliases

# class DiffCommand(Command):
#     def __init__(self, app):
#         super().__init__(app)
#         parser = app.subparsers.add_parser(
#             "diff", help="Muestra las diferencias entre dos revisiones"
#         )
#         parser.add_argument(
#             "revisar", help="Revisiones en el formato REV1:REV2 o ramas en formato ALIAS-R1:ALIAS-R2", type=str
#         )
#         parser.add_argument(
#             "-f", "--file", help="Especifica un archivo específico para comparar", default=None, type=str
#         )
#         parser.set_defaults(command="diff")

#     def run(self, args):
#         tipo = self.identify_revision_or_branch(args.revisar)
#         if tipo == 'revisions':
#             self.diff_between_revisions(args)
#         else:
#             self.diff_between_branches(args)

#     def diff_between_revisions(self, args):
#         try:
#             rev1, rev2 = map(int, args.revisar.split(":"))
#         except ValueError:
#             print(Fore.RED + "Error: Debes especificar las revisiones en el formato 'REV1:REV2'." + Style.RESET_ALL)
#             return

#         diff_command = f"svn diff -r {rev1}:{rev2}"
#         if args.file:
#             diff_command += f" {args.file}"

#         try:
#             output = subprocess.check_output(diff_command, shell=True, text=True)
#             if output.strip():
#                 self.color_diff_output(output)
#             else:
#                 print(Fore.YELLOW + "No hay cambios detectados entre las revisiones especificadas." + Style.RESET_ALL)
#         except subprocess.CalledProcessError as e:
#             print(Fore.RED + f"Error al ejecutar svn diff: {e}" + Style.RESET_ALL)

#     def diff_between_branches(self, args):
#         try:
#             alias1, alias2 = args.revisar.split(":")
#         except ValueError:
#             print(Fore.RED + "Error: Debes especificar los alias en el formato 'ALIAS1:ALIAS2'." + Style.RESET_ALL)
#             return

#         branch_name1 = get_branch_name_from_aliases(alias1, self.app.aliases)
#         branch_name2 = get_branch_name_from_aliases(alias2, self.app.aliases)

#         if branch_name1 == self.app.main_name:
#             branch_url1 = self.app.main
#         else:
#             branch_url1 = f"{self.app.branches}/{branch_name1}"

#         if branch_name2 == self.app.main_name:
#             branch_url2 = self.app.main
#         else:
#             branch_url2 = f"{self.app.branches}/{branch_name2}"

#         diff_command = f"svn diff {branch_url1} {branch_url2}"
#         try:
#             output = subprocess.check_output(diff_command, shell=True, text=True)
#             print(Fore.GREEN + "Diferencias entre las ramas:" + Style.RESET_ALL)
#             print(output)
#         except subprocess.CalledProcessError as e:
#             print(Fore.RED + f"Error al ejecutar svn diff: {e}" + Style.RESET_ALL)

#     def identify_revision_or_branch(self,arg):
#         """Identifica si el argumento es un rango de revisiones o de ramas."""
#         if all(part.isdigit() for part in arg.split(":")):
#             return "revisions"
#         else:
#             return "branches"

#     def color_diff_output(self, output):
#         for line in output.split("\n"):
#             if line.startswith("-"):
#                 print(Fore.RED + line + Style.RESET_ALL)
#             elif line.startswith("+"):
#                 print(Fore.GREEN + line + Style.RESET_ALL)
#             else:
#                 print(line)
import subprocess
from colorama import Fore, Style
from . import Command
from helpers import get_branch_name_from_aliases


class DiffCommand(Command):
    def __init__(self, app):
        super().__init__(app)
        parser = app.subparsers.add_parser(
            "diff", help="Muestra las diferencias entre dos revisiones"
        )
        parser.add_argument(
            "revisar",
            help="Revisiones en el formato REV1:REV2 o ramas en formato ALIAS-R1:ALIAS-R2",
            type=str,
        )
        parser.add_argument(
            "-f",
            "--file",
            help="Especifica un archivo específico para comparar",
            default=None,
            type=str,
        )
        parser.set_defaults(command="diff")

    def run(self, args):
        tipo = self.identify_revision_or_branch(args.revisar)
        if tipo == "revisions":
            self.diff_between_revisions(args)
        else:
            self.diff_between_branches(args)

    def diff_between_revisions(self, args):
        try:
            rev1, rev2 = map(int, args.revisar.split(":"))
        except ValueError:
            print(
                Fore.RED
                + "Error: Debes especificar las revisiones en el formato 'REV1:REV2'."
                + Style.RESET_ALL
            )
            return

        diff_command = f"svn diff -r {rev1}:{rev2}"
        if args.file:
            diff_command += f" {args.file}"

        try:
            output = subprocess.check_output(diff_command, shell=True, text=True)
            if output.strip():
                print(output)
                # html_output = self.generate_html_diff(output)
                # self.save_html_report(html_output, "diff_report.html")
                # print(Fore.GREEN + "Informe de diferencias generado en 'diff_report.html'." + Style.RESET_ALL)
            else:
                print(
                    Fore.YELLOW
                    + "No hay cambios detectados entre las revisiones especificadas."
                    + Style.RESET_ALL
                )
        except subprocess.CalledProcessError as e:
            print(Fore.RED + f"Error al ejecutar svn diff: {e}" + Style.RESET_ALL)

    def diff_between_branches(self, args):
        try:
            alias1, alias2 = args.revisar.split(":")
        except ValueError:
            print(
                Fore.RED
                + "Error: Debes especificar los alias en el formato 'ALIAS1:ALIAS2'."
                + Style.RESET_ALL
            )
            return

        branch_name1 = get_branch_name_from_aliases(alias1, self.app.aliases)
        branch_name2 = get_branch_name_from_aliases(alias2, self.app.aliases)

        if branch_name1 == self.app.main_name:
            branch_url1 = self.app.main
        else:
            branch_url1 = f"{self.app.branches}/{branch_name1}"

        if branch_name2 == self.app.main_name:
            branch_url2 = self.app.main
        else:
            branch_url2 = f"{self.app.branches}/{branch_name2}"

        diff_command = f"svn diff {branch_url1} {branch_url2}"
        try:
            output = subprocess.check_output(diff_command, shell=True, text=True)
            if output.strip():
                print(output)
                # html_output = self.generate_html_diff(output)
                # self.save_html_report(html_output, self.app.html_file)
                # print(Fore.GREEN + "Informe de diferencias generado en 'diff_report.html'." + Style.RESET_ALL)
            else:
                print(
                    Fore.YELLOW
                    + "No hay cambios detectados entre las ramas especificadas."
                    + Style.RESET_ALL
                )
        except subprocess.CalledProcessError as e:
            print(Fore.RED + f"Error al ejecutar svn diff: {e}" + Style.RESET_ALL)

    def identify_revision_or_branch(self, arg):
        """Identifica si el argumento es un rango de revisiones o de ramas."""
        if all(part.isdigit() for part in arg.split(":")):
            return "revisions"
        else:
            return "branches"
