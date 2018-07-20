from flask import Flask
from flask import render_template
from flask import url_for
import requests

app = Flask(__name__)


@app.route('/')
def home():
    home = render_template('index.html')
    return home


@app.errorhandler(404)
def page_not_found(error):
    not_found = render_template('404.html'), 404
    return not_found


if __name__ == "__main__":
    app.run()
