# cryptauth

A lightweight forward-auth service that uses [SIWE (Sign-In with Ethereum)](https://docs.metamask.io/wallet/how-to/sign-data/siwe/) for authentication.

Tested with Metamask.

## Requirements
- Python 3.11+
- [FastAPI](https://fastapi.tiangolo.com/)
- [siwe](https://github.com/spruceid/siwe-py)

## Installation
```bash
pip install hatchling hatch-vcs
hatch build
pip install dist/*.whl
```

## Usage

Development
```shell
hatch shell
uvicorn cryptauth.views:app --reload
```

Production
```shell
uvicorn cryptauth.views:app --host 0.0.0.0 --port 8000
```

## Project Layout
- `src/cryptauth`: Main application code
- `src/cryptauth/templates`: HTML templates
- `src/cryptauth/static`: JS/CSS assets
- `pyproject.toml`: Build configuration

## License
[GNU AGPLv3](LICENSE)
