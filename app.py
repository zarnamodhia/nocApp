import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from pymongo import MongoClient
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv
import urllib.parse
import uuid

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# MongoDB Atlas Setup
encoded_username=urllib.parse.quote_plus("modhiazarnaa")
encoded_password=urllib.parse.quote_plus("zarna@6408")
database_name="NocDatabase"
client = MongoClient(f"mongodb+srv://{encoded_username}:{encoded_password}@nocdatabase.u7b7o.mongodb.net/{database_name}?retryWrites=true&w=majority")
db = client["NocDatabase"]
collection = db["UserDetails"]

# Cloudinary Setup
cloudinary.config(
    cloud_name="dqzrfjurn",
    api_key="297492448329361",
    api_secret="CRR0aYWoUTjgSYZ0FOsjOvUhJMs",
)

ALLOWED_EXTENSIONS = {"pdf"}
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

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

        if not (allowed_file(noc_file.filename) and allowed_file(bill_file.filename)):
            return jsonify({"error": "Only PDF files are allowed"}), 400

        # Generate Unique Filenames
        noc_filename = f"noc_{uuid.uuid4()}.pdf"
        bill_filename = f"bill_{uuid.uuid4()}.pdf"

        # Upload PDFs to Cloudinary
        noc_upload = cloudinary.uploader.upload(noc_file, resource_type="raw",public_id=noc_filename, format="pdf",type="upload",overwrite=True)
        bill_upload = cloudinary.uploader.upload(bill_file, resource_type="raw",public_id=bill_filename, format="pdf",type="upload",overwrite=True)

        # Store Data in MongoDB
        data = {
            "username": username,
            "email": email,
            "noc_certificate_url": noc_upload["secure_url"],
            "bill_receipt_url": bill_upload["secure_url"],
        }
        result = collection.insert_one(data)
        stored_data = collection.find_one({"_id": result.inserted_id})
        stored_data["_id"] = str(stored_data["_id"])  # Convert ObjectId to string

        return jsonify({"message": "Data stored successfully", "data": stored_data}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run Flask app
if __name__ == "__main__":
    app.run(debug=True)
