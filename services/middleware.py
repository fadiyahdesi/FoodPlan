from functools import wraps
from flask import request, jsonify, current_app
import jwt

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"status": "error", "message": "Token diperlukan"}), 401
        try:
            token = token.split(" ")[1]
            decoded = jwt.decode(token, current_app.secret_key, algorithms=["HS256"])

            users_id = decoded.get('id') # Ambil `users_id` dari token
            if not users_id:
                return jsonify({"status": "error", "message": "users_id tidak ditemukan dalam token"}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({"status": "error", "message": "Token telah kedaluwarsa"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"status": "error", "message": "Token tidak valid"}), 401
        return f(users_id, *args, **kwargs)
    return decorated

