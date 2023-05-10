import os
from typing import TypedDict
from .config_vars import ConfigVars

Paths = TypedDict('Paths', {
    'config': str,
    'db': str,
    'node.socket': str
})


def make_paths(cfg: ConfigVars, is_testnet: bool) -> Paths:
    network_base_path = os.path.join(cfg['CARDANO_PATH'], cfg['NETWORK'])

    if not os.path.exists(network_base_path):
        os.mkdir(network_base_path)

    paths = ['config', 'node.socket', 'db']
    if is_testnet:
        testnet_base_path = os.path.join(network_base_path, cfg['TESTNET_NAME'])
        base_path = testnet_base_path
        if not os.path.exists(testnet_base_path):
            os.mkdir(testnet_base_path)
    else:
        base_path = network_base_path

    path_dict = {path: os.path.join(base_path, path) for path in paths}

    os.chdir(base_path)
    for path in path_dict.values():
        if not os.path.exists(path):
            if path != 'node.socket':
                os.mkdir(path)
            else:
                open(path, 'a').close()

    return {
        'config': path_dict['config'],
        'db': path_dict['db'],
        'node.socket': path_dict['node.socket']}
