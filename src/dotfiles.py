import os
import platform
import shutil
import tempfile
from itertools import groupby
from typing import Generator, NoReturn
from .paths import Network, NetworkPaths, Paths
from .utils import ind, print_fail, print_neutral, print_success_generic

# Nix daemon failsafe for MacOS users
daemon_path = "'/nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh'"
daemon_snippet_lines = [
    "# Nix\n",
    f"[ -e {daemon_path} ] && . {daemon_path}" + "\n",
    "# End Nix\n"]


def remove_excess_newlines(lines: list[str]) -> Generator[str, None, None]:
    """
    Prevents accumulation of newlines in dotfiles by removing consecutive newlines in excess of 2.
    """
    for _, group in groupby(lines, key=lambda line: line.strip() == ""):
        lines_in_group = list(group)
        if not lines_in_group[0].strip():
            yield "\n" if len(lines_in_group) <= 2 else ""
        else:
            yield "\n".join(line.strip() for line in lines_in_group) + "\n"


def overwrite_dotfile_safely(
        dotfile_path: str, new_content: list[str]) -> None | NoReturn:
    """
    Creates a temporary backup of a given dotfile before overwriting its contents.
    Restores the backup if an exception occurs.
    """

    temp_dir = tempfile.mkdtemp()
    filename = os.path.basename(dotfile_path)
    backup_path = os.path.join(temp_dir, f"{filename}.bak")

    try:
        shutil.copy2(dotfile_path, backup_path)
        with open(dotfile_path, 'w') as dotfile:
            dotfile.writelines(remove_excess_newlines(new_content))
        print_success_generic()

    except:
        print_fail(
            f'\n{ind(f"An error occurred updating {dotfile_path}: restoring original file.")}\n')
        shutil.copy2(backup_path, dotfile_path)

    finally:
        shutil.rmtree(temp_dir)
        # sys.exit(1) # exit here?


def update_dotfiles(paths: Paths) -> None | NoReturn:
    """
    Updates the contents of all target dotfiles to include cardano-node socket path and aliases.
    Removes previous socket path and aliases if present.
    For Mac users, adds Nix daemon failsafe code to dotfiles to prevent Nix breakage from MacOS updates.
    """
    is_darwin = platform.system() == 'Darwin'
    dotfiles = ['.bash_profile', '.bashrc', '.zprofile',
                '.zshrc'] if is_darwin else ['.bashrc']

    def make_alias(net: Network) -> tuple[str, str]:
        node_alias = f"{'main' if net.value == 'mainnet' else net.value}-node"
        network_paths: NetworkPaths = getattr(paths, net.value)
        config_path = network_paths.config
        db_path = network_paths.db
        topology = f"--topology {config_path}/topology.json"
        database = f"--database-path {db_path}"
        socket = f"--socket-path $CARDANO_NODE_SOCKET_PATH"
        port = "--port 1337"
        config = f"--config {config_path}/config.json"

        return (f"alias {node_alias}=", f"'cardano-node run {topology} {database} {socket} {port} {config}'\n")

    alias_chunks = [make_alias(net) for net in Network]
    aliases = [f"{alias}{value}" for alias, value in alias_chunks]

    def is_alias_or_socket_path(line: str) -> bool:
        is_alias = any(line.startswith(prefix) for prefix, _ in alias_chunks)
        is_socket_path = line.startswith("export CARDANO_NODE_SOCKET_PATH")

        return is_alias or is_socket_path

    for dotfile in dotfiles:
        file_path = os.path.expanduser(f"~/{dotfile}")
        if not os.path.exists(file_path):
            print_neutral(ind(f"Creating '{file_path}' file..."))
            open(file_path, 'a').close()

        print_neutral(ind(
            f"Adding {'Nix daemon failsafe, ' if is_darwin else ''}socket variable and aliases to '{file_path}'"))

        with open(file_path, 'r') as f:
            lines = f.readlines()
            new_socket = f"export CARDANO_NODE_SOCKET_PATH='{paths.socket}'\n"
            common_content = [new_socket, *aliases]

            linux_content = [
                line for line in lines
                if not is_alias_or_socket_path(line)
            ] + common_content
            # Add Nix daemon failsafe to user dotfiles on darwin
            # (Prevents breakage of Nix from MacOS system updates)
            darwin_content = [*daemon_snippet_lines, "\n"] + [
                line for line in lines
                if
                not is_alias_or_socket_path(line) and
                not line.strip() + "\n" in daemon_snippet_lines] + common_content

        overwrite_dotfile_safely(
            file_path, darwin_content if is_darwin else linux_content)
