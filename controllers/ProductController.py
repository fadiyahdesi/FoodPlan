# controllers/ProductController.py
from flask import render_template
from models.connectDB import db, Product
import base64

def detect_image_format(image_data):
    """Deteksi format gambar berdasarkan header byte."""
    if image_data.startswith(b'\xff\xd8'):
        return "jpeg"  # Ini berlaku untuk .jpg dan .jpeg
    elif image_data.startswith(b'\x89PNG'):
        return "png"
    elif image_data.startswith(b'RIFF') and image_data[8:12] == b'WEBP':
        return "webp"
    else:
        return "jpeg"  # Default ke jpeg jika format tidak dikenali

def products():
    with db.session.begin():  # Start a new session
          products = db.session.execute(db.select(Product).order_by(Product.id)).scalars().all()

    products_with_images = []
    for product in products:
        
        if product.images:
            # Deteksi format gambar
            image_format = detect_image_format(product.images)
            # Encode gambar ke base64
            image_data = base64.b64encode(product.images).decode('utf-8')
            # Set image_src dengan format yang terdeteksi
            image_src = f"data:image/{image_format};base64,{image_data}"
        else:
            image_src = None  # Jika gambar tidak ada, atur ke None

        products_with_images.append({
            'title': product.title,
            'description': product.description,
            'image_src': image_src
        })

    return render_template('user/index.html', products=products_with_images)