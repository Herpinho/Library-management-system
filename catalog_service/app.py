from flask import Flask
from controller import * 

app = Flask(__name__)
app.register_blueprint(catalog_blueprint, url_prefix='/catalog')
if __name__ == '__main__':
    app.run(debug= True, host = '0.0.0.0',
            port= 1000)