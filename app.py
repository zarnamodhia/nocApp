import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from pymongo import MongoClient
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv
import urllib.parse

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
        result = collection.insert_one(data)
        data[")id"]=str(result.inserted_id)
        return jsonify({"message": "Data stored successfully", "data": data}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run Flask app
if __name__ == "__main__":
    app.run(debug=True)
