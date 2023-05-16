import os
import platform
from typing import NoReturn

from .paths import Network, NetworkPaths, Paths
from .utils import ind, print_neutral, print_success


def update_dotfiles(paths: Paths) -> None | NoReturn:
    dotfiles = ['.bash_profile', '.zprofile'] if platform.system() == 'Darwin' else [
        '.bashrc']

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

    def not_alias(line):
        return not any(line.startswith(prefix) for prefix, _ in alias_chunks)

    for dotfile in dotfiles:
        file_path = os.path.expanduser(f"~/{dotfile}")
        if not os.path.exists(file_path):
            print_neutral(ind(f"> Creating '{file_path}' file..."))
            open(file_path, 'a').close()

        print_neutral(
            ind(f"> Adding socket variable and aliases to '{file_path}'"))

        with open(file_path, 'r') as f:
            lines = f.readlines()

            new_socket = f"export CARDANO_NODE_SOCKET_PATH='{paths.socket}'\n"
            dotfile_contents = [
                line for line in lines
                if not_alias(line) and
                not line.startswith("export CARDANO_NODE_SOCKET_PATH")] + [
                new_socket, *aliases]

        with open(file_path, 'w') as f:
            f.writelines(dotfile_contents)

        print_success(ind(f"> {dotfile}: SUCCESS\n"))
