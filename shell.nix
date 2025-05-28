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
    python39
    uv
  ]);
  multiPkgs = pkgs: (with pkgs; [
    fontconfig
    glib
    gnumake
    harfbuzz
    noto-fonts-cjk-sans
    pango
    python39
    uv
  ]);
  runScript = "bash";
}).env

