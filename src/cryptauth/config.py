import os

SESSIONS_FILE = os.getenv("CRYPTAUTH_SESSIONS_FILE", "sessions.db")
AUTHORIZED_ADDRESSES_FILE = os.getenv(
    "CRYPTAUTH_AUTHORIZED_ADDRESSES_FILE", "authorized.txt"
)
HOSTNAMES = os.getenv("CRYPTAUTH_HOSTNAME", "localhost,auth.test.localhost").split(",")

COOKIES_HOSTNAME = os.getenv("CRYPTAUTH_COOKIES_HOSTNAME", "test.localhost")
COOKIES_SECURE = os.getenv("CRYPTAUTH_COOKIES_SECURE", "false") == "true"
