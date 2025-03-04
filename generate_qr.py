import sys
import qrcode
import mysql.connector
import json
import cloudinary
import cloudinary.uploader
from datetime import datetime

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
        # Update the pass table with the QR code URL
        update_query = "UPDATE pass SET qr_code_path = %s WHERE pass_id = %s"
        cursor.execute(update_query, (qr_code_url, pass_id))
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    finally:
        cursor.close()
        conn.close()

def generate_qr_code(pass_id, user_id, destination, start_date, end_date):
    # Prepare the QR code data in JSON format
    qr_data = json.dumps({
        "pass_id": pass_id,
        "user_id": user_id,
        "destination": destination,
        "start_date": start_date,
        "end_date": end_date
    })
    qr_code_path = f"{user_id}_{pass_id}.png"
    
    # Generate QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)

    # Create an image from the QR Code instance
    img = qr.make_image(fill_color="black", back_color="white")

    # Save QR code locally
    img.save(qr_code_path)

    # Upload QR to Cloudinary
    upload_result = cloudinary.uploader.upload(qr_code_path)
    qr_code_url = upload_result.get("secure_url")

    # Insert Cloudinary QR code URL into the database
    insert_qr_code_path(pass_id, qr_code_url)

if __name__ == "__main__":
    # Command line arguments
    pass_id = sys.argv[1]
    user_id = sys.argv[2]
    destination = sys.argv[3]
    start_date = sys.argv[4]
    end_date = sys.argv[5]

    # Call the function to generate and upload QR code
    generate_qr_code(pass_id, user_id, destination, start_date, end_date)
