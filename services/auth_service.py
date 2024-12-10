import hashlib
import os
import jwt
import datetime
from flask import current_app, url_for
import base64
from models.connectDB import User
from models.connectDB import db # Sesuaikan dengan struktur proyek Anda

class AuthService:
    @staticmethod
    def md5_hash(password):
        """Fungsi untuk membuat hash MD5 dari password."""
        return hashlib.md5(password.encode()).hexdigest()

    @staticmethod
    def generate_token(user):
        """Menghasilkan token JWT."""
        payload = {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "role": user.role.role,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)  # Token berlaku 2 jam
        }
        token = jwt.encode(payload, current_app.secret_key, algorithm="HS256")
        print(f"Payload token: {payload}")
        return token

    @staticmethod
    def decode_token(token):
        """Mendekode dan memvalidasi token JWT."""
        try:
            payload = jwt.decode(token, current_app.secret_key, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            return {"error": "Token telah kedaluwarsa"}
        except jwt.InvalidTokenError:
            return {"error": "Token tidak valid"}

    @staticmethod
    def login(email, password):
        """Logika login berbasis token."""
        user = User.query.filter_by(email=email).first()
        if user and user.password == AuthService.md5_hash(password):
            token = AuthService.generate_token(user)
            print(f"Token Generated: {token}")

            # Konversi avatar (longblob) ke Base64
            avatar_base64 = None
            if user.avatar:
                avatar_base64 = base64.b64encode(user.avatar).decode('utf-8')

            return {
                "status": "success",
                "message": "Login berhasil",
                "token": token,
                "user": {
                    "id": user.id,
                    "nama": user.nama,
                    "email": user.email,
                    "username": user.username,
                    "avatar": avatar_base64,  # Avatar dalam format Base64
                    "role": user.role.role,
                }
            }
        return {
            "status": "error",
            "message": "Email atau password salah"
        }
        

    @staticmethod
    def logout():
        """Logika logout (opsional, misalnya blacklist token)."""
        return {"status": "success", "message": "Logout berhasil"}
    
    @staticmethod
    def register(nama, email, username, password, role_id):
        """
        Fungsi untuk registrasi pengguna baru.
        :param nama: Nama lengkap pengguna
        :param email: Email pengguna
        :param password: Password pengguna
        :param role_id: ID peran (role) pengguna
        :return: Dictionary dengan status dan pesan
        """
        # Cek apakah email sudah terdaftar
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return {
                "status": "error",
                "message": "Email sudah terdaftar"
            }

        # Buat pengguna baru
        hashed_password = AuthService.md5_hash(password)
        new_user = User(nama=nama, email=email, username=username, password=hashed_password, role_id=role_id)
        
        # Tentukan avatar default jika pengguna tidak mengupload avatar
        default_avatar_path = os.path.join(current_app.root_path, 'static', 'assets', 'img', 'default-avatar.png')
        if not new_user.avatar:
            with open(default_avatar_path, "rb") as img_file:
                new_user.avatar = img_file.read()

        try:
            db.session.add(new_user)
            db.session.commit()

            # Generate token setelah registrasi
            token = AuthService.generate_token(new_user)
            if not token:
                return {
                    "status": "error",
                    "message": "Token tidak dapat dibuat"
                }
            print(f"Token: {token}")
            # Konversi avatar (longblob) ke Base64
            avatar_base64 = base64.b64encode(new_user.avatar).decode('utf-8')
            print(f"Avatar: {new_user.avatar}")
            return {
                "status": "success",
                "message": "Registrasi berhasil",
                "token": token,  # Tambahkan token
                "user": {
                    "id": new_user.id,
                    "nama": new_user.nama,
                    "username": new_user.username,
                    "email": new_user.email,
                    "role_id": new_user.role_id,
                    "avatar": avatar_base64  # Avatar dalam format Base64
                }
            }
        except Exception as e:
            db.session.rollback()
            return {
                "status": "error",
                "message": f"Terjadi kesalahan: {str(e)}"
        }
            
    @staticmethod
    def loginWithGoogle(user_info):
        """Login atau registrasi menggunakan Google."""
        # Cari pengguna berdasarkan email
        user = User.query.filter_by(email=user_info['email']).first()

        if not user:
            # Jika pengguna belum terdaftar, buat pengguna baru
            username = user_info['email'].split('@')[0]  # Ambil username dari email
            hashed_password = AuthService.md5_hash(os.urandom(8).hex())  # Password acak

            # Tentukan avatar default jika tidak tersedia dari Google
            avatar = user_info.get('picture')
            if not avatar:
                default_avatar_path = os.path.join(current_app.root_path, 'static', 'assets', 'img', 'default-avatar.png')
                with open(default_avatar_path, "rb") as img_file:
                    avatar = base64.b64encode(img_file.read()).decode('utf-8')  # Avatar default dalam Base64

            # Buat pengguna baru
            user = User(
                email=user_info['email'],
                nama=user_info.get('name', 'Pengguna Google'),
                username=username,
                password=hashed_password,
                avatar=avatar,
                role_id=2  # Role default (pengguna biasa)
            )
            db.session.add(user)
            db.session.commit()

        # Generate token JWT untuk login
        token = AuthService.generate_token(user)

        # Return respons login
        return {
            "status": "success",
            "message": "Login berhasil",
            "token": token,
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "name": user.nama,
                "avatar": user.avatar,  # Avatar dari Google atau default
            }
        }