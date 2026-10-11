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
            pango

            gnumake
            pkg-config
            python311
            python311Packages.uv
            python311Packages.uv-build

            zsh
        ];
        shellHook = ''
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
