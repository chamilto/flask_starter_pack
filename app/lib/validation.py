from functools import wraps

from flask import current_app as app, jsonify, request
from jsonschema import ValidationError


def validate_schema(schema):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                schema.validate(request.json)
            except ValidationError, ex:
                app.logger.info('{0}'.format(ex.message))
                return jsonify({"error": ex.message}), 400
            return f(*args, **kwargs)
        return wrapper
    return decorator
