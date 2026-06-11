import os

TITLE = os.environ.get("TITLE") or "Wake on LAN"
SERVER_NAME = os.environ.get("SERVER_NAME") or "Wake on LAN Server"
SECRET = os.environ.get("SECRET") or os.urandom(32).hex()
MAIL_FROM = os.environ.get("MAIL_FROM") or "<Wake on LAN Server> noreply@localhost"
MAIL_SERVER = os.environ.get("MAIL_SERVER") or "localhost"
MAIL_PORT = os.environ.get("MAIL_PORT") or 25
MAIL_USER = os.environ.get("MAIL_USER")
MAIL_PASS = os.environ.get("MAIL_PASS")
MAIL_USE_TLS = True if MAIL_PORT == "587" else False
MAIL_USE_SSL = True if MAIL_PORT == "465" else False