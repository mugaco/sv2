import json
import os
import subprocess
import inquirer
import re
from colorama import Fore, Style
from rich.console import Console
from rich.panel import Panel

# Verifica que el archivo de configuración exista
def ensure_config_exists(config_path):
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    if not os.path.exists(config_path):
        with open(config_path, "w") as file:
            json.dump({}, file)


# Carga el archivo JSON con alias de ramas
def load_branch_aliases(config_path):
    with open(config_path, "r") as file:
        return json.load(file)


# Carga el archivo JSON de whos
def load_whos(whos_path):
    with open(whos_path, "r") as file:
        return json.load(file)
# Carga el archivo JSON de repos
def load_repos(repos):
    with open(repos, "r") as file:
        return json.load(file)

# Devuelve el nombre de la rama basado en el alias
def get_branch_name_from_aliases(alias, aliases):
    return aliases.get(alias, None)


def add_alias(alias, branch_name, config_path):
    # Cargar el archivo de alias existente
    repo_nme = get_repo_name()
    aliases = load_branch_aliases(config_path)

    # Añadir el nuevo alias y el nombre de la rama al diccionario
    aliases[repo_nme][alias] = branch_name

    # Guardar el diccionario actualizado en el archivo JSON
    with open(config_path, "w") as file:
        json.dump(aliases, file, indent=4)

    # print(f"Alias '{alias}' añadido con éxtio para la rama '{branch_name}'.")


def remove_alias(alias, config_path):
    # Cargar los alias existentes
    repo_nme = get_repo_name()

    aliases_todos = load_branch_aliases(config_path)
    aliases = aliases_todos.get(repo_nme)
    # Verificar si el alias existe en el diccionario
    if alias in aliases:
        # Eliminar el alias del diccionario
        del aliases[alias]
        aliases_todos[repo_nme] = aliases
        # Guardar el diccionario actualizado en el archivo JSON
        with open(config_path, "w") as file:
            json.dump(aliases_todos, file, indent=4)

    else:
        # Informar al usuario si el alias no existe
        print(f"El alias '{alias}' no existe y no puede ser eliminado.")


def is_not_alias(alias, aliases):
    valor = aliases.get(alias)
    if valor is not None:
        return False
    return True


# Devuelve el alias basado en el nombre de la rama
def get_alias_from_branch_name(branch_name, aliases):
    for alias, name in aliases.items():
        if name == branch_name:
            return alias
    return None


# Verifica si una rama tiene ramas hijas
def has_children(branch_url, branches_url, ancestor):
    try:
        branch_name = branch_url.split("/")[-1]
        list_command = f"svn list {branches_url}"
        output = subprocess.check_output(list_command, shell=True, text=True)
        branch_prefix = f"{branch_name}{ancestor}"
        return any(
            branch.startswith(branch_prefix) for branch in output.strip().split("\n")
        )
    except subprocess.CalledProcessError:
        print(Fore.RED + "Error al listar las ramas del repositorio." + Style.RESET_ALL)
        return False


# Obtiene la lista de ramas hijas de una rama específica
def get_children_branches(branch_name, aliases, branches_url, ancestor):
    branch_tree = []
    parent_prefix = f"{branch_name}{ancestor}"
    for alias, full_branch_name in aliases.items():
        if full_branch_name.startswith(parent_prefix):
            child_name = full_branch_name[len(parent_prefix) :].split(ancestor)[0]
            if child_name and all(
                child["alias"] != child_name for child in branch_tree
            ):
                branch_tree.append(
                    {
                        "alias": alias,
                        "branch": full_branch_name,
                        "hijos": get_children_branches(
                            full_branch_name, aliases, branches_url, ancestor
                        ),
                    }
                )
    return branch_tree


def get_parent_branch(branch_name, main_name, ancestor, aliases):
    # print(branch_name)
    # print(aliases)
    # Implementación simplificada de obtener la rama padre desde la URL
    parts = branch_name.split(ancestor)
    # print(parts)
    if len(parts) > 1:
        return f"{parts[-2]} ({get_alias_from_branch_name(parts[-2],aliases)})"
    if parts[0] == main_name:
        return None
    return f"{main_name} (main)"


# Imprime la jerarquía de las ramas de forma recursiva
def print_branch_hierarchy(branch_data, depth=0):
    if not branch_data:
        return
    indent = "    " * depth
    for branch in branch_data:
        alias = branch["alias"]
        full_branch = branch["branch"]
        children = branch["hijos"]
        print(Fore.CYAN + f"{indent}├── {alias} ({full_branch})" + Style.RESET_ALL)
        print_branch_hierarchy(children, depth + 1)


# Colorea la salida del comando diff
def color_diff_output(output):
    for line in output.split("\n"):
        if line.startswith("-"):
            print(Fore.RED + line + Style.RESET_ALL)
        elif line.startswith("+"):
            print(Fore.GREEN + line + Style.RESET_ALL)
        else:
            print(line)


# Evalúa si hay cambios en la salida de comandos SVN
def hay_cambios(output):
    for line in output.splitlines():
        stripped_line = line.strip()
        if not stripped_line:
            continue
        if stripped_line[0] not in "UADGRC":
            continue
        if "mergeinfo" in line or "Updating '.'" in line or "At revision" in line:
            continue
        if stripped_line[0] in "UADGR" and not stripped_line.endswith("."):
            return True
    return False


def invert_branch_format(branch_info):
    """
    Invierte el formato de la cadena de la rama de 'trunk2 (main)' a 'main (trunk2)'.
    """
    if not branch_info:
        return ""

    # Dividir la cadena basada en el espacio antes del '('
    parts = branch_info.split(" (")
    if len(parts) < 2:
        return branch_info  # Devuelve la entrada si no está en el formato esperado

    branch_name = parts[0]
    alias = parts[1][:-1]  # Eliminar el ')' final

    # Reformatear y devolver en el nuevo orden
    return f"{alias} ({branch_name})"


def info_get_lines():
    svn_command = "svn info"
    output = subprocess.check_output(svn_command, shell=True, text=True)
    return output.strip().split("\n")

def get_repo_name():
    svn_command = "svn info"
    try:
        output = subprocess.check_output(svn_command, shell=True, text=True, stderr=subprocess.STDOUT)

    except subprocess.CalledProcessError as e:
        # Manejar el caso en que el comando SVN falla
        # print(f"Error al ejecutar el comando SVN: {e.output}")
        return None
    info_lines = output.strip().split("\n")
    url_line = next(line for line in info_lines if line.startswith("URL:"))
    path_segments = url_line.split("/")
    if len(path_segments) >= 5:  # Verificar que hay suficientes segmentos
        return path_segments[4]
    else:
        return None


def get_parent(ancestor, main_name):
    info_lines = info_get_lines()
    url_line = next(line for line in info_lines if line.startswith("URL:"))
    # print(url_line)
    branch_url = url_line.split("URL: ")[1].strip()
    # print(branch_url)
    branch_name = branch_url.split("/")[-1]
    partes = branch_name.split(ancestor)
    # print(partes)
    if partes[0] == main_name:
        return None
    if len(partes) == 1:
        return main_name
    return partes[-2]  # penultimo elemento de la lista


def get_branch_name():
    info_lines = info_get_lines()
    url_line = next(line for line in info_lines if line.startswith("URL:"))
    # print(url_line)
    branch_url = url_line.split("URL: ")[1].strip()
    # print(branch_url)
    branch_name = branch_url.split("/")[-1]
    return branch_name

# def dialog(question):
#     print(
#         Fore.YELLOW
#             + question
#             + Style.RESET_ALL
#         )
#     message = input().strip()
#     return message
def is_email(answers, current):
    import re
    if not re.match(r"[^@]+@[^@]+\.[^@]+", current):
        raise inquirer.errors.ValidationError('', reason='Por favor, introduce un email válido.')
    return True

def is_not_empty(answers, current):
    if not current:
        raise inquirer.errors.ValidationError('', reason='Este campo es obligatorio.')
    return True

def dialog(questions, rules=None):
    if isinstance(questions, str):
        questions = {"ques":questions}
        rules = {"ques":"required"}

    questions_list = []
    for key, message in questions.items():
        if rules and key in rules:
            rule = rules[key]
            if 'email' in rule:
                questions_list.append(inquirer.Text(key, message=message, validate=is_email))
            elif 'required' in rule:
                questions_list.append(inquirer.Text(key, message=message, validate=is_not_empty))
            else:
                questions_list.append(inquirer.Text(key, message=message))
        else:
            questions_list.append(inquirer.Text(key, message=message))
        
    answers = inquirer.prompt(questions_list)
    return answers
def cconfirm(message):
    question = [
        inquirer.List(
            'confirmation',
            message=f"{message} [Sí/no]",
            choices=['Sí', 'no'],
            default='Sí'
        )
    ]
    answer = inquirer.prompt(question)
    return answer['confirmation'] == 'Sí'    
# def dialog(questions):
#     if isinstance(questions, str):
#         questions_list = [
#             inquirer.Text('v', message=questions),
#         ]
#         answers = inquirer.prompt(questions_list)
#         return answers['v']
    
#     elif isinstance(questions, dict):
#         questions_list = [
#             inquirer.Text(key, message=value) for key, value in questions.items()
#         ]
#         answers = inquirer.prompt(questions_list)
#         return answers
    
#     else:
#         raise ValueError("El argumento debe ser una cadena o un diccionario")

def dialog_list(message, choices):
    questions = [
        inquirer.List(
            'opcion',
            message=message,
            choices=choices,
        ),
    ]

    respuestas = inquirer.prompt(questions)
    
    if respuestas and 'opcion' in respuestas:
        return re.sub(r'\s*\(.*?\)\s*', '', respuestas['opcion'])
    else:
        return None

def check_user(whos,whos_path):
    who = subprocess.check_output("whoami", shell=True, text=True).strip("-\n ")
    
    if who not in whos:
        mprint("Aún no registrado en sv2","i")
        datos = dialog({
            "name":"Tu nombre",
            "email":"Tue email en quartup"
        },{
            
            "name":"required",
            "email":"required|email"
        })
        whos[who] = datos
        # Guardar los cambios en el archivo JSON
        with open(whos_path, 'w') as file:
            json.dump(whos, file, indent=4)
   



def mprint(message,value,m=False):
    valid_values = ['s','i','e']
    if value not in valid_values:
        raise ValueError(f"'{value}' no es un valor válido. Los valores válidos son: {valid_values}")
    if value == 's':
        title = "Success"
        color = "green"
        simbolo = "✔"
    if value == 'e':
        title = "Error"
        color = "red"
        simbolo = "✘"

    if value == 'i':
        title = "Info"
        color = "blue"    
        simbolo = "ℹ"

    console = Console()
    if m: 
        p = Panel(message, title=title, border_style=color, title_align="left")
    else:    
        p = f"[{color}]{simbolo}[/{color}] {message}"
    # console.print(panel)
    console.print(p)
# def success_message(message):
#     console.print(f"[green]✔ {message}[/green]")

# def error_message(message):
#     console.print(f"[red]✘ {message}[/red]")

# def info_message(message):
#     console.print(f"[blue]ℹ {message}[/blue]")
    # def error_panel(message):
    #     panel = Panel(message, title="Error", border_style="red", title_align="left")
    #     console.print(panel)

    # def info_panel(message):
    #     panel = Panel(message, title="Info", border_style="blue", title_align="left")
    #     console.print(panel)

# Ejemplo de uso
# success_panel("Operación completada exitosamente")
# error_panel("Error al completar la operación")
# info_panel("Información importante")
