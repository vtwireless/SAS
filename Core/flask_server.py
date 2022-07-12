from flask import Flask
from flask_cors import CORS
from flask_routes import app_routes


app = Flask(__name__)
CORS(app)
app.register_blueprint(app_routes)


# @app.before_request
# def log_request_info():
#     # app.logger.debug('Headers: %s', request.headers)
#     app.logger.debug('Body: %s', request.get_data())


if __name__ == '__main__':
    app.run(
        host='localhost',
        port=8000,
        debug=True,
        use_reloader=True
    )


