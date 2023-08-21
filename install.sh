#!/usr/bin/env bash

run_python_script() {
  source .env
  if ! python3 main.py; then
    exit 1
  fi
}

cleanup_nix_store() {
  read -p "Clean up nix-store? [Y/n] " answer
  answer=${answer:-Y}

  if [[ $answer =~ ^[Yy]$ ]]; then
    nix-collect-garbage -d
  fi
}

# Check if python3 command is available and Python version is 3.6 or greater
if command -v python3 &> /dev/null &&
   python_version=$(python3 -c "import sys; print(sys.version_info.major * 10 + sys.version_info.minor)") &&
   [[ $python_version -ge 40 ]]; then
  run_python_script
  cleanup_nix_store
  else
    # If not, use nix-shell with Python 3.11
    nix-shell -p python311 --run "$(declare -f run_python_script); run_python_script"

    if [ $? -eq 0 ]; then
      cleanup_nix_store
    fi
fi