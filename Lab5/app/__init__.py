from flask import Flask

app = Flask(__name__)
app.secret_key = b"brandnewworld"

from app import views