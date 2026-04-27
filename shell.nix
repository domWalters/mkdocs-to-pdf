{ pkgs ? import <nixpkgs> {} }:

(pkgs.buildFHSEnv {
    name = "mkdocs-to-pdf-env";
    targetPkgs = pkgs: (with pkgs; [
        fontconfig
        gcc
        glib
        gnumake
        gnumake
        harfbuzz
        noto-fonts-cjk-sans
        pango
        python312
        python312Packages.uv
        python312Packages.uv-build
    ]);
    multiPkgs = pkgs: (with pkgs; [
        fontconfig
        gcc
        glib
        gnumake
        gnumake
        harfbuzz
        noto-fonts-cjk-sans
        pango
        python312
        python312Packages.uv
        python312Packages.uv-build
    ]);
    runScript = ''
        bash --init-file <(
            cat $HOME/.bashrc;
            if [ ! -f .venv/bin/activate ]; then
                make sync;
            fi;
            cat .venv/bin/activate;
        ) -i
    '';
}).env
