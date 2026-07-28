from flask import Flask
from flask_oidc import OpenIDConnect

import os

from dotenv import load_dotenv, dotenv_values

app = Flask(__name__)

config = {}

# Set some default configuration values
config['SERVER_NAME'] = os.getenv('SERVER_NAME') or "Wake on LAN Server"
config['SERVER_URL'] = os.getenv('SERVER_URL') or "http://localhost:3000"

config['MAIL_FROM'] = os.getenv('MAIL_FROM') or ""
config['MAIL_SERVER'] = os.getenv('MAIL_SERVER') or ""
config['MAIL_PORT'] = os.getenv('MAIL_PORT') or 25
config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') or False
config['MAIL_USER'] = os.getenv('MAIL_USER') or ""
config['MAIL_PASS'] = os.getenv('MAIL_PASS') or ""

config['SECRET'] = os.getenv('SECRET') or os.urandom(32)
config['SESSION_COOKIE_SECURE'] = os.getenv('SESSION_COOKIE_SECURE') or True
config['SESSION_COOKIE_HTTPONLY'] = os.getenv('SESSION_COOKIE_HTTPONLY') or True

config['SESSION_COOKIE_SAMESITE'] = os.getenv('SESSION_COOKIE_SAMESITE') or "Lax"

config['OIDC_ENABLED'] = os.getenv('OIDC_ENABLED') or False
config['OIDC_SCOPES'] = os.getenv('OIDC_SCOPES') or "openid email profile"
config['OIDC_CLIENT_SECRETS'] = os.getenv('OIDC_CLIENT_SECRETS') or "./data/client_secrets.json"
config['OIDC_PATH_PREFIX'] = os.getenv('OIDC_PATH_PREFIX') or "/oidc"
config['OIDC_OVERWRITE_REDIRECT_URI'] = os.getenv('OIDC_OVERWRITE_REDIRECT_URI') or ''
config['OIDC_ADMIN_GROUPS'] = os.getenv('OIDC_ADMIN_GROUPS') or ''
config['OIDC_SERVICE_GROUPS'] = os.getenv('OIDC_SERVICE_GROUPS') or ''
config['OIDC_RECOVER_PASSWORD_URL'] = os.getenv('OIDC_RECOVER_PASSWORD_URL') or None

config['LOG_LEVEL'] = os.getenv('LOG_LEVEL') or "INFO"


if os.environ.get('ENV') == "development":
    load_dotenv()
    # Load configuration from .env file
    config = dotenv_values()
    
app.config.from_mapping(config)

oidc = None

if app.config['OIDC_ENABLED'] == 'True':
    oidc = OpenIDConnect(app, prefix=app.config['OIDC_PATH_PREFIX'] if 'OIDC_PATH_PREFIX' in app.config else None)