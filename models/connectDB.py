from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Text, DateTime, LargeBinary, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime

# Buat instance dari SQLAlchemy
db = SQLAlchemy()

class Base(DeclarativeBase):
    pass

class Product(db.Model):
    __tablename__ = "product"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey('category.id'), nullable=False)
    ingredients: Mapped[str] = mapped_column(Text)
    steps: Mapped[str] = mapped_column(Text)
    carbohidrat: Mapped[int] = mapped_column(Integer)
    protein: Mapped[int] = mapped_column(Integer)
    fat: Mapped[int] = mapped_column(Integer)
    description: Mapped[str] = mapped_column(Text)
    images: Mapped[LargeBinary] = mapped_column(LargeBinary)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, onupdate=datetime.utcnow)
    
    # Relasi ke tabel Category
    category = relationship('Category', backref='products')

class Category(db.Model):
    __tablename__ = 'category'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, onupdate=datetime.utcnow)

# Tambahkan fungsi untuk mendapatkan produk berdasarkan kategori dan semua produk

def get_all_products():
    products = Product.query.all()
    return [
        {
            "title": product.title,
            "description": product.description,
            "image_src": product.images,  # Ubah ini sesuai kebutuhan Anda
            "category": product.category.name
        }
        for product in products
    ]

def get_products_by_category(category_name):
    products = Product.query.join(Category).filter(Category.name == category_name).all()
    return [
        {
            "title": product.title,
            "description": product.description,
            "image_src": product.images,  # Ubah ini sesuai kebutuhan Anda
            "category": product.category.name
        }
        for product in products
    ]

class Role(db.Model):
    __tablename__ = 'role'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    role: Mapped[str] = mapped_column(String(50), nullable=False)

class User(db.Model):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nama: Mapped[str] = mapped_column(String(100), nullable=False)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(50), nullable=False)
    avatar: Mapped[LargeBinary] = mapped_column(LargeBinary, nullable=True)
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey('role.id'), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    role = relationship('Role', backref='users')
    
