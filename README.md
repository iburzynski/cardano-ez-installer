# **Cardano EZ-Installer**

A quick and easy way to install `cardano-node` and `cardano-cli` using Nix.

## **Installation**

- This installer can only be used with Unix-like operating systems (Linux, MacOS, WSL). Windows is not supported.
- See the `Minimum System Requirements` for the particular release of `cardano-node` you're installing on the **[releases](https://github.com/input-output-hk/cardano-node/releases)** page (the release the installer uses is set with the `NODE_RELEASE` variable in the `.env` file).
- The `nix` package manager is required for installation. Instructions for installing and configuring Nix are provided below.
- This installer configures `cardano-node` and `cardano-cli` to work with the following terminal shells:
  - `bash` (Linux & MacOS)
  - `zsh` (MacOS)

  The installer configures the node and cli to work with MacOS in both login and interactive shells.
  
  If you wish to use a different shell you'll need to manually configure the necessary aliases and `CARDANO_NODE_SOCKET_PATH` export in the associated dotfile.

1. **Install `nix`**

- If you're setting up Nix on your system for the first time, try Determinate Systems' **[Zero-to-Nix](https://zero-to-nix.com)** in lieu of the official installer, as it provides an easier tool for **[installing](https://zero-to-nix.com/start/install)** and **[uninstalling](https://zero-to-nix.com/start/uninstall)** Nix.
- Alternatively, you may follow the instructions for **multi-user installation** for your OS at **[nixos.org](https://nixos.org/download.html)**. This approach will require some additional configuration and it will be harder to uninstall Nix should you need to. It is only recommended if you've previously installed Nix on your system, as it will detect and repair a previous installation as needed.
- When you are finished installing Nix, close the terminal session and open a fresh one.

2. **Configure `nix.conf`**

- Edit `/etc/nix/nix.conf`: this requires root access to edit. Use a terminal-based editor like `nano` (i.e.):

  ```sh
  sudo nano /etc/nix/nix.conf
  ```

- Modify the file following the instructions below:

  ```
  # Sample /etc/nix/nix.conf

  # Step 2a: Add this line to enable Flakes if missing (if you used the Zero-to-Nix installer this should already be added)
  experimental-features = nix-command flakes

  # Step 2b: Add your username to trusted-users (also include 'root' to prevent overriding default setting)
  trusted-users = root your-username
  
  # Step 2c: Add zw3rk binary cache (add to existing substituters/trusted-public-keys if already present)
  substituters = https://cache.zw3rk.com
  trusted-public-keys = loony-tools:pr9m4BkM/5/eSTZlkQyRt57Jz7OMBxNSUiMC4FkcNfk=
  ```

  **Step 2c** is a temporary measure due to some critical binaries like GHC being missing from IOG's official cache. Without these additions to `nix.conf` Nix will attempt to build these dependencies from source, causing the installation to take an extraordinarily long time and potentially fail!

  **🚨 IMPORTANT!** You must restart the `nix-daemon` to apply the changes

  **Linux:**

  ```sh
  sudo systemctl restart nix-daemon
  ```

  **MacOS:**

  ```sh
  sudo launchctl stop org.nixos.nix-daemon
  sudo launchctl start org.nixos.nix-daemon
  ```

3. **Clone and configure**

- Clone this repository on your system.
- Open `cardano-ez-installer/.env` in any text editor and adjust the environment variables according to your preference.

  > By default the installer is configured to save the necessary files to `~/cardano` and `~/cardano-src` directories.

  ```sh
    # .env

    export NODE_RELEASE="8.0.0" # Replace with newer version and re-run the script to update your installation
    export CARDANO_SRC_PATH="$HOME/cardano-src" # Where cardano-node source files will be saved
    export CARDANO_PATH="$HOME/cardano" # Where node database and config files will be saved
  ```

4. **Run `cardano-ez-installer`**

- Open a terminal window and enter the `cardano-ez-installer` directory.
- Run `./install.sh` to start the installation.
- The installation may take a long time, especially with a fresh install, so be patient! The EZ-Installer doesn't display output information while `cardano-node` and `cardano-cli` are building, to make the installation process easier to follow. If the installer is taking a while on a particular step but you don't see any errors, assume that the installation is proceeding successfully.
- If you encounter any errors during the installation process, return to the `README` and follow the instructions to resolve them. Then run `./install.sh` again.

5. **Start your node**

- Once the installation completes, you can start `cardano-node` from a new terminal window using any of the following aliases:
  - `preprod-node` for preprod testnet
  - `preview-node` for preview testnet
  - `main-node` for mainnet

## **Using `cardano-cli`**

To use `cardano-cli`, first start the node using the alias for the network you're working with.

Then open a new terminal window. You'll need to set the `CARDANO_NODE_NETWORK_ID` variable in this terminal session to tell `cardano-cli` which network you're using.

For `preprod` testnet:
```sh
CARDANO_NODE_NETWORK_ID=1
```

For `preview` testnet:
```sh
CARDANO_NODE_NETWORK_ID=2
```

For `mainnet`:
```sh
CARDANO_NODE_NETWORK_ID=mainnet
```

If you intend to primarily use a single network and don't want to set this variable every time you use `cardano-cli`, you can export this variable in the appropriate dotfile (`~/.bashrc` for Linux, `~/.bash_profile`/`~/.zprofile` for MacOS in login shell sessions, `~/.bashrc`/`~/.zshrc` for MacOS in interactive shell sessions), for example:

```sh
# ~./bashrc

# add this to use preprod testnet:
export CARDANO_NODE_NETWORK_ID=1
```

Once the `CARDANO_NODE_NETWORK_ID` variable is set, you'll be able to run any `cardano-cli` command and interact with your running node.

To check the sync progress of your node, use the following command:

```sh
cardano-cli query tip
```

## **Updating `cardano-node` and `cardano-cli`**

Updating `cardano-node` and `cardano-cli` is simple:

- Change the version number for the `NODE_RELEASE` variable in `.env`.
- Run `./install.sh` to update.
