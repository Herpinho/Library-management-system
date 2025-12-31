from flask import Flask
from controller import user_blueprint

app = Flask(__name__)
app.register_blueprint(user_blueprint, url_prefix="/users")

if __name__ == "__main__":
    app.run(debug=True,host= "0.0.0.0", port=5001)