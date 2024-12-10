from flask import jsonify, abort
from models.connectDB import Category, User, Validasi, db, Product
import base64

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

def getUserAndProduk(users_id):
    try:
        # Ambil data pengguna
        with db.session.begin():
            user = db.session.query(User).filter_by(id=users_id).one_or_none()

            if not user:
                return jsonify({"error": "User not found"}), 404

            # Encode avatar image to base64 if it exists
            avatar = None
            if user.avatar:
                image_format = detect_image_format(user.avatar)
                image_data = base64.b64encode(user.avatar).decode('utf-8')
                avatar = f"data:image/{image_format};base64,{image_data}"
                
            role_name = user.role.role if user.role else None

            # Ambil category_id dari tabel validasi
            user_validation = db.session.execute(
                db.select(Validasi).filter_by(users_id=users_id)
            ).scalar_one_or_none()

            if not user_validation:
                return jsonify({"error": "User validation missing"}), 404

            category_id = user_validation.category_id
            
            # Ambil kategori
            category = db.session.execute(
                db.select(Category).filter_by(id=category_id)
            ).scalar_one_or_none()

            if not category:
                return jsonify({"error": "Category not found"}), 404

            # Ambil produk sesuai category_id
            matching_products = db.session.execute(
                db.select(Product).filter_by(category_id=category_id).order_by(Product.id)
            ).scalars().all()
            
            # Ambil produk yang tidak sesuai category_id
            other_products = db.session.execute(
                db.select(Product).filter(Product.category_id != category_id).order_by(Product.id)
            ).scalars().all()
        
        # Format produk dengan gambar jika ada
        def format_product(product, category_name=None):
            if product.images:
                image_format = detect_image_format(product.images)
                image_data = base64.b64encode(product.images).decode('utf-8')
                image_src = f"data:image/{image_format};base64,{image_data}"
            else:
                image_src = None

            return {
                'id': product.id,
                'title': product.title,
                'category_id': product.category_id,
                'category_name': category_name or product.category.name,
                'ingredients': product.ingredients,
                'steps': product.steps,
                'carbohidrat': product.carbohidrat,
                'protein': product.protein,
                'fat': product.fat,
                'description': product.description,
                'image_src': image_src,
            }

        # Format produk
        products_with_images = [format_product(product, category.name) for product in matching_products]
        other_products_with_images = [format_product(product) for product in other_products]

        # Gabungkan semua data dalam response
        response = {
            "user": {
                'id': user.id,
                'nama': user.nama,
                'email': user.email,
                'username': user.username,
                'password': user.password,
                'avatar': avatar,
                'role': role_name,
            },
            "products": {
                "matching_products": products_with_images,
                "other_products": other_products_with_images
            }
        }

        return jsonify(response)
    
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500


