import os

SESSIONS_FILE = os.getenv("CRYPTAUTH_SESSIONS_FILE", "sessions.db")
AUTHORIZED_ADDRESSES_FILE = os.getenv(
    "CRYPTAUTH_AUTHORIZED_ADDRESSES_FILE", "authorized.txt"
)
HOSTNAME = os.getenv("CRYPTAUTH_HOSTNAME", "localhost")
