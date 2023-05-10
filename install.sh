#!/usr/bin/env bash

# Runs Python installer in a temporary Nix shell:
nix-shell -p python311 --run "
  source .env
  if ! python3 main.py; then
    exit 1
  fi
"

if [ $? -eq 0 ]; then
  echo "Cleaning up nix-store..."
  nix-collect-garbage
fi