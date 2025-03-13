import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from pymongo import MongoClient
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# MongoDB Atlas Setup
client = MongoClient(os.getenv("MONGO_URI"))
db = client["NocDatabase"]
collection = db["UserDetails"]

# Cloudinary Setup
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)

# Serve HTML Form
@app.route("/")
def index():
    return render_template("index.html")

# File Upload Route
@app.route("/upload", methods=["POST"])
def upload_files():
    try:
        username = request.form["username"]
        email = request.form["email"]
        noc_file = request.files["noc_certificate"]
        bill_file = request.files["bill_receipt"]

        # Upload PDFs to Cloudinary
        noc_upload = cloudinary.uploader.upload(noc_file, resource_type="raw")
        bill_upload = cloudinary.uploader.upload(bill_file, resource_type="raw")

        # Store Data in MongoDB
        data = {
            "username": username,
            "email": email,
            "noc_certificate_url": noc_upload["secure_url"],
            "bill_receipt_url": bill_upload["secure_url"],
        }
        collection.insert_one(data)

        return jsonify({"message": "Data stored successfully", "data": data}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run Flask app
if __name__ == "__main__":
    app.run(debug=True)
