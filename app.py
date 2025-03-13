import os
import cloudinary
import cloudinary.uploader
import pymongo
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv

import urllib.parse

MONGO_USERNAME = urllib.parse.quote_plus(os.getenv("MONGO_USERNAME", ""))
MONGO_PASSWORD = urllib.parse.quote_plus(os.getenv("MONGO_PASSWORD", ""))
MONGO_CLUSTER = os.getenv("MONGO_CLUSTER", "")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "NocDatabase")

MONGO_URI = f"mongodb+srv://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_CLUSTER}/{MONGO_DB_NAME}?retryWrites=true&w=majority"

client = pymongo.MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]
collection = db["UserDetails"]

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)
# 🔹 Render HTML Form
@app.route("/")
def index():
    return render_template("index.html")

# 🔹 Handle Form Submission & File Upload
@app.route("/submit", methods=["POST"])
def submit_form():
    name = request.form.get("name")
    email = request.form.get("email")

    if "noc_certificate" not in request.files or "bill_receipt" not in request.files:
        return jsonify({"error": "Both NOC and Bill Receipt are required"}), 400

    noc_certificate = request.files["noc_certificate"]
    bill_receipt = request.files["bill_receipt"]

    # Upload PDFs to Cloudinary
    noc_response = cloudinary.uploader.upload(noc_certificate, resource_type="raw")
    bill_response = cloudinary.uploader.upload(bill_receipt, resource_type="raw")

    # Store user data in MongoDB
    user_data = {
        "name": name,
        "email": email,
        "noc_certificate_url": noc_response["secure_url"],
        "bill_receipt_url": bill_response["secure_url"]
    }
    inserted_user = collection.insert_one(user_data)

    return jsonify({
        "message": "Data submitted successfully!",
        "data": {
            "_id": str(inserted_user.inserted_id),
            "name": name,
            "email": email,
            "noc_certificate_url": noc_response["secure_url"],
            "bill_receipt_url": bill_response["secure_url"]
        }
    }), 201

# 🔹 Retrieve All Users & Uploaded Files
@app.route("/get_users", methods=["GET"])
def get_users():
    users = collection.find({}, {"_id": 1, "name": 1, "email": 1, "noc_certificate_url": 1, "bill_receipt_url": 1})

    formatted_users = [{
        "_id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "noc_certificate_url": user["noc_certificate_url"],
        "bill_receipt_url": user["bill_receipt_url"]
    } for user in users]

    return jsonify({"users": formatted_users}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=10000)
