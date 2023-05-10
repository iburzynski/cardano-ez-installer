# **Cardano EZ-Installer**

A quick and easy way to install `cardano-node` and `cardano-cli` using Nix.

## **Installation**

- This installer can only be used with Unix-like operating systems (Linux, MacOS, WSL). Windows is not supported.
- See the `Minimum System Requirements` for the particular release of `cardano-node` you're installing on the **[releases](https://github.com/input-output-hk/cardano-node/releases)** page (the release the installer uses is set with the `NODE_RELEASE` variable in the `.env` file).
- The instruction process below presumes you have `bash` installed on your system. Run `bash --version` in your terminal to confirm that you have `bash`, and install it first if needed.
- The `nix` package manager is required for installation. Instructions for installing and configuring Nix are provided below.

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
  ```

  **🚨 IMPORTANT!** You must restart the `nix-daemon` to apply the changes

  **Linux:**

  ```sh
  sudo systemctl restart nix-daemon
  ```

  **MacOS:** first find the name of the `nix-daemon` service

  ```sh
  sudo launchctl list | grep nix
  ```

  Then stop and restart the service

  ```sh
  sudo launchctl stop <NAME>
  sudo launchctl start <NAME>
  ```

3. **Clone and configure**

- Clone this repository on your system.
- Open `cardano-ez-installer/.env` in any text editor and adjust the environment variables according to your preference.

  > By default the installer is configured to install `cardano-node` for the `preview` testnet and saves the necessary files to `~/cardano` and `~/cardano-src` directories.

  ```sh
      # .env

      export NETWORK="testnet" # "testnet" | "mainnet"
      export NETWORK_MAGIC=2 # Testnet: 1 (preprod) | 2 (preview)
      export NODE_RELEASE="1.35.7" # Replace with newer version and re-run the script to update your installation
      export CARDANO_SRC_PATH="$HOME/cardano-src" # Where cardano-node source files will be saved
      export CARDANO_PATH="$HOME/cardano" # Where node database and config files will be saved
  ```

4. **Run `cardano-ez-installer`**

- Open a `bash` terminal window and enter the `cardano-ez-installer` directory.
- Run `./install.sh` to start the installation.
- The installation may take a long time, especially with a fresh install, so be patient! The EZ-Installer doesn't display output information while `cardano-node` and `cardano-cli` are building, to make the installation process easier to follow. If the installer is taking a while on a particular step but you don't see any errors, assume that the installation is proceeding successfully.
- If you encounter any errors during the installation process, return to the `README` and follow the instructions to resolve them. Then run `./install.sh` again.

## **Updating `cardano-node` and `cardano-cli`**

Updating `cardano-node` and `cardano-cli` is simple:

- Change the version number for the `NODE_RELEASE` variable in `.env`.
- Run `./install.sh` to update.
