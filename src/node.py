import os
from typing import NoReturn

from .config_vars import ConfigVars
from .utils import ind, print_neutral, print_success, run, run_quiet
from .paths import Network, NetworkPaths, Paths


def install_node(cfg: ConfigVars) -> None | NoReturn:
    print_neutral(f"\n{ind('> Installing cardano-node...')}")

    os.chdir(cfg['CARDANO_SRC_PATH'])

    if not os.path.exists("cardano-node"):
        run_quiet(
            ["git", "clone", "https://github.com/input-output-hk/cardano-node"],
            "Error cloning cardano-node repository")
        os.chdir("cardano-node")
    else:
        os.chdir("cardano-node")
        run_quiet(
            ["git", "fetch"],
            "Error fetching cardano-node repository")

    run_quiet(
        ["git", "reset", "--hard", cfg['NODE_RELEASE']],
        f"Error resetting git to release {cfg['NODE_RELEASE']}")

    run_quiet(
        ["nix", "profile", "remove", ".*cardano-node*"],
        "Error removing cardano-node from nix profile")
    run(
        ["nix", "profile", "install", "--accept-flake-config",
         "--extra-substituters", "https://cache.zw3rk.com",
         "--extra-trusted-public-keys",
         "loony-tools:pr9m4BkM/5/eSTZlkQyRt57Jz7OMBxNSUiMC4FkcNfk=",
         ".#cardano-node"],
        "Error installing cardano-node")

    print_success(ind("> cardano-node: SUCCESS\n"))

    print_neutral(ind("> Installing cardano-cli..."))

    run_quiet(
        ["nix", "profile", "remove", ".*cardano-cli*"],
        "Error removing cardano-cli from nix profile")
    run(
        ["nix", "profile", "install", "--accept-flake-config",
         "--extra-substituters", "https://cache.zw3rk.com",
         "--extra-trusted-public-keys",
         "loony-tools:pr9m4BkM/5/eSTZlkQyRt57Jz7OMBxNSUiMC4FkcNfk=",
         "--no-warn-dirty", ".#cardano-cli"],
        "Error installing cardano-cli")

    print_success(ind("> cardano-cli: SUCCESS\n"))


def download_node_configs(
        paths: Paths) -> None | NoReturn:
    print_neutral(ind("> Downloading node config files..."))
    config_files = [
        "config",
        "db-sync-config",
        "submit-api-config",
        "topology",
        "alonzo-genesis",
        "byron-genesis",
        "conway-genesis",
        "shelley-genesis",
    ]
    for net in Network:
        network_paths: NetworkPaths = getattr(paths, net.value)
        config_path = network_paths.config
        os.chdir(config_path)
        config_src = f"https://book.world.dev.cardano.org/environments/{net.value}"

        for file in config_files:
            run_quiet(
                ["curl", "-O", "-J", f"{config_src}/{file}.json"],
                f"Error downloading '{file}.json'")

    print_success(ind("> node config files: SUCCESS\n"))
