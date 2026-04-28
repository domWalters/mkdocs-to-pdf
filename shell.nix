{ pkgs ? import <nixpkgs> {} }:
pkgs.mkShell {
    buildInputs = with pkgs.buildPackages; [
        fontconfig
        gcc
        glib
        gobject-introspection
        pango

        gnumake
        noto-fonts-cjk-sans
        pkg-config
        python310
        python310Packages.uv
        python310Packages.uv-build
    ];
    shellHook = ''
        if [ -f .venv/bin/activate ]; then
            source $HOME/.bashrc;
        fi;
        if [ ! -f .venv/bin/activate ]; then
            make sync;
        fi;
        source .venv/bin/activate;
        export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:${pkgs.fontconfig.lib}/lib;
        export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:${pkgs.gcc.cc.lib}/lib;
        export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:${pkgs.glib.out}/lib;
        export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:${pkgs.pango.out}/lib;
    '';
}
