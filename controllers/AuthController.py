import hashlib
from flask import request, jsonify
from models.connectDB import User
from models.connectDB import db
from services.auth_service import AuthService
from services.session_service import SessionService
from google.oauth2 import id_token
from google.auth.transport import requests
import requests as req

GOOGLE_CLIENT_ID = "705335153334-mnop4njgqkaf2j6ltbbgf1d1u1todl5p.apps.googleusercontent.com"

def loginMobile():
    data = request.get_json()
    if data is None:
        return jsonify({"error": "Request body is not JSON"}), 400

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email dan password diperlukan"}), 400

    response = AuthService.login(email, password)
    if response['status'] == 'success':
        return jsonify(response), 200
    
    print(response)
    return jsonify(response), 401

def logoutMobile():
    response = AuthService.logout()
    return jsonify(response), 200

def getProfile():
    user = SessionService.get_current_user()
    if user:
        return jsonify({
            "id": user.id,
            "nama": user.nama,
            "email": user.email,
            "role": user.role.role,
        }), 200
    return jsonify({"error": "User not logged in"}), 401

def registerMobile():
    data = request.get_json()
    print(data);
    if not data:
        return jsonify({"error": "Request body is not JSON"}), 400

    email = data.get('email')
    password = data.get('password')
    nama = data.get('nama')
    username = data.get('username')
    print(username)

    # Validasi input
    if not email or not password or not nama or not username:
        return jsonify({"error": "Semua field (nama, email, username, password) diperlukan"}), 400

    # Periksa apakah email atau username sudah terdaftar
    if User.query.filter_by(email=email).first() or User.query.filter_by(username=username).first():
        return jsonify({"error": "Email atau username sudah digunakan"}), 409

    # Hash password sebelum disimpan
    hashed_password = hashlib.md5(password.encode()).hexdigest()

    # Panggil AuthService untuk menangani registrasi dan logika tambahan
    result = AuthService.register(nama, email, username, hashed_password, 2)  # 2 untuk role_id default (pengguna biasa)
    print(result)
    # Cek status dari AuthService
    if result["status"] == "success":
        return jsonify({
            "message": result["message"],
            "token": result["token"],  # Token yang dikirimkan dari AuthService
            "user": result["user"],  # Detail pengguna termasuk avatar dan role_id
        }), 201
    else:
        return jsonify({"error": result["message"]}), 500

def google_login():
    token = request.json.get("token")
    print(token);
    if not token:
        return jsonify({"error": "Token tidak ditemukan"}), 400

    try:
        # Verifikasi token menggunakan Google
        id_info = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID)
        print(id_info)
        # Ambil email dan avatar dari token
        email = id_info["email"]
        avatar_url = id_info["picture"]
        
        # Cek apakah pengguna sudah ada di database
        user = User.query.filter_by(email=email).first()

        if user:
            # Jika pengguna sudah ada, kirimkan data pengguna
            user_info = {
                "user_id": user.id,
                "nama": user.nama,
                "email": user.email,
                "avatar": avatar_url,
                "role_id": user.role_id
            }
            return jsonify({"success": True, "user_info": user_info}), 200
        else:
            # Jika pengguna belum ada, ambil gambar avatar dari URL dan simpan sebagai BLOB
            avatar_response = req.get(avatar_url)
            avatar_binary = avatar_response.content  # Gambar dalam bentuk binary

            new_user = User(
                nama=id_info["name"],
                username=email.split('@')[0],  # Username berdasarkan email
                email=email,
                password='',  # Password kosong karena login menggunakan Google
                avatar=avatar_binary  # Simpan avatar sebagai binary BLOB
            )
            db.session.add(new_user)
            db.session.commit()

            user_info = {
                "user_id": new_user.id,
                "nama": new_user.nama,
                "email": new_user.email,
                "avatar": avatar_url,
                "role_id": new_user.role_id
            }

            return jsonify({"success": True, "user_info": user_info}), 201

    except ValueError:
        return jsonify({"error": "Token tidak valid"}), 400