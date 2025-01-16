{ pkgs ? import <nixpkgs> {} }:
let
  cryptauth = import ./default.nix { inherit pkgs; };
in
pkgs.mkShell {
  packages = [
    cryptauth
  ];
}
