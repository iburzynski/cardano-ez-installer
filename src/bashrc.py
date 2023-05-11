import os
from .utils import ind, print_neutral, print_success
from .paths import Paths


def add_bashrc_alias(node_alias: str, paths: Paths) -> None:
    bashrc = os.path.expanduser("~/.bashrc")

    if not os.path.exists(bashrc):
        print_neutral(ind(f"> Creating {bashrc} file..."))
        open(bashrc, 'a').close()

    print_neutral(
        ind(f"> Adding `{node_alias}` alias and CARDANO_NODE_SOCKET to ~/.bashrc..."))

    with open(bashrc, 'r') as f:
        lines = f.readlines()
        topology = f"--topology {paths['config']}/topology.json"
        database = f"--database-path {paths['db']}"
        socket = f"--socket-path {paths['node.socket']}"
        port = "--port 1337"
        config = f"--config {paths['config']}/config.json"
        new_alias = f"alias {node_alias}='cardano-node run {topology} {database} {socket} {port} {config}'\n"
        new_socket = f"export CARDANO_NODE_SOCKET_PATH='{paths['node.socket']}'\n"
        bashrc_contents = [line for line in lines
                           if not line.startswith(f"alias {node_alias}") and
                           not line.startswith(
                               "export CARDANO_NODE_SOCKET_PATH")] + [new_alias,
                                                                      new_socket]

    with open(bashrc, 'w') as f:
        f.writelines(bashrc_contents)

    print_success(ind("> .bashrc: SUCCESS\n"))
