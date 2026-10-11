{ pkgs ? import <nixpkgs> {} }:
let
    fontsConf = pkgs.makeFontsConf {
        fontDirectories = [
            pkgs.noto-fonts-cjk-sans
        ];
    };
in
    pkgs.mkShell {
        packages = with pkgs; [
            chromium
            fontconfig
            gcc
            glib
            gobject-introspection
            harfbuzz
            libyaml
            pango

            gnumake
            pkg-config
            python311
            python311Packages.uv
            python311Packages.uv-build

            zsh
        ];
        shellHook = ''
            # Nix's Python 3.11 build configuration leaks `_PYTHON_SYSCONFIGDATA_NAME`
            # into the shell, which makes uv-built wheels for other interpreters
            # (e.g. 3.15) use Python 3.11's include paths and produce mismatched
            # wheel tags. Unset it so uv provisions each interpreter correctly.
            unset _PYTHON_SYSCONFIGDATA_NAME

            case "$(basename "$SHELL")" in
                "bash")
                    if [ -f $HOME/.bashrc ]; then
                        source $HOME/.bashrc
                    fi
                    ;;
                "zsh")
                    if [ -f $HOME/.zshrc ]; then
                        source $HOME/.zshrc
                    fi
                    ;;
            esac
            export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:${pkgs.fontconfig.lib}/lib
            export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:${pkgs.gcc.cc.lib}/lib
            export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:${pkgs.glib.out}/lib
            export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:${pkgs.pango.out}/lib
            export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:${pkgs.harfbuzz.out}/lib
            export FONTCONFIG_FILE="${fontsConf}"
            . ./scripts/settings-venv.sh
            . ./scripts/settings-post-venv.sh
        '';
    }
