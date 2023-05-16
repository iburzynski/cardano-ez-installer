import os
from enum import Enum
from typing import NoReturn, TypedDict
from .config_vars import ConfigVars


class Network(Enum):
    PREPROD = 'preprod'
    PREVIEW = 'preview'
    MAINNET = 'mainnet'


class Subdir(Enum):
    CONFIG = 'config'
    DB = 'db'


SubdirPaths = TypedDict('SubdirPaths', {
    'config': str,
    'db': str,
})


class NetworkPaths():
    network: str
    path: str
    config: str
    db: str

    def __init__(self, cardano_path: str, network: Network):
        self.network = network.value
        self.path = os.path.join(cardano_path, self.network)
        for subdir in Subdir:
            setattr(self, subdir.value, os.path.join(self.path, subdir.value))


class Paths():
    preprod: NetworkPaths
    preview: NetworkPaths
    mainnet: NetworkPaths
    socket: str

    def __init__(self, cardano_path: str):
        for net in Network:
            setattr(self, net.value, NetworkPaths(cardano_path, net))
        self.socket = os.path.join(cardano_path, 'node.socket')

    def make_paths(self) -> None | NoReturn:
        for net in Network:
            nps: NetworkPaths = getattr(self, net.value)

            if not os.path.exists(nps.path):
                os.mkdir(nps.path)

            os.chdir(nps.path)
            for subdir in Subdir:
                path = getattr(nps, subdir.value)
                if not os.path.exists(path):
                    os.mkdir(path)

        # Create node.socket
        open(self.socket, 'a').close()


def make_paths(cfg: ConfigVars) -> Paths | NoReturn:
    paths: Paths = Paths(cfg['CARDANO_PATH'])
    paths.make_paths()
    return paths
