# shellcheck shell=sh

this_dir="$(realpath "$(pwd)")"

if [ "$this_dir" != "$(git rev-parse --show-toplevel)" ]; then
    echo "$0 must be sourced from the directory that it is in"
    return 1
fi

if [ -n "$IN_NIX_SHELL" ]; then
    . ./scripts/settings-venv.sh
elif command -v nix-shell > /dev/null 2>&1; then
    nix-shell --run "$SHELL"
else
    . ./scripts/settings-venv.sh
fi

. ./scripts/settings-post-venv.sh
