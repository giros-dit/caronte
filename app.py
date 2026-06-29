from flask import Flask
from flask_oidc import OpenIDConnect

from dotenv import load_dotenv, dotenv_values

load_dotenv()

app = Flask(__name__)
config = dotenv_values()
app.config.from_mapping(config)

oidc = OpenIDConnect(app, prefix=config['OIDC_PATH_PREFIX'] if 'OIDC_PATH_PREFIX' in config else None)