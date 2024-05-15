# /usr/local/bin/sv2/src/svnapp.py

import argparse
from dotenv import load_dotenv
import os
import subprocess

# Cargar las variables desde el archivo .env
load_dotenv()
from commands.list_command import ListCommand
from commands.aliases_command import AliasesCommand
from commands.info_command import InfoCommand
from commands.update_command import UpdateCommand
from commands.commit_command import CommitCommand
from commands.branch_command import BranchCommand
from commands.clone_command import CloneCommand
from commands.merge_command import MergeCommand
from commands.to_command import ToCommand
from commands.revert_command import RevertCommand
from commands.log_command import LogCommand
from commands.diff_command import DiffCommand
from commands.status_command import StatusCommand
from commands.add_command import AddCommand
from commands.build_aliases_command import BuildAliasesCommand
from commands.edit_alias_command import EditAliasCommand
from commands.pull_request_command import PullRequestCommand
from commands.remove_command import RemoveCommand
from commands.move_command import MoveCommand
from helpers import ensure_config_exists, load_branch_aliases, load_whos, get_repo_name,dialog_list, mprint


class SV2App:
    def __init__(self):
        config_path = os.getenv("ALIASES_FILE")
        whos_path = os.getenv("WHOS_FILE")
        repos_path = os.getenv("REPOS_FILE")
        self.repos = load_whos(repos_path)
        self.store_sv2_url = os.getenv("STORE_SV2_URL")
        self.store_sv2_buzon = os.getenv("STORE_SV2_BUZON")
        self.env = os.getenv("ENV")
        self.config_path = os.path.expanduser(config_path)
        ensure_config_exists(self.config_path)
        repo_name = get_repo_name()
        get_stuff = True

        if repo_name is None:
            get_stuff = False
            r = []
            for key, value in self.repos.items():
                r.append(f'{key} ({value})')
            repo_name = dialog_list("Elige el repositorio",r)

        all_repo_aliases = load_branch_aliases(self.config_path)
        self.whos = load_whos(whos_path)
        self.aliases = all_repo_aliases.get(repo_name, {})
        self.main_name = "trunk2"
        self.pre_name = "pretrunk2"
        self.base = f"https://dev.quartup.net/svn/{repo_name}/quartup"

        # self.base = "https://dev.quartup.net/svn/qproof/quartup"
        self.main = f"{self.base}/{self.main_name}"
        self.pre = f"{self.base}/{self.pre_name}"
        # self.main = "https://dev.quartup.net/svn/quptmp/quartup/trunk2"
        self.branches = f"{self.base}/branches"
        self.ancestor = "__"
        self.prefijo_rama = ""

        self.parser = argparse.ArgumentParser(
            prog="sv2", description="Capa de uso mejorado para SVN"
        )
        self.subparsers = self.parser.add_subparsers(dest="command", required=True)
        if get_stuff:
            self.current_branch_name = self.get_current_branch_name()
            self.current_branch_alias = self.get_current_branch_alias()
            self.current_branch_url = self.get_current_branch_url()
            self.parent_branch_name = self.get_parent_branch_name()
            self.parent_branch_alias = self.get_parent_branch_alias()
            self.parent_branch_url = self.get_parent_branch_url()

        # Inicializar comando
        self.commands = {
            "list": ListCommand(self),
            "aliases": AliasesCommand(self),
            "build-aliases": BuildAliasesCommand(self),
            "edit-alias": EditAliasCommand(self),
            "edal": EditAliasCommand(self),
            "info": InfoCommand(self),
            "i": InfoCommand(self),
            "update": UpdateCommand(self),
            "up": UpdateCommand(self),
            "commit": CommitCommand(self),
            "c": CommitCommand(self),
            "branch": BranchCommand(self),
            "br": BranchCommand(self),
            "clone": CloneCommand(self),
            "merge": MergeCommand(self),
            "to": ToCommand(self),
            "revert": RevertCommand(self),
            "log": LogCommand(self),
            "diff": DiffCommand(self),
            "st": StatusCommand(self),
            "status": StatusCommand(self),
            "add": AddCommand(self),
            "pr": PullRequestCommand(self),
            "pull-request": PullRequestCommand(self),
            "rm": RemoveCommand(self),
            "mv": MoveCommand(self),
            "move": MoveCommand(self),
        }

    def run(self):
        args = self.parser.parse_args()
        # print(self.current_branch_name)
        # print(self.current_branch_alias)
        # print(self.current_branch_url)
        # print(self.parent_branch_name)
        # print(self.parent_branch_alias)
        # print(self.parent_branch_url)
        # return
        command = self.commands.get(args.command)
        if command:
            command.run(args)
        else:
            self.parser.print_help(self.prog_name)

    def get_current_branch_name(self):
        info_lines = self.get_lines_info()
        url_line = next(line for line in info_lines if line.startswith("URL:"))
        # print(url_line)
        branch_url = url_line.split("URL: ")[1].strip()
        # print(branch_url)
        branch_name = branch_url.split("/")[-1]
        return branch_name

    def get_current_branch_alias(self):
        return self.get_branch_alias(self.current_branch_name)

    def get_current_branch_url(self):
        info_lines = self.get_lines_info()
        url_line = next(line for line in info_lines if line.startswith("URL:"))
        # print(url_line)
        branch_url = url_line.split("URL: ")[1].strip()
        return branch_url

    def get_parent_branch_name(self):
        p = self.current_branch_name.split(self.ancestor)
        if len(p) == 1:
            if p[0] == self.main_name:
                return None
            else:
                return self.main_name
        else:
            del p[-1]
            return self.ancestor.join(p)

    def get_parent_branch_alias(self):
        return self.get_branch_alias(self.parent_branch_name)

    def get_branch_alias(self, branch_name):
        for alias, name in self.aliases.items():
            if name == branch_name:
                return alias
        return None

    def get_parent_branch_url(self):
        p = self.current_branch_name.split(self.ancestor)
        if len(p) == 1:
            if p[0] == self.main_name:
                return None
            else:
                return self.main
        else:
            del p[-1]
            return f"{self.branches}/{self.ancestor.join(p)}"

    def get_lines_info(self):
        svn_command = "svn info"
        output = subprocess.check_output(svn_command, shell=True, text=True)
        return output.strip().split("\n")
