# shellcheck shell=sh

scripts_bin="$(realpath "scripts/bin")"
case ":${PATH}:" in
    *:"$scripts_bin":*)
        ;;
    *)
        export PATH="$scripts_bin:$PATH"
        ;;
esac
