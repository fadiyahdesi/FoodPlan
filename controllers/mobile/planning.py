import base64
import os
from flask import json, jsonify
from models.connectDB import DetailPlanning, db, Planning, Product, Kegiatan

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

def getPlanning(users_id):
    try:
        with db.session.begin():
            plans = Planning.query.all()  # Ambil semua data dari tabel Planning
            results = []

            for plan in plans:
                # Proses gambar untuk tiap Planning
                images = None
                if plan.images:
                    image_format = detect_image_format(plan.images)
                    image_data = base64.b64encode(plan.images).decode('utf-8')
                    images = f"data:image/{image_format};base64,{image_data}"

                # Ambil nama kategori
                category_name = plan.category.name if plan.category else None
                
                # Ambil aktivitas berdasarkan planning_id
                aktivitas_plan = []
                if plan.id:
                    aktivitas1 = Kegiatan.query.filter(Kegiatan.planning_id == plan.id).all()  # Perbaikan di sini
                    for aktivitas in aktivitas1:
                        aktivitas_plan.append({
                            'id': aktivitas.id,
                            'planning_id': aktivitas.planning_id,
                            'aktivitas': aktivitas.aktivitas,
                        })
                
                # Rekomendasi makanan berdasarkan category_id
                recommended_foods = {
                    "Pagi": [],
                    "Siang": [],
                    "Malam": []
                }

                if plan.category_id:
                    products = Product.query.filter_by(category_id=plan.category_id).all()
                    for product in products:
                        product_image = None
                        if product.images:
                            try:
                                image_format = detect_image_format(product.images)
                                image_data = base64.b64encode(product.images).decode('utf-8')
                                product_image = f"data:image/{image_format};base64,{image_data}"
                            except Exception:
                                product_image = None

                        product_data = {
                            'id': product.id,
                            'title': product.title,
                            'category_id': product.category_id,
                            'category_name': product.category.name if product.category else None,
                            'description': product.description,
                            'ingredients': product.ingredients,  # Tambahan ingredients
                            'steps': product.steps,  # Tambahan steps
                            'carbohidrat': product.carbohidrat,  # Tambahan carbohidrat
                            'protein': product.protein,  # Tambahan protein
                            'fat': product.fat,  # Tambahan fat
                            'images_src': product_image,
                        }

                        # Tentukan waktu makan berdasarkan deskripsi
                        if "sarapan" in product.description.lower() or "pagi" in product.description.lower() or "buah" in product.description.lower() or "sayur" in product.description.lower():
                            if product_data not in recommended_foods["Pagi"]:
                                recommended_foods["Pagi"].append(product_data)
                        if "makan siang" in product.description.lower() or "siang" in product.description.lower() or "daging" in product.description.lower() or "oatmeal" in product.description.lower():
                            if product_data not in recommended_foods["Siang"]:
                                recommended_foods["Siang"].append(product_data)
                        if "makan malam" in product.description.lower() or "malam" in product.description.lower() or "protein tinggi" in product.description.lower() or "lemak rendah" in product.description.lower() or "daging" in product.description.lower():
                            if product_data not in recommended_foods["Malam"]:
                                recommended_foods["Malam"].append(product_data)


                # Ambil data dari tabel DetailPlanning yang sesuai
                details = []
                detail_plans = DetailPlanning.query.filter_by(planning_id=plan.id).all()
                for detail in detail_plans:
                    details.append({
                        'durasi': detail.durasi,
                        'kesulitan': detail.kesulitan,
                        'komitmen': detail.komitmen,
                        'pilih': detail.pilih,
                        'lakukan': detail.lakukan,
                    })

                # Tambahkan data ke hasil
                results.append({
                    'id': plan.id,
                    'nama': plan.nama,
                    'categoryId': plan.category_id,
                    'categoryName': category_name,
                    'description': plan.description,
                    'image': images,
                    'rekomendasiMakanan': recommended_foods,  # Daftar makanan yang direkomendasikan
                    'details': details,
                    'aktivitas': aktivitas_plan,
                })

        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
