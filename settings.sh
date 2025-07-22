# shellcheck shell=sh

if [ "$(pwd)" != "$(git rev-parse --show-toplevel)" ]; then
    echo "$0 must be sourced from the directory that it is in"
    return 1
fi

if command -v nix-shell > /dev/null 2>&1; then
    nix-shell
else
    . .venv/bin/activate
fi
