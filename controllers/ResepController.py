# controllers/ResepController.py
from flask import render_template
from models.connectDB import db, Product, Category
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
        return "jpeg"  # Default to jpeg if the format is not recognized

def resep():
    with db.session.begin():
        # Fetch all products ordered by ID
        reseps = db.session.execute(db.select(Product).order_by(Product.id)).scalars().all()
        
        # Fetch unique categories from Product table
        categories = db.session.query(Product.category).distinct().all()

    # Prepare recipe data with images
    reseps_with_images = []
    for product in reseps:
        image_src = None
        if product.images:
            image_format = detect_image_format(product.images)
            image_data = base64.b64encode(product.images).decode('utf-8')
            image_src = f"data:image/{image_format};base64,{image_data}"

        reseps_with_images.append({
            'title': product.title,
            'description': product.description,
            'image_src': image_src,
            'category': product.category  # Pass category to the template
        })
        
    # Convert categories to a simple list of strings
    categories_list = [category[0] for category in categories]

    return render_template('resep/resep.html', reseps=reseps_with_images, categories=categories_list)