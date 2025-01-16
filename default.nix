{ pkgs ? import <nixpkgs> {} }:
let
  ckzg = pkgs.callPackage ./ckzg.nix {
    lib = pkgs.lib;
    fetchFromGitHub = pkgs.fetchFromGitHub;
    clang = pkgs.clang;
    buildPythonPackage = pkgs.python312Packages.buildPythonPackage;
    python = pkgs.python312Packages.python;
    pythonOlder = null;  # or pkgs.python311Packages.python if needed
    pyyaml = pkgs.python312Packages.pyyaml;
    blst = pkgs.blst;
    setuptools = pkgs.python312Packages.setuptools;
  };

  abnf = pkgs.python312Packages.buildPythonPackage rec {
    pname = "abnf";
    version = "2.3.1";
    pyproject = true;
    src = pkgs.fetchPypi {
      inherit pname version;
      sha256 = "sha256-LT7UkMZMDihe01OE1KWI87HokwYgsJt2YChRCCeE408=";
    };
    nativeBuildInputs = [
      pkgs.python312Packages.setuptools-scm
    ];
    pythonImportsCheck = [ "abnf" ];
  };

  ethKeys = pkgs.python312Packages.buildPythonPackage rec {
    pname = "eth-keys";
    version = "0.6.1";
    src = pkgs.fetchPypi {
      inherit version;
      pname = builtins.replaceStrings ["-"] ["_"] pname;
      sha256 = "sha256-pD4mPLyr/WL6dpFo78bCex9WAwQOTeIruE0SVn5P2WI=";
    };
    pythonImportsCheck = [ "eth_keys" ];
    propagatedBuildInputs = [
     ethUtils
    ];
  };

  rlp = pkgs.python312Packages.buildPythonPackage rec {
    pname = "rlp";
    version = "4.0.1";
    src = pkgs.fetchPypi {
      inherit pname version;
      sha256 = "sha256-vO+xEBPfrfiQJkIzeSO9DHhtyKJ8tMIdpuFU5Shp7LE=";
    };
    pythonImportsCheck = [ "rlp" ];
    propagatedBuildInputs = [
      ethUtils
    ];
  };

  ethRlp = pkgs.python312Packages.buildPythonPackage rec {
    pname = "eth-rlp";
    version = "2.1.0";
    src = pkgs.fetchPypi {
      inherit pname version;
      sha256 = "sha256-1bQIqM0g7UlujmbQVZVg0pvCHO5IL4k5NqHwXQ3dxKA=";
    };
    pythonImportsCheck = [ "eth_rlp" ];
    propagatedBuildInputs = [
      rlp
      ethUtils
      pkgs.python312Packages.hexbytes
    ];
  };
  
  ethKeyfile = pkgs.python312Packages.buildPythonPackage rec {
    pname = "eth-keyfile";
    version = "0.8.1";
    src = pkgs.fetchPypi {
      inherit version;
      pname = builtins.replaceStrings ["-"] ["_"] pname;
      sha256 = "sha256-lwi8MfOGtSzKCWkjj/NbGscr16cYbyqEuGEQ08lzvsE=";
    };
    pythonImportsCheck = [ "eth_keyfile" ];
    propagatedBuildInputs = [
      pkgs.python312Packages.pycryptodome
      ethKeys
    ];
  };

  ethHash = pkgs.python312Packages.buildPythonPackage rec {
    pname = "eth-hash";
    version = "0.7.1";
    src = pkgs.fetchPypi {
      inherit version;
      pname = builtins.replaceStrings ["-"] ["_"] pname;
      sha256 = "sha256-0kEaQDoLCmLoJHtBF5MtkA/7TIxksV+SYgVHylzka+U=";
    };
    pythonImportsCheck = [ "eth_hash" ];
    propagatedBuildInputs = [
    ];
  };
  
  ethAbi = pkgs.python312Packages.buildPythonPackage rec {
    pname = "eth-abi";
    version = "5.2.0";
    src = pkgs.fetchPypi {
      inherit version;
      pname = builtins.replaceStrings ["-"] ["_"] pname;
      sha256 = "sha256-F4cD+pjAfY7s1a5Wnn6NFZ5JPrtu61NKj+lz+8TkDvA=";
    };
    pythonImportsCheck = [ "eth_abi" ];
    propagatedBuildInputs = [
      ethTyping
      ethUtils
      pkgs.python312Packages.parsimonious
      pkgs.python312Packages.bitarray
    ];
  };

  ethAccount = pkgs.python312Packages.buildPythonPackage rec {
    pname = "eth-account";
    version = "0.13.4";
    src = pkgs.fetchPypi {
      inherit version;
      pname = builtins.replaceStrings ["-"] ["_"] pname;
      sha256 = "sha256-Lh8t4kC+89nz2AE2VhNdKnm2vm1OeIW86crOQzSko3Y=";
    };
    propagatedBuildInputs = [
      ethKeyfile
      ethRlp
      ethAbi
      ckzg
      pkgs.python312Packages.pydantic
      pkgs.python312Packages.hexbytes
    ];
    pythonImportsCheck = [ "eth_account" ];
  };

  ethTyping = pkgs.python312Packages.buildPythonPackage rec {
    pname = "eth-typing";
    version = "5.1.0";
    src = pkgs.fetchPypi {
      inherit version;
      pname = builtins.replaceStrings ["-"] ["_"] pname;
      sha256 = "sha256-hYHyEu5iUqqihTd6d2IPbl9uFqw/FExh8Jj6/UeWexo=";
    };
    propagatedBuildInputs = [
      pkgs.python312Packages.typing-extensions
    ];
    pythonImportsCheck = [ "eth_typing" ];
  };

  ethUtils = pkgs.python312Packages.buildPythonPackage rec {
    pname = "eth-utils";
    version = "5.1.0";
    src = pkgs.fetchPypi {
      inherit version;
      pname = builtins.replaceStrings ["-"] ["_"] pname;
      sha256 = "sha256-hMYxS5zx/NUmEHRku/SH4/hwl6LnUzYNXtMZ99QuPyA=";
    };
    pythonImportsCheck = [ "eth_utils" ];
    propagatedBuildInputs = [
      ethTyping
      ethHash
      pkgs.python312Packages.toolz
    ];
  };

  web3 = pkgs.python312Packages.buildPythonPackage rec {
    pname = "web3";
    version = "7.7.0";
    src = pkgs.fetchPypi {
      inherit pname version;
      sha256 = "sha256-TQMyuaeLhV5XzOvZ4edMjoVblYaax7j+WHhzFZPnZAg=";
    };
    pythonImportsCheck = [ "web3" ];
    propagatedBuildInputs = [
      ethAccount
      pkgs.python312Packages.idna
      pkgs.python312Packages.aiohttp
      pkgs.python312Packages.requests
      pkgs.python312Packages.websockets
    ];
  };

  siwe = pkgs.python312Packages.buildPythonPackage rec {
    pname = "siwe";
    version = "4.4.0";
    pyproject = true;
    src = pkgs.fetchPypi {
      inherit pname version;
      sha256 = "sha256-X9+EMlOpHXgIXx2hHtfJaVu7dD4RLaZY5jooXd8//sc=";
    };
    propagatedBuildInputs = [
      abnf
      ethAccount
      ethTyping
      ethUtils
      pkgs.python312Packages.pydantic
      pkgs.python312Packages.typing-extensions
      web3
    ];
    nativeBuildInputs = [ pkgs.python312Packages.poetry-core ];
    pythonImportsCheck = [ "siwe" ];
  };

  pythonEnv = pkgs.python312.withPackages (ps: with ps; [
    fastapi
    pydantic
    siwe
    uvicorn
    jinja2
  ]);
in
  pythonEnv

