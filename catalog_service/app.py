from flask import Flask
from controller import book_blueprint

app = Flask(__name__)
app.register_blueprint(book_blueprint, url_prefix="/books")

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5002)