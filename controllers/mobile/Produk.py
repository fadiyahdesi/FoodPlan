from flask import jsonify, abort
from models.connectDB import db, Product
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

def prodMobile(): 
    try:
        with db.session.begin():  # Start a new session
            products = db.session.execute(db.select(Product).order_by(Product.id)).scalars().all()

        products_with_images = []
        for product in products:
            print(f"ID: {product.id}, Title: {product.title}, Description: {product.description}")

            # Encode image if available
            if product.images:
                image_format = detect_image_format(product.images)
                image_data = base64.b64encode(product.images).decode('utf-8')
                image_src = f"data:image/{image_format};base64,{image_data}"
            else:
                image_src = None

            products_with_images.append({
                'id': product.id,
                'title': product.title,
                'category_id': product.category_id,
                'ingredients': product.ingredients,
                'steps': product.steps,
                'carbohidrat': product.carbohidrat,
                'protein': product.protein,
                'fat': product.fat,
                'description': product.description,
                'created_at': product.created_at.isoformat() if product.created_at else None,
                'updated_at': product.updated_at.isoformat() if product.updated_at else None,
                'image_src': image_src
            })

        return jsonify(products_with_images)
    except Exception as e:
        print(f"Error: {e}")
        abort(500, description="Internal Server Error")