import subprocess
from colorama import Fore, Style
from tabulate import tabulate
from . import Command
from helpers import info_get_lines


class LogCommand(Command):
    def __init__(self, app):
        super().__init__(app)
        parser = app.subparsers.add_parser(
            "log",
            help="Muestra el historial de revisiones de la rama actual o especificada",
        )
        parser.add_argument(
            "-l",
            "--limit",
            type=int,
            help="Limita el número de entradas de log mostradas",
        )
        parser.add_argument(
            "-r",
            "--revision",
            help="Especifica el rango de revisiones para mostrar, por ejemplo, 5:10",
        )
        parser.add_argument(
            "-d",
            "--date",
            help="Filtra el log para mostrar solo las entradas desde la fecha especificada (formato YYYY-MM-DD)",
        )
        parser.add_argument(
            "-a", "--author", help="Filtra los logs por autor especificado", type=str
        )
        parser.set_defaults(command="log")

    def run(self, args):
        self.log(args)

    def log(self, args):
        log_command = f"svn log {self.get_url_full_current()}"
        if args.date:
            log_command += f" --revision '{{{args.date}}}:HEAD'"
        if args.limit:
            log_command += f" -l {args.limit}"
        if args.revision:
            log_command += f" -r {args.revision}"
        if args.author:
            log_command += f" --search {args.author}"

        try:
            output = subprocess.check_output(log_command, shell=True, text=True)
            if output.strip():
                self.parse_svn_log(output, args.limit)
            else:
                print(
                    Fore.YELLOW + "No hay entradas en el historial." + Style.RESET_ALL
                )
        except subprocess.CalledProcessError as e:
            print(Fore.RED + f"Error al ejecutar svn log: {e}" + Style.RESET_ALL)

    def parse_svn_log(self, output, limit=None):
        entries = []
        logs = output.strip().split(
            "------------------------------------------------------------------------"
        )
        for log_entry in logs:
            lines = log_entry.strip().split("\n")
            if len(lines) < 1 or " | " not in lines[0]:
                continue

            header = lines[0]
            header_parts = header.split(" | ")
            if len(header_parts) < 4:
                continue

            revision, author, date, _ = header_parts
            date = date.split(" (")[0]  # Eliminar la parte de la zona horaria
            message = "\n".join(lines[1:]).strip()
            entries.append([revision, author, date, message])

        # Aplicar límite si está definido
        if limit is not None:
            entries = entries[:limit]

        if entries:
            print(
                tabulate(
                    entries,
                    headers=["Revisión", "Autor", "Fecha", "Mensaje"],
                    tablefmt="grid",
                )
            )
        else:
            print(Fore.YELLOW + "No hay entradas en el historial." + Style.RESET_ALL)

    def get_url_full_current(self):
        info_lines = info_get_lines()
        url_line = next(line for line in info_lines if line.startswith("URL:"))
        return url_line.split("URL: ")[1].strip()
