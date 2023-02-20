from flask import Flask
from index_blueprint import index_blueprint

# Create app first
def create_app():
    app = Flask(__name__)
    app.register_blueprint(index_blueprint)

    app.secret_key = "hello"

    return app


if __name__ == "__main__":

    app = create_app()
    app.run(debug=True, host="0.0.0.0")
