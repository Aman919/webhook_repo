from flask import Flask
from flask_cors import CORS
from routes import webhook_blueprint

app = Flask(__name__)
CORS(app)


# Register the webhook route
app.register_blueprint(webhook_blueprint)

if __name__=="__main__":
    app.run(debug=True, port=5000)
