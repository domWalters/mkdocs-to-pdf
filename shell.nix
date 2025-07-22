{ pkgs ? import <nixpkgs> {} }:

(pkgs.buildFHSEnv {
  name = "mkdocs-to-pdf-env";
  targetPkgs = pkgs: (with pkgs; [
    fontconfig
    glib
    gnumake
    harfbuzz
    noto-fonts-cjk-sans
    pango
    python310
    uv
  ]);
  multiPkgs = pkgs: (with pkgs; [
    fontconfig
    glib
    gnumake
    harfbuzz
    noto-fonts-cjk-sans
    pango
    python310
    uv
  ]);
  runScript = "bash --init-file <(cat $HOME/.bashrc; cat .venv/bin/activate) -i";
}).env
