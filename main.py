#!/usr/bin/env python3

import subprocess
import sys
from typing import NoReturn

from src.nix_conf import check_nix_conf
from src.utils import ind, print_success
from src.config_vars import make_cfg
from src.dotfiles import update_dotfiles
from src.paths import make_paths
from src.install import install_node, download_node_configs, prompt_install_aiken, prompt_install_ogmios

VERSION = 0.3


def install() -> None | NoReturn:
    print(f"\n** Cardano-EZ-Installer v{VERSION} **")
    # Check if Nix is installed
    try:
        subprocess.check_output(["nix", "--version"])
    except OSError:
        print("Error: Nix is not installed on this system.")
        sys.exit(1)
    nix_conf_ready = check_nix_conf()

    cfg = make_cfg()

    if nix_conf_ready:
        install_node(cfg)
    else:
        sys.exit(1)

    paths = make_paths(cfg)
    download_node_configs(paths)
    update_dotfiles(paths)
    prompt_install_aiken(cfg)
    prompt_install_ogmios(cfg)

    print_success(ind(
        f"Installation complete!\n"))

    print("Run `preprod-node`, `preview-node`, or `main-node` in a new terminal window to start the node.")


install()
