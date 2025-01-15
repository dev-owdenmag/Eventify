from flask import Flask
from flask_mysqldb import MySQL
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

mysql = MySQL(app)

# Add `enumerate` to the Jinja environment
app.jinja_env.globals.update(enumerate=enumerate)

from app import routes  # Import routes to register them
