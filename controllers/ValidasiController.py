from flask import jsonify, request
from models.connectDB import Validasi, db

def validasi(users_id):
    data = request.get_json()
    
    # Ambil data dari form Flutter
    usia = data.get('usia')
    jenis_kelamin = data.get('jenis_kelamin')
    tinggi_badan = data.get('tinggi_badan')
    berat_badan = data.get('berat_badan')
    riwayat = data.get('riwayat')
    category_id = data.get('category_id')  # Menggunakan category_id yang sudah dikirim
    
    # Cek apakah data dengan users_id sudah ada
    existing_validasi = Validasi.query.filter_by(users_id=users_id).first()
    
    if existing_validasi:
        # Jika data sudah ada, lakukan update
        existing_validasi.usia = usia
        existing_validasi.jenis_kelamin = jenis_kelamin
        existing_validasi.tinggi_badan = tinggi_badan
        existing_validasi.berat_badan = berat_badan
        existing_validasi.riwayat = riwayat
        existing_validasi.category_id = category_id
        
        db.session.commit()
        return jsonify({"status": "success", "message": "Data berhasil diperbarui"}), 200
    else:
        # Jika data belum ada, simpan data baru
        validasi_data = Validasi(
            users_id=users_id,
            usia=usia,
            jenis_kelamin=jenis_kelamin,
            tinggi_badan=tinggi_badan,
            berat_badan=berat_badan,
            riwayat=riwayat,
            category_id=category_id,
        )
        db.session.add(validasi_data)
        db.session.commit()

        return jsonify({"status": "success", "message": "Data berhasil disimpan"}), 200
