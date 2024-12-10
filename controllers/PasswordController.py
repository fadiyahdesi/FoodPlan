from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import hashlib
import random
import smtplib
from flask import jsonify, request
from models.connectDB import ResetPassword, User, db


otp_expiry_time = 300
otp_storage={}

def send_otp_email(email, otp):
    sender_email = "ilhamhattamanggala123@gmail.com"  # Ganti dengan email pengirim
    sender_password = "lqkv ljza mhbi qpbx"  # Ganti dengan App Password Gmail
    recipient_email = email

    # Konten email
    subject = "Kode OTP Reset Password Anda"
    body = f"""
    Hai,\n\n
    Kami menerima permintaan untuk mereset password Anda. Gunakan kode OTP di bawah untuk mengganti password Anda:\n
    {otp}\n\n
    OTP ini berlaku selama 5 menit.\n
    Jika Anda tidak meminta reset password, abaikan email ini.\n
    Salam,\nTim Anda
    """

    # Mengatur MIME
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = recipient_email
    message['Subject'] = subject
    message.attach(MIMEText(body, 'plain'))

    try:
        # Menghubungkan ke server SMTP Gmail
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()  # Mulai koneksi TLS
            server.login(sender_email, sender_password)  # Login ke Gmail
            server.sendmail(sender_email, recipient_email, message.as_string())  # Kirim email
        print("Email OTP berhasil dikirim!")
    except Exception as e:
        print(f"Gagal mengirim email: {e}")

def forgot_password():
    email = request.json.get('email')
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'message': 'Email tidak ditemukan!'}), 404

    # Generate OTP secara acak
    otp = str(random.randint(100000, 999999))

    # Simpan OTP ke database atau tempat penyimpanan sementara
    otp_entry = ResetPassword(users_id=user.id, token=otp)
    db.session.add(otp_entry)
    db.session.commit()

    # Kirim OTP ke email pengguna
    send_otp_email(email, otp)
    return jsonify({'message': 'OTP reset password telah dikirim!'}), 200

def verify_otp():
    data = request.json
    email = data.get('email')
    otp = data.get('otp')

    # Cari entry OTP yang sesuai dengan email
    reset_entry = ResetPassword.query.filter_by(token=otp).first()
    if not reset_entry:
        return jsonify({'message': 'OTP tidak valid!'}), 400

    # Verifikasi apakah OTP yang dimasukkan sesuai dan masih berlaku
    if reset_entry.token == otp:
        db.session.commit()
        return jsonify({'message': 'OTP valid! Silakan lanjutkan dengan reset password.'}), 200
    else:
        return jsonify({'message': 'OTP tidak valid atau sudah kadaluarsa!'}), 400
    
def reset_password():
    data = request.json
    otp = data.get('otp')
    new_password = data.get('password')

    reset_entry = ResetPassword.query.filter_by(token=otp).first()
    if not reset_entry:
        return jsonify({'message': 'OTP tidak valid!'}), 400

    try:
        # Verifikasi apakah OTP yang dimasukkan sesuai
        user = User.query.filter_by(id=reset_entry.users_id).first()
        if not user:
            return jsonify({'message': 'Pengguna tidak ditemukan!'}), 404

        # Reset password pengguna
        user.password = hashlib.md5(new_password.encode('utf-8')).hexdigest()

        # Hapus OTP setelah digunakan
        db.session.delete(reset_entry)
        db.session.commit()

        return jsonify({'message': 'Password berhasil direset!'}), 200
    except Exception as e:
        return jsonify({'message': 'Terjadi kesalahan saat mereset password!'}), 500
    
def resend_otp():
    try:
        data = request.get_json()
        email = data.get('email')

        if not email:
            return jsonify({'status': 'error', 'message': 'Email tidak boleh kosong'}), 400

        # Generate OTP baru
        otp = random.randint(100000, 999999)
        otp_storage[email] = otp

        # Kirim email ke pengguna
        email_sent = send_otp_email(email, otp)
        if email_sent:
            return jsonify({'status': 'success', 'message': 'Kode OTP berhasil dikirim ulang ke email Anda'}), 200
        else:
            return jsonify({'status': 'error', 'message': 'Gagal mengirim OTP. Coba lagi nanti'}), 500

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'status': 'error', 'message': 'Terjadi kesalahan pada server'}), 500