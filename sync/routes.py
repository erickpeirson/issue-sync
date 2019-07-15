from flask import Blueprint, Response, request, make_response, current_app
from werkzeug.exceptions import Forbidden

from .controllers import handle_issuesevent, handle_issuecommentevent

api = Blueprint('api', __name__, url_prefix='')


@api.route('/status', methods=['GET'])
def status() -> Response:
    return make_response({})


@api.route('/issuesevent', methods=['POST'])
def issuesevent() -> Response:
    token = request.args.get('token')
    current_app.logger.error('%s:%s', token, current_app.config['WEBHOOK_TOKEN'])
    if token is None or token != current_app.config['WEBHOOK_TOKEN']:
        raise Forbidden('Missing or invalid token')
    return make_response(*handle_issuesevent(request.get_json()))


@api.route('/issuecommentevent', methods=['POST'])
def issuecommentevent() -> Response:
    token = request.args.get('token')
    current_app.logger.error('%s:%s', token, current_app.config['WEBHOOK_TOKEN'])
    if token is None or token != current_app.config['WEBHOOK_TOKEN']:
        raise Forbidden('Missing or invalid token')
    return make_response(*handle_issuecommentevent(request.get_json()))

