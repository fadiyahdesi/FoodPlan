import hashlib
from flask import Flask, request, jsonify, session # type: ignore
from models.connectDB import db, User

def md5_hash(password):
    """Fungsi untuk membuat hash MD5 dari password."""
    return hashlib.md5(password.encode()).hexdigest()

def loginMobile():
    # Mendapatkan data JSON dari permintaan
    data = request.get_json()
    print("Data diterima:", data)  # Debug log

    if data is None:
        return jsonify({"error": "Request body is not JSON"}), 400

    email = data.get('email')
    password = data.get('password')
    print("Email:", email, "Password:", password)  # Debug log

    # Memeriksa apakah input telah diberikan
    if not email or not password:
        return jsonify({"error": "Email dan password diperlukan"}), 400

    # Mencari pengguna berdasarkan email
    user = User.query.filter_by(email=email).first()
    print("User ditemukan:", user)  # Debug log
    print("Password dari database:", user.password)
    
    # Buat hash MD5 dari password yang diberikan dan bandingkan dengan hash di database
    if user and user.password == md5_hash(password):
        # Jika cocok, simpan informasi pengguna di sesi
        session['user_id'] = user.id
        return jsonify({
            "message": "Login berhasil",
            "user": {
                "id": user.id,
                "nama": user.nama,
                "email": user.email,
                "role": user.role.role,
                # "avatar": user.avatar
            }
        })
    else:
        return jsonify({"error": "Email atau password salah"}), 401
