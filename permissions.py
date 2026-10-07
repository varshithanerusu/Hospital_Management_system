from functools import wraps

from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt


def admin_required():
    def decorator(function):

        @wraps(function)
        @jwt_required()
        def wrapper(*args, **kwargs):

            claims = get_jwt()

            if claims.get("role") != "admin":
                return jsonify({
                    "status": "error",
                    "message": "Admin access required"
                }), 403

            return function(*args, **kwargs)

        return wrapper

    return decorator