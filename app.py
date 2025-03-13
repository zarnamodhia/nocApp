import os
import base64
import urllib.parse
import io
from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# MongoDB Atlas Setup
encoded_username = urllib.parse.quote_plus(os.getenv("modhiazarnaa"))
encoded_password = urllib.parse.quote_plus(os.getenv("zarna@6408"))
database_name = "NocDatabase"

client = MongoClient(f"mongodb+srv://{encoded_username}:{encoded_password}@nocdatabase.u7b7o.mongodb.net/{database_name}?retryWrites=true&w=majority")
db = client["NocDatabase"]
collection = db["UserDetails"]

# Allowed File Extensions
ALLOWED_EXTENSIONS = {"pdf"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# Serve HTML Form
@app.route("/")
def index():
    return render_template("index.html")

# File Upload Route (Stores PDFs as Base64 in MongoDB)
@app.route("/upload", methods=["POST"])
def upload_files():
    try:
        username = request.form["username"]
        email = request.form["email"]
        noc_file = request.files["noc_certificate"]
        bill_file = request.files["bill_receipt"]

        # Validate File Type
        if not (allowed_file(noc_file.filename) and allowed_file(bill_file.filename)):
            return jsonify({"error": "Only PDF files are allowed"}), 400

        # Convert PDFs to Base64
        noc_base64 = base64.b64encode(noc_file.read()).decode("utf-8")
        bill_base64 = base64.b64encode(bill_file.read()).decode("utf-8")

        # Store Base64 string in MongoDB
        data = {
            "username": username,
            "email": email,
            "noc_certificate_base64": noc_base64,
            "bill_receipt_base64": bill_base64,
        }
        result = collection.insert_one(data)

        return jsonify({"message": "Data stored successfully", "id": str(result.inserted_id)}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Serve PDF for Download
@app.route("/download/<file_type>/<user_id>", methods=["GET"])
def download_pdf(file_type, user_id):
    try:
        # Find the user data in MongoDB
        user_data = collection.find_one({"_id": ObjectId(user_id)})
        if not user_data:
            return jsonify({"error": "User not found"}), 404

        # Get the Base64 string of the requested file
        if file_type == "noc_certificate":
            pdf_base64 = user_data.get("noc_certificate_base64")
            filename = "noc_certificate.pdf"
        elif file_type == "bill_receipt":
            pdf_base64 = user_data.get("bill_receipt_base64")
            filename = "bill_receipt.pdf"
        else:
            return jsonify({"error": "Invalid file type"}), 400

        if not pdf_base64:
            return jsonify({"error": "File not found"}), 404

        # Convert Base64 back to PDF file
        pdf_data = base64.b64decode(pdf_base64)
        pdf_io = io.BytesIO(pdf_data)

        return send_file(pdf_io, mimetype="application/pdf", as_attachment=True, download_name=filename)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
