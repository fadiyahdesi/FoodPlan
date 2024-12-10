from flask import Flask, jsonify, request, render_template, session, redirect, url_for
from flask_cors import CORS
from controllers.PasswordController import forgot_password, resend_otp, reset_password, verify_otp
from controllers.ValidasiController import validasi
from controllers.mobile.Produk import getUserAndProduk
from controllers.mobile.DeteksiController import predict
from controllers.mobile.Users import gantiavatar, update_profileAll, userProfile
from controllers.mobile.planning import getPlanning
from models.connectDB import db, Product
from controllers.ProductController import products
from controllers.ChatController import ChatController
from sqlalchemy import func
from controllers.AuthController import loginMobile, registerMobile
from controllers.AdminController import UserList, create_product, dashboard, delete_product, loginAdmin, produkAdmin, update_product
from controllers.ResepController import resep
from controllers.AdminController import add_user, edit_user, delete_user
import base64  # <-- Tambahkan baris ini untuk mengimpor base64
import logging
from authlib.integrations.flask_client import OAuth
from services.auth_service import AuthService
from services.middleware import token_required


app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:@localhost/foodplan"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)  # Initialize the SQLAlchemy instance with the app

chat_controller = ChatController(app, api_key="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", pdf_path="data/chatbot.pdf")
app.secret_key = 'foodplan_123'

# Konfigurasi logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.get("/")
def product_list():
    return products()

# Define route to get chatbot response
@app.route('/get_response', methods=['POST'])
def get_chat_response():
    return chat_controller.get_response()

@app.route('/admin', methods=['GET', 'POST'])
def login():
    return loginAdmin()

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

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
    limit = request.args.get('limit', 8)  # Ambil parameter limit (default 8)
    try:
        limit = int(limit)  # Konversi limit ke integer
    except ValueError:
        limit = 8  # Default ke 8 jika nilai limit tidak valid

    # Query produk berdasarkan kategori yang dipilih
    query = db.select(Product)
    if selected_category == 'dietnormal':
        query = query.filter(Product.category_id == 1)
    elif selected_category == 'dietBerat':
        query = query.filter(Product.category_id == 2)
    elif selected_category == 'dietSport':
        query = query.filter(Product.category_id == 3)
    elif selected_category == 'dietKhusus':
        query = query.filter(Product.category_id == 4)
    elif selected_category == 'diet2Nyawa':
        query = query.filter(Product.category_id == 5)

    # Terapkan limit jika diperlukan
    if limit > 0:
        query = query.limit(limit)

    # Eksekusi query
    products = db.session.execute(query).scalars().all()

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
    return render_template('user/index.html', products=products_with_images, selected_category=selected_category)

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
        if 'files' not in request.files:
            logger.error("No files part in the request.")
            return jsonify({'status': 'error', 'message': 'No files part in the request.'}), 400

        files = request.files.getlist('files')  # Ambil semua file
        if not files:
            logger.error("No files uploaded.")
            return jsonify({'status': 'error', 'message': 'No files uploaded.'}), 400

        logger.info(f"{len(files)} files received.")
        
        # Panggil fungsi prediksi
        results = predict(files)  # Panggil fungsi baru
        logger.info(f"Prediction results: {results}")

        # Format hasil
        return jsonify({'status': 'success', 'results': results}), 200

    except Exception as e:
        logger.error(f"Internal Server Error: {str(e)}")
        return jsonify({'status': 'error', 'message': f'Internal Server Error: {str(e)}'}), 500



#================================================================================================================
# Mobile Server 
#================================================================================================================

@app.route('/login', methods=['POST'])
def login_page():
    return loginMobile()

@app.route('/register', methods=['POST'])
def register_user():
    return registerMobile()

@app.route('/forgot-password', methods=['POST'])
def forgotPassword():
    return forgot_password()

@app.route('/verify-otp', methods=['POST'])
def verifyToken():
    return verify_otp()

@app.route('/reset-password', methods=['POST'])
def resetPassword():
    return reset_password()

@app.route('/resend-otp', methods=['POST'])
def resendOtp():
    return resend_otp()

@app.route('/validate', methods=['POST'])
@token_required
def validasi_user(users_id):
    # print(f"users_id yang diterima di validasi_user: {users_id}")
    return validasi(users_id)


@app.route("/beranda", methods=['GET'])
@token_required
def produk_page(users_id):
    return getUserAndProduk(users_id)
    # print(f"users_id yang diterima di produk_page: {users_id}")
    # return prodMobile(users_id)

@app.route('/user-profile', methods=['GET'])
@token_required
def profileUser(users_id):
    print(f"users_id yang diterima di user-beranda: {users_id}")
    return userProfile(users_id)

@app.route('/upload-profile-image', methods=['POST'])
@token_required
def uploadProfileImage(users_id):
    return gantiavatar(users_id)

@app.route('/update-profile', methods=['PUT'])
@token_required
def updateProfile(users_id):
    return update_profileAll(users_id)

@app.route('/planning-page', methods=['GET'])
@token_required
def planningPage(users_id):
    return getPlanning(users_id)

if __name__ == "__main__":
    app.run(debug=True)
    