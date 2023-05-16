import os
from typing import NoReturn

from .config_vars import ConfigVars
from .utils import ind, print_neutral, print_success, run_quiet
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
        ["nix", "build", "--accept-flake-config", ".#cardano-node"],
        "Error building cardano-node")

    # Patch broken default.nix in 8.0.0 release
    if cfg["NODE_RELEASE"] == '8.0.0':
        default_nix_path = os.path.join(
            cfg['CARDANO_SRC_PATH'],
            'cardano-node', 'default.nix')
        with open(default_nix_path, 'w') as f:
            f.write(
                '''let defaultCustomConfig = import ./nix/custom-config.nix defaultCustomConfig;
  # This file is used by nix-shell.
  # It just takes the shell attribute from default.nix.
in
{
  # override scripts with custom configuration
  withHoogle ? defaultCustomConfig.withHoogle
, profileData ? null
, profileName ? if profileData != null then profileData.profileName
                else defaultCustomConfig.localCluster.profileName
, workbenchDevMode ? defaultCustomConfig.localCluster.workbenchDevMode
, workbenchStartArgs ? defaultCustomConfig.localCluster.workbenchStartArgs
, customConfig ? {
    inherit withHoogle;
    localCluster = {
      inherit profileName workbenchDevMode workbenchStartArgs;
    };
  }
, system ? builtins.currentSystem
}:
with (import ./nix/flake-compat.nix customConfig);
defaultNix // defaultNix.packages.${system} // {
  private.project = defaultNix.legacyPackages.${system};
}''')

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
        paths: Paths) -> None | NoReturn:
    print_neutral(ind("> Downloading node config files..."))
    networks = ['mainnet', 'preprod', 'preview']
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
