from flask import Flask
from flask import render_template
from flask import url_for
import requests

app = Flask(__name__)


@app.route('/')
def test_page():
    home = render_template('index.html')
    return home


if __name__ == "__main__":
    app.run()
