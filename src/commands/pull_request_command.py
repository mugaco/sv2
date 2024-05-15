import subprocess
from colorama import Fore, Style
import os

from . import Command
from helpers import get_branch_name_from_aliases, info_get_lines
from utils.notify import Notify

from halo import Halo


class PullRequestCommand(Command):
    def __init__(self, app):
        super().__init__(app)
        parser = app.subparsers.add_parser(
            "pull-request", help="Realiza pull request al administrador del repositorio"
        )
        parser.add_argument(
            "alias", help="Alias de la rama de la que pedimos pull request"
        )

        parser.set_defaults(command="pull-request")
        parser_c = app.subparsers.add_parser(
            "pr", help="Realiza pull request al administrador del repositorio"
        )
        parser_c.add_argument(
            "alias", help="Alias de la rama de la que pedimos pull request"
        )
        parser.set_defaults(command="pr")
        parser_c.set_defaults(command="pull-request")

    def run(self, args):
        self.pull_request(args)

    def pull_request(self, args):
        try:
            spinner = Halo(text="Realizando pull request...", spinner="dots")
            spinner.start()

            request_branch_alias = args.alias
            request_branch_name = get_branch_name_from_aliases(
                request_branch_alias, self.app.aliases
            )
            request_branch_url = f"{self.app.branches}/{request_branch_name}"
            lines = info_get_lines()

            who = subprocess.check_output("whoami", shell=True, text=True).strip("-\n ")
            user = self.app.whos.get("jmmunoz")
            user = self.app.whos[who]
            diff_command = (
                f"svn diff {self.app.current_branch_url} {request_branch_url}"
            )

            output = subprocess.check_output(diff_command, shell=True, text=True)
            if output.strip():
                # html_output = self.generate_html_diff(output)
                html_output = self.generate_html_diff(output)
                self.notify(html_output, user)
            else:
                spinner.warn("No hay cambios detectados entre las ramas especificadas.")
                
            spinner.succeed("Pull request realizado con éxito")
            return

        except subprocess.CalledProcessError as e:
            spinner.fail(f"Error al ejecutar el comando: {e}")

        finally:
            spinner.stop()

    def generate_html_diff(self, output):
        """Convierte la salida de diff en un formato HTML para VuePress."""
        diff_lines = output.splitlines()
        html_lines = []
        # html_lines.append()
        html_lines.append('<pre><code class="diff">')

        for line in diff_lines:
            escaped_line = (
                line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            )

            if line.startswith("Index:") or line.startswith("==="):
                html_lines.append(f'<span class="diff-header">{escaped_line}</span>')
            elif line.startswith("---"):
                html_lines.append(
                    f'<span class="diff-minus-header">{escaped_line}</span>'
                )
            elif line.startswith("+++"):
                html_lines.append(
                    f'<span class="diff-plus-header">{escaped_line}</span>'
                )
            elif line.startswith("-"):
                html_lines.append(f'<span class="diff-minus">{escaped_line}</span>')
            elif line.startswith("+"):
                html_lines.append(f'<span class="diff-plus">{escaped_line}</span>')
            else:
                html_lines.append(escaped_line)

        html_lines.append("</code></pre>")

        return "\n".join(html_lines)

    def notify(self, html_output, user):
        # Inicializa la clase Notify con la URL del endpoint
        api_url = self.app.store_sv2_url


        notifier = Notify(api_url)

        # Crea el objeto JSON para enviar
        notification_data = {
            "attachments": None,
            "description": html_output,
            "email": user["email"],
            "name": user["name"],
            "recipient": self.app.store_sv2_buzon,
            "subdomain": "quartup",
            "subject": "pull request",
            "tenant_id": "6269744aa9da50110432ceb7",
        }
        # Envía la notificación
        notifier.send(notification_data)
