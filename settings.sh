# shellcheck shell=sh

if [ "$(pwd)" != "$(git rev-parse --show-toplevel)" ]; then
    echo "$0 must be sourced from the directory that it is in"
    return 1
fi

source_venv() {
    # shellcheck disable=SC1091
    if [ ! -f .venv/bin/activate ]; then
        make sync
    fi
    . .venv/bin/activate
}

if [ -n "$IN_NIX_SHELL" ]; then
    source_venv
elif command -v nix-shell > /dev/null 2>&1; then
    nix-shell
else
    source_venv
fi
