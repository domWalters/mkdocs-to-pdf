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
            fontconfig
            gcc
            glib
            gobject-introspection
            pango

            gnumake
            pkg-config
            python310
            python310Packages.uv
            python310Packages.uv-build

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
            export FONTCONFIG_FILE="${fontsConf}"
            make sync
            source .venv/bin/activate
        '';
    }
