"""Web Server Gateway Interface entry-point."""

from sync.factory import create_app
import os


__flask_app__ = create_app()


def application(environ, start_response):
    """WSGI application factory."""
    for key, value in environ.items():
        if key == 'SERVER_NAME':    # This will only confuse Flask.
            continue
        os.environ[key] = str(value)
        __flask_app__.config[key] = value
    return __flask_app__(environ, start_response)
