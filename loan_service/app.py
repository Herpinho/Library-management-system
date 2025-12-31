from flask import Flask
from controller import loan_blueprint

app = Flask(__name__)
app.register_blueprint(loan_blueprint, url_prefix="/loans")

if __name__ == '__main__':   
    app.run(debug=True, host="0.0.0.0", port=5003)