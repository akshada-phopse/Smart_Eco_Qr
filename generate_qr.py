from flask import Flask, request, jsonify
import qrcode
import mysql.connector
import json
import cloudinary
import cloudinary.uploader
from datetime import datetime
import os

app = Flask(__name__)

# Cloudinary Configuration
cloudinary.config(
    cloud_name="dy7jrabpa",
    api_key="687789493943795",
    api_secret="tzx4h-ssVG8933P54MwsTcttkGY"
)

# InfinityFree Database connection
def db_connect():
    return mysql.connector.connect(
        host="sql302.infinityfree.com",
        user="if0_38421232",
        password="AkshadaF2012",
        database="if0_38421232_ecocommute"
    )

def insert_qr_code_path(pass_id, qr_code_url):
    conn = db_connect()
    cursor = conn.cursor()
    try:
        update_query = "UPDATE pass SET qr_code_path = %s WHERE pass_id = %s"
        cursor.execute(update_query, (qr_code_url, pass_id))
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    finally:
        cursor.close()
        conn.close()

def generate_qr_code(pass_id, user_id, destination, start_date, end_date):
    qr_data = json.dumps({
        "pass_id": pass_id,
        "user_id": user_id,
        "destination": destination,
        "start_date": start_date,
        "end_date": end_date
    })
    qr_code_filename = f"{user_id}_{pass_id}.png"
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(qr_code_filename)

    upload_result = cloudinary.uploader.upload(qr_code_filename)
    qr_code_url = upload_result.get("secure_url")

    # Clean up local file after upload
    if os.path.exists(qr_code_filename):
        os.remove(qr_code_filename)

    insert_qr_code_path(pass_id, qr_code_url)

    return qr_code_url

@app.route('/generate_qr', methods=['POST'])
def handle_generate_qr():
    try:
        data = request.json
        pass_id = data['pass_id']
        user_id = data['user_id']
        destination = data['destination']
        start_date = data['start_date']
        end_date = data['end_date']

        qr_code_url = generate_qr_code(pass_id, user_id, destination, start_date, end_date)

        return jsonify({
            "status": "success",
            "message": "QR code generated and uploaded.",
            "qr_code_url": qr_code_url
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
