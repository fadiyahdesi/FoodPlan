from flask import session
from models.connectDB import User  # Import model User sesuai struktur proyek Anda

class SessionService:
    @staticmethod
    def get_current_user():
        """Mengambil informasi pengguna saat ini dari sesi"""
        user_id = session.get('user_id')
        if not user_id:
            return None
        return User.query.get(user_id)
