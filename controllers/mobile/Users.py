import base64
import hashlib
from pydoc import text
from flask import request, jsonify, session
from models.connectDB import Validasi, db, User
from sqlalchemy import text

def detect_image_format(image_data):
    """Detect image format based on header bytes."""
    if image_data.startswith(b'\xff\xd8'):
        return "jpeg"
    elif image_data.startswith(b'\x89PNG'):
        return "png"
    elif image_data.startswith(b'RIFF') and image_data[8:12] == b'WEBP':
        return "webp"
    else:
        return "jpeg"

def userProfile(users_id):
    try:
        with db.session.begin(): 
            user = db.session.query(User).filter_by(id=users_id).one_or_none()
            
            validasi = db.session.query(Validasi).filter_by(users_id=users_id).one_or_none()

            if not user:
                return jsonify({"error": "User not found"}), 404

            # Encode avatar image to base64 if it exists
            avatar = None
            if user.avatar:
                image_format = detect_image_format(user.avatar)
                image_data = base64.b64encode(user.avatar).decode('utf-8')
                avatar = f"data:image/{image_format};base64,{image_data}"
                
            role_name = user.role.role if user.role else None
            category_name = validasi.category.name if validasi.category else None
            
            response = {
                'id': user.id,
                'nama': user.nama,
                'email': user.email,
                'username': user.username,
                'password': user.password,
                'avatar': avatar,
                'role': role_name,
                'usia': validasi.usia,
                'tBadan': validasi.tinggi_badan,
                'bBadan': validasi.berat_badan,
                'jKelamin': validasi.jenis_kelamin,
                'riwayat': validasi.riwayat,
                'tipeDiet': category_name,
            }
            return jsonify(response)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

def gantiavatar(users_id):
    with db.session.begin():
        data = request.get_json()
        print(data)
        base64_avatar = data.get('avatar')
        print(base64_avatar)
        if not base64_avatar:
            return jsonify({"error": "Avatar tidak ditemukan"}), 400
        avatar_binary = base64.b64decode(base64_avatar)
        
        user = db.session.query(User).filter_by(id=users_id).one_or_none()
        if not user:
                return jsonify({"error": "User not found"}), 404
        
        user.avatar = avatar_binary
        db.session.commit()

        return jsonify({"message": "Avatar berhasil diubah"}), 200  
    
FIELD_MAP = {
    "Nama": {"table": "users", "column_name": "nama", "type": str},
    "Email": {"table": "users", "column_name": "email", "type": str},
    "Username": {"table": "users", "column_name": "username", "type": str},
    "Password": {"table": "users", "column_name": "password", "type": str},
    "Usia": {"table": "validasi", "column_name": "usia", "type": int},
    "Tinggi Badan": {"table": "validasi", "column_name": "tinggi_badan", "type": int},
    "Berat Badan": {"table": "validasi", "column_name": "berat_badan", "type": int},
    "Riwayat Kesehatan": {"table": "validasi", "column_name": "riwayat", "type": str},
    "Program Diet": {
        "table": "validasi",
        "column_name": "category_id",
        "type": int,
        "enum_values": [1, 2, 3, 4, 5],  # Nilai valid ENUM
    },
    "Jenis Kelamin": {
        "table": "validasi",
        "column_name": "jenis_kelamin",
        "type": str,
        "enum_values": ["Laki-Laki", "Perempuan"],  # Nilai valid ENUM
    },
}

def update_profileAll(users_id):
    try:
        data = request.json
        user_id = users_id
        field = data.get('field')
        value = data.get('value')

        # Validasi field
        if field not in FIELD_MAP:
            return jsonify({"error": f"Field '{field}' tidak valid"}), 400

        field_info = FIELD_MAP[field]
        expected_type = field_info["type"]
        table_name = field_info["table"]
        column_name = field_info["column_name"]
        
        # Jika field adalah password, hash password terlebih dahulu
        if field == "password":
            # Menggunakan hashlib untuk mengenkripsi password dengan MD5
            value = hashlib.md5(value.encode('utf-8')).hexdigest()

        # Validasi tipe data
        try:
            value = expected_type(value)
        except ValueError:
            return jsonify({"error": f"Field '{field}' harus bertipe {expected_type.__name__}"}), 400

        # Validasi ENUM jika ada
        if "enum_values" in field_info:
            valid_values = field_info["enum_values"]
            if value not in valid_values:
                return jsonify(
                    {"error": f"Nilai '{value}' tidak valid untuk field '{field}'. Pilihan yang valid: {valid_values}"}
                ), 400

        # Logika update tabel
        if table_name == "users":
            query = text(f"UPDATE user SET {column_name} = :value WHERE id = :users_id")
        elif table_name == "validasi":
            query = text(f"UPDATE validasi SET {column_name} = :value WHERE users_id = :users_id")

        # Eksekusi query dengan parameter binding
        print(f"Query: {query} | Values: {value}, {users_id}")
        db.session.execute(query, {'value': value, 'users_id': users_id})

        # Commit ke database
        db.session.commit()

        return jsonify({"message": f"Data {field} berhasil diperbarui"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500