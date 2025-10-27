from flask import Flask
from controller import *

app = Flask(__name__)
app.register_blueprint(payment_blueprint, url_prefix="/payments")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)