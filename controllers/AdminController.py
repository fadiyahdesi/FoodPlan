from flask import render_template, request, redirect, url_for, flash, session
from hashlib import md5
from werkzeug.security import check_password_hash  # Ganti 'your_application' dengan nama aplikasi Anda
from models.connectDB import User, Role, Product, db, Category
import base64, hashlib

def loginAdmin():
    if request.method == 'POST':
        identifier = request.form['identifier']  # Username atau Email
        password = request.form['password']
        
        # Hash password dengan MD5
        hashed_password = md5(password.encode()).hexdigest()  # Menggunakan MD5 untuk hashing
        
        # Ambil user dari database berdasarkan username atau email
        user = User.query.filter((User.username == identifier) | (User.email == identifier)).first()
        
        if user and user.password == hashed_password:  # Bandingkan hashed password
            # Cek apakah role user adalah admin
            role = Role.query.get(user.role_id)  # Dapatkan role berdasarkan role_id
            if role and role.role == 'admin':
                # Jika username/email dan password benar serta role admin
                session['admin_id'] = user.id  # Simpan id admin di session
                flash('Login berhasil!', 'success')
                return redirect(url_for('dashboardAdmin'))  # Ganti dengan route yang sesuai
            else:
                flash('Akses ditolak: Anda bukan admin.', 'danger')
        else:
            flash('Nama pengguna/email atau kata sandi salah.', 'danger')

    return render_template('admin/LoginRegister/Login.html')  # Pastikan ada template login.html

def detect_avatar_format(avatar_data):
    """Deteksi format gambar berdasarkan header byte."""
    if avatar_data.startswith(b'\xff\xd8'):
        return "jpeg"  # Ini berlaku untuk .jpg dan .jpeg
    elif avatar_data.startswith(b'\x89PNG'):
        return "png"
    elif avatar_data.startswith(b'RIFF') and avatar_data[8:12] == b'WEBP':
        return "webp"
    else:
        return "jpeg"
    
def dashboard():
    # Periksa apakah admin sudah login
    if 'admin_id' not in session:
        flash('Silakan login terlebih dahulu.', 'warning')
        return redirect(url_for('login'))

    # Ambil data user berdasarkan admin_id yang ada di session
    user = User.query.get(session['admin_id'])

    # Deteksi format avatar untuk admin yang sedang login
    avatar_format = None
    avatar_data = None
    if user.avatar:
        avatar_format = detect_avatar_format(user.avatar)
        avatar_data = base64.b64encode(user.avatar).decode('utf-8')

    # Ambil semua admin
    admins = User.query.filter_by(role_id=1).all()

    # Siapkan data untuk setiap admin
    for admin in admins:
        if admin.avatar:
            admin.avatar_format = detect_avatar_format(admin.avatar)
            admin.avatar_data = base64.b64encode(admin.avatar).decode('utf-8')
        else:
            admin.avatar_format = None
            admin.avatar_data = None

    # Kirim data user dan statistik ke template dashboard.html
    return render_template('admin/pages/dashboard.html',
                           admins=admins,
                           nama=user.nama,
                           email=user.email,
                           role=user.role.role,
                           avatar_data=avatar_data,
                           avatar_format=avatar_format)

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

def produkAdmin():
    # Check if the admin is logged in
    if 'admin_id' not in session:
        flash('Silakan login terlebih dahulu.', 'warning')
        return redirect(url_for('login'))

    # Get the logged-in user's details
    user = User.query.get(session['admin_id'])

    # Detect avatar format and encode it for the logged-in admin
    avatar_format = None
    avatar_data = None
    if user.avatar:
        avatar_format = detect_image_format(user.avatar)
        avatar_data = base64.b64encode(user.avatar).decode('utf-8')

    # Get selected category from request arguments
    selected_category_id = request.args.get('category')

    # Query products based on selected category
    query = db.select(Product).order_by(Product.id)
    if selected_category_id:
        query = query.where(Product.category_id == selected_category_id)
    products = db.session.execute(query).scalars().all()

    # Process products with images
    products_with_images = []
    for product in products:
        image_src = None
        if product.images:
            # Detect image format
            image_format = detect_image_format(product.images)
            image_data = base64.b64encode(product.images).decode('utf-8')
            image_src = f"data:image/{image_format};base64,{image_data}"

        products_with_images.append({
            'id': product.id,
            'title': product.title,
            'description': product.description,
            'image_src': image_src,
            'category_name': product.category.name if product.category else None
        })

    # Retrieve distinct categories for the dropdown
    categories = db.session.query(Category).all()

    # Render template with user details and products
    return render_template(
        'admin/pages/produk.html',
        products=products_with_images,
        categories=categories,
        selected_category=selected_category_id,
        nama=user.nama,
        email=user.email,
        avatar_data=avatar_data,
        avatar_format=avatar_format
    )

def create_product():
    # Check if the admin is logged in
    if 'admin_id' not in session:
        flash('Silakan login terlebih dahulu.', 'warning')
        return redirect(url_for('login'))

    # Get the logged-in user's details
    user = User.query.get(session['admin_id'])

    # Detect avatar format and encode it for the logged-in admin
    avatar_format = None
    avatar_data = None
    if user.avatar:
        avatar_format = detect_image_format(user.avatar)
        avatar_data = base64.b64encode(user.avatar).decode('utf-8')
            
    if request.method == 'POST':
        # Get form data with validation
        title = request.form.get('title')
        description = request.form.get('description')
        ingredients = request.form.get('ingredients')
        steps = request.form.get('steps')
        category_id = request.form.get('category_id')
        
        # Optional fields with default values if not provided
        carbohidrat = request.form.get('carbohidrat', 0)
        protein = request.form.get('protein', 0)
        fat = request.form.get('fat', 0)
        
        # Check for required fields
        if not (title and description and ingredients and steps and category_id):
            flash("Please fill in all required fields.", "danger")
            return redirect(url_for('tambah_produk'))
        
        # Process image file if provided
        image = request.files.get('image')
        image_data = image.read() if image else None
        
        # Create a new product instance
        new_product = Product(
            title=title,
            description=description,
            ingredients=ingredients,
            steps=steps,
            category_id=category_id,
            carbohidrat=carbohidrat,
            protein=protein,
            fat=fat,
            images=image_data
        )

        # Save to the database
        try:
            db.session.add(new_product)
            db.session.commit()
            flash('Product created successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {str(e)}", "danger")
            return redirect(url_for('tambah_produk'))

        return redirect(url_for('product_admin'))

    # Get categories for dropdown
    categories = db.session.query(Category).all()
    return render_template(
        'admin/pages/crudProduk/tambah.html',
        categories=categories,
        avatar_data=avatar_data,
        avatar_format=avatar_format
    )

def update_product(id):
    product = Product.query.get(id)
    if request.method == 'POST':
        # Update product details from form
        product.title = request.form['title']
        product.description = request.form['description']
        product.category_id = request.form['category_id']
        product.ingredients = request.form.get('ingredients')  # Get ingredients
        product.steps = request.form.get('steps')  # Get steps
        product.carbohidrat = request.form.get('carbohidrat', type=float)  # Get and convert to float
        product.protein = request.form.get('protein', type=float)  # Get and convert to float
        product.fat = request.form.get('fat', type=float)  # Get and convert to float

        # Check if a new image is uploaded and update it
        if 'image' in request.files:
            image = request.files['image']
            if image:
                product.images = image.read()  # Store image binary data

        # Commit the updates to the database
        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('product_admin'))

    # Render the edit page with existing data
    categories = Category.query.all()  # Retrieve all categories for dropdown
    return render_template('admin/pages/crudProduk/edit.html', product=product, categories=categories)
    
def delete_product(id):
    product = Product.query.get(id)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('product_admin'))

def md5_hash(text):
    return hashlib.md5(text.encode()).hexdigest()

def UserList():
    # Memeriksa apakah pengguna sudah login
    if 'admin_id' not in session:
        flash('Silakan login terlebih dahulu.', 'warning')
        return redirect(url_for('login'))

    # Mengambil detail pengguna yang sedang login
    user = User.query.get(session['admin_id'])

    # Mendeteksi format avatar dan mengkodekannya untuk pengguna yang sedang login
    avatar_format = None
    avatar_data = None
    if user.avatar:
        avatar_format = detect_image_format(user.avatar)
        avatar_data = base64.b64encode(user.avatar).decode('utf-8')

    # Mengambil semua pengguna dari database
    all_users = User.query.all()

    # Menyiapkan data untuk semua pengguna
    user_data_all = []
    for u in all_users:
        avatar_format_u = None
        avatar_data_u = None
        if u.avatar:
            avatar_format_u = detect_image_format(u.avatar)
            avatar_data_u = base64.b64encode(u.avatar).decode('utf-8')
        
        user_data_all.append({
            'id': u.id,
            'nama': u.nama,
            'username': u.username,
            'email': u.email,
            'avatar_data': avatar_data_u,
            'avatar_format': avatar_format_u,
            'original_password': u.password,
            'role': u.role.role  # Mengambil nama role
        })

    # Render template dengan data pengguna
    return render_template(
        'admin/pages/listuser.html',  # Template untuk dashboard
        id=user.id,
        nama=user.nama,
        avatar_data=avatar_data,
        avatar_format=avatar_format,
        user_data_all=user_data_all  # Mengirimkan semua data pengguna
    )
    
def list_users():
    users = User.query.all()
    return render_template("admin/pages/listuser.html", users=users)

# Menambahkan user baru
def add_user():
    if request.method == 'POST':
        # Ambil data dari form
        nama = request.form['nama']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role_id = request.form['role_id']

        # Hash password
        hashed_password = hashlib.md5(password.encode()).hexdigest()

        # Buat user baru tanpa menyebutkan updated_at
        new_user = User(
            nama=nama,
            username=username,
            email=email,
            password=hashed_password,
            role_id=role_id
        )

        # Simpan ke database
        db.session.add(new_user)
        db.session.commit()
        flash('User berhasil ditambahkan!', 'success')
        return redirect(url_for('ListUser'))

    # Tampilkan form tambah user
    roles = Role.query.all()
    return render_template('admin/pages/crudUser/add_user.html', roles=roles)

# Mengedit user
def edit_user(user_id):
    user = User.query.get(user_id)
    if request.method == 'POST':
        user.nama = request.form['nama']
        user.username = request.form['username']
        user.email = request.form['email']
        password = request.form['password']
        user.role_id = request.form['role_id']

        # Jika password diubah, hash ulang
        if password:
            user.password = hashlib.md5(password.encode()).hexdigest()
        
        db.session.commit()
        flash('User berhasil diupdate!', 'success')
        return redirect(url_for('ListUser'))

    roles = Role.query.all()
    return render_template('admin/pages/crudUser/edit_user.html', user=user, roles=roles)

# Menghapus user
def delete_user(user_id):
    user = User.query.get(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User berhasil dihapus!', 'success')
    return redirect(url_for('ListUser'))