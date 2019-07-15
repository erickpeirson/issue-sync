
from flask import Flask, jsonify, Response
from werkzeug.exceptions import BadRequest, InternalServerError, NotFound, \
    MethodNotAllowed, Forbidden, HTTPException

from arxiv import vault
from arxiv.base.middleware import wrap
from .routes import api
from .services import database, jira
from .serialize import EnumJSONEncoder


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_pyfile('config.py')
    app.json_encoder = EnumJSONEncoder
    database.init_app(app)
    jira.init_app(app)
    app.register_blueprint(api)
    app.logger.setLevel(app.config['LOGLEVEL'])
    register_error_handlers(app)

    if app.config['VAULT_ENABLED']:
        wrap(app, [vault.middleware.VaultMiddleware])
        app.middlewares['VaultMiddleware'].update_secrets({})

    return app


def register_error_handlers(app: Flask) -> None:
    """Register error handlers for the Flask app."""
    app.errorhandler(BadRequest)(jsonify_exception)
    app.errorhandler(InternalServerError)(jsonify_exception)
    app.errorhandler(NotFound)(jsonify_exception)
    app.errorhandler(MethodNotAllowed)(jsonify_exception)
    app.errorhandler(Forbidden)(jsonify_exception)


def jsonify_exception(error: HTTPException) -> Response:
    """Render exceptions as JSON."""
    exc_resp = error.get_response()
    response: Response = jsonify(reason=error.description)
    response.status_code = exc_resp.status_code
    return response
