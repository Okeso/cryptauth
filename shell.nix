{ pkgs ? import <nixos-unstable> {} }:
let
  abnf = pkgs.python312.pkgs.buildPythonPackage rec {
    pname = "abnf";
    version = "2.3.1";
    pyproject = true;
    src = pkgs.fetchPypi {
      inherit pname version;
      sha256 = "sha256-LT7UkMZMDihe01OE1KWI87HokwYgsJt2YChRCCeE408=";
    };
    propagatedBuildInputs = with pkgs.python312.pkgs; [
      setuptools
      setuptools-scm
    ];
  };

  siwe = pkgs.python312.pkgs.buildPythonPackage rec {
    pname = "siwe";
    version = "4.4.0";
    pyproject = true;
    src = pkgs.fetchPypi {
      inherit pname version;
      sha256 = "sha256-X9+EMlOpHXgIXx2hHtfJaVu7dD4RLaZY5jooXd8//sc=";
    };
    propagatedBuildInputs = with pkgs.python312.pkgs; [
      poetry-core
      abnf
      eth-account
      eth-utils
      eth-typing
      pydantic
      pydantic-core
      typing-extensions
      web3
    ];
  };

  python = pkgs.python312.withPackages (ps: [
    ps.fastapi
    ps.pydantic
    siwe
    ps.eth-keys
    ps.uvicorn
    ps.hatchling
    ps.hatch-vcs
  ]);
in
pkgs.mkShell {
  buildInputs = [
    python
  ];
  shellHook = ''
    echo "Entering Nix shell for cryptauth..."
  '';
}