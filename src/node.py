import os
from typing import NoReturn

from .config_vars import ConfigVars
from .utils import ind, print_neutral, print_success, run_quiet


def install_node(cfg: ConfigVars, is_testnet: bool) -> None | NoReturn:
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
        ["nix", "build", "--accept-flake-config",
         f".#{cfg['TESTNET_NAME'] if is_testnet else 'mainnet'}/node"],
        "Error building cardano-node")

    run_quiet(
        ["nix-env", "-f", ".", "-iA", "cardano-node"],
        "Error adding cardano-node to PATH")

    print_success(ind("> cardano-node: SUCCESS\n"))

    print_neutral(ind("> Installing cardano-cli..."))

    run_quiet(
        ["nix", "build", "--accept-flake-config", ".#cardano-cli"],
        "Error building cardano-cli")

    run_quiet(
        ["nix-env", "-f", ".", "-iA", "cardano-cli"],
        "Error adding cardano-cli to PATH")

    print_success(ind("> cardano-cli: SUCCESS\n"))


def download_node_configs(
        cfg: ConfigVars, configs_path: str, is_testnet: bool) -> None | NoReturn:
    print_neutral(ind("> Downloading node config files..."))
    os.chdir(configs_path)
    config_src = f"https://book.world.dev.cardano.org/environments/{cfg['TESTNET_NAME'] if is_testnet else 'mainnet'}"
    config_files = [
        "config",
        "db-sync-config",
        "submit-api-config",
        "topology",
        "alonzo-genesis",
        "byron-genesis",
        "shelley-genesis",
    ]
    for file in config_files:
        run_quiet(
            ["curl", "-O", "-J", f"{config_src}/{file}.json"],
            f"Error downloading '{file}.json'")
    print_success(ind("> node config files: SUCCESS\n"))
