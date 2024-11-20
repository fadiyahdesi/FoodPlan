from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from controllers.mobile.Produk import prodMobile
from controllers.mobile.DeteksiController import predict
from models.connectDB import db, Product, Role, User  # Import db from models.py, but after db is defined
from langchain_community.document_loaders import PyPDFLoader
from controllers.ProductController import products
from controllers.ChatController import ChatController
from sqlalchemy import func
from sqlalchemy.orm import load_only
from controllers.LoginController import loginMobile
from controllers.AdminController import UserList, create_product, dashboard, delete_product, loginAdmin, produkAdmin, update_product
from controllers.ResepController import resep
from controllers.AdminController import add_user, edit_user, delete_user
import base64  # <-- Tambahkan baris ini untuk mengimpor base64
import logging


app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:@localhost/foodplan"
db.init_app(app)  # Initialize the SQLAlchemy instance with the app

chat_controller = ChatController(app, api_key="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", pdf_path="data/chatbot.pdf")
app.secret_key = 'foodplan_123'
# Konfigurasi logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.get("/")
def product_list():
    return products()

@app.route('/login', methods=['POST'])
def login_page():
    return loginMobile()

# Define route to get chatbot response
@app.route('/get_response', methods=['POST'])
def get_chat_response():
    return chat_controller.get_response()

@app.route('/admin', methods=['GET', 'POST'])
def login():
    return loginAdmin()

@app.route('/admin/dashboard')
def dashboardAdmin():
    return dashboard()

@app.route('/count')
def count():
    # Menggunakan DATE_FORMAT untuk MySQL
    result = (
        db.session.query(
            func.DATE_FORMAT(Product.created_at, '%Y-%m')  # Menggunakan DATE_FORMAT
            .label('month'), 
            Product.category.label('product_category'), 
            func.count(Product.id).label('count')
        )
        .group_by('month', 'product_category')  # Pastikan Anda menggunakan nama label
        .all()
    )
    
    # Mengonversi hasil menjadi list of dicts untuk JSON response
    response = [
        {
            'month': row.month,
            'product_category': row.product_category,
            'count': row.count
        } 
        for row in result
    ]
    
    return jsonify(response)

@app.route('/admin/produk')
def product_admin():
    return produkAdmin()

@app.route('/admin/produk/tambah', methods=['GET', 'POST'])
def tambah_produk():
    return create_product()

@app.route('/admin/produk/edit/<int:id>', methods=['GET', 'POST'])
def edit_produk(id):
    return update_product(id)

@app.route('/admin/produk/hapus/<int:id>', methods=['POST'])
def hapus_produk(id):
    return delete_product(id)

@app.route('/admin/listuser')
def ListUser():
    return UserList()

@app.route('/resep')
def reseps():
    return resep()

@app.route("/produk-page", methods=['GET'])
def produk_page():
    return prodMobile()

# Admin routes
@app.route('/admin/user/tambah', methods=['GET', 'POST'])
def add_user_route():
    return add_user()

@app.route('/admin/user/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_user_route(user_id):
    return edit_user(user_id)

@app.route('/admin/user/hapus/<int:user_id>', methods=['POST'])
def delete_user_route(user_id):
    return delete_user(user_id)

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

@app.route('/categoryproduk')
def categoryproduk():
    # Ambil kategori yang dipilih dari request (default ke 'semua')
    selected_category = request.args.get('category', 'semua')

    # Ambil produk sesuai kategori yang dipilih
    if selected_category == 'dietnormal':
        products = db.session.execute(db.select(Product).filter(Product.category_id == 1)).scalars().all()
    elif selected_category == 'dietBerat':
        products = db.session.execute(db.select(Product).filter(Product.category_id == 2)).scalars().all()
    elif selected_category == 'dietSport':
        products = db.session.execute(db.select(Product).filter(Product.category_id == 3)).scalars().all()
    elif selected_category == 'dietKhusus':
        products = db.session.execute(db.select(Product).filter(Product.category_id == 4)).scalars().all()
    elif selected_category == 'diet2Nyawa':
        products = db.session.execute(db.select(Product).filter(Product.category_id == 5)).scalars().all()
    else:
        products = db.session.execute(db.select(Product)).scalars().all()

    # Tambahkan pemrosesan gambar untuk setiap produk
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

        # Simpan informasi produk dan gambar
        products_with_images.append({
            'title': product.title,
            'description': product.description,
            'image_src': image_src
        })

    # Render template dengan data produk dan gambar
    return render_template('user/index.html', products=products_with_images)

@app.route('/categoryresep')
def categoryresep():
    # Ambil kategori yang dipilih dari request (default ke 'semua')
    selected_category = request.args.get('category', 'semua')

    # Ambil produk sesuai kategori yang dipilih
    if selected_category == 'dietnormal':
        products = db.session.execute(db.select(Product).filter(Product.category_id == 1)).scalars().all()
    elif selected_category == 'dietBerat':
        products = db.session.execute(db.select(Product).filter(Product.category_id == 2)).scalars().all()
    elif selected_category == 'dietSport':
        products = db.session.execute(db.select(Product).filter(Product.category_id == 3)).scalars().all()
    elif selected_category == 'dietKhusus':
        products = db.session.execute(db.select(Product).filter(Product.category_id == 4)).scalars().all()
    elif selected_category == 'diet2Nyawa':
        products = db.session.execute(db.select(Product).filter(Product.category_id == 5)).scalars().all()
    else:
        products = db.session.execute(db.select(Product)).scalars().all()

    # Tambahkan pemrosesan gambar untuk setiap produk
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

        # Simpan informasi produk dan gambar
        products_with_images.append({
            'title': product.title,
            'description': product.description,
            'image_src': image_src
        })

    # Render template dengan data produk dan gambar
    return render_template('resep/resep.html', reseps=products_with_images)

# Detail Resep
@app.route('/resep/<int:id>')
def detail_resep(id):
    # Fetch the resep by ID
    product = db.session.query(Product).filter_by(id=id).first()
    
    if not product:
        return "resep not found", 404

    # Process image if available
    image_src = None
    if product.images:
        image_format = detect_image_format(product.images)
        image_data = base64.b64encode(product.images).decode('utf-8')
        image_src = f"data:image/{image_format};base64,{image_data}"

    # Pass all required details to the template
    detail_reseps = {
        'title': product.title,
        'description': product.description,
        'image_src': image_src,
        'ingredients': product.ingredients,
        'steps': product.steps,
        'carbohydrates': product.carbohydrates,
        'protein': product.protein,
        'fat': product.fat,
        'category_id': product.category_id,
    }

    return render_template('resep/detail_resep.html', resep=detail_reseps)

@app.route('/predict', methods=['POST'])
def predict_endpoint():
    try:
        logger.info(f"Request received: {request.method} {request.url}")
        
        # Cek apakah file ada dalam request
        if 'file' not in request.files:
            logger.error("No file part in the request.")
            return jsonify({'status': 'error', 'message': 'No file part in the request.'}), 400

        file = request.files['file']
        if file.filename == '':
            logger.error("No selected file.")
            return jsonify({'status': 'error', 'message': 'No selected file.'}), 400

        logger.info(f"File received: {file.filename}")
        
        # Panggil fungsi prediksi
        result = predict(file)  # Fungsi predict
        logger.info(f"Prediction result: {result}")

        # Jika ada error di predict
        if result.startswith("Error"):
            return jsonify({'status': 'error', 'message': result}), 400

        # Query produk yang cocok, tanpa kolom created_at dan updated_at
        matched_products = Product.query.options(
            load_only(Product.id, Product.title, Product.ingredients, Product.steps, 
                      Product.carbohidrat, Product.protein, Product.fat, Product.description, 
                      Product.images, Product.category_id)
        ).filter(Product.ingredients.like(f"%{result}%")).all()

        if not matched_products:
            return jsonify({'status': 'success', 'message': 'No products found matching the prediction.'}), 200

        # Format hasil pencarian
        products_data = [
            {
                'id': product.id,
                'title': product.title,
                'category_id': product.category_id,
                'ingredients': product.ingredients,
                'steps': product.steps,
                'carbohidrat': product.carbohidrat,
                'protein': product.protein,
                'fat': product.fat,
                'description': product.description,
                'images': product.images.decode('utf-8') if product.images else None  # Jika ingin mengubah binary ke string
            }
            for product in matched_products
        ]

        # Berikan hasil pencarian ke Flutter
        return jsonify({'status': 'success', 'prediction': result, 'products': products_data}), 200

    except Exception as e:
        logger.error(f"Internal Server Error: {str(e)}")
        return jsonify({'status': 'error', 'message': f'Internal Server Error: {str(e)}'}), 500

if __name__ == "__main__":
    app.run(debug=True)
    