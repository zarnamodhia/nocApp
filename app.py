from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pymongo
import urllib.parse
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# 🔹 MongoDB Atlas Connection
MONGO_USERNAME = os.getenv("MONGO_USERNAME")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
CLUSTER_URL = os.getenv("CLUSTER_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME")

# Encode credentials
encoded_username = urllib.parse.quote_plus(MONGO_USERNAME)
encoded_password = urllib.parse.quote_plus(MONGO_PASSWORD)

# MongoDB Connection URI
MONGO_URI = f"mongodb+srv://{encoded_username}:{encoded_password}@{CLUSTER_URL}/{DATABASE_NAME}?retryWrites=true&w=majority"

# Connect to MongoDB
client = pymongo.MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
collection = db["UserDetails"]

# 🔹 Render HTML Form
@app.route("/")
def index():
    return render_template("index.html")

# 🔹 Handle Form Submission
@app.route("/submit", methods=["POST"])
def submit_form():
    name = request.form.get("name")
    email = request.form.get("email")

    if not name or not email:
        return jsonify({"error": "Name and email are required"}), 400

    # Store user data in MongoDB
    user_data = {"name": name, "email": email}
    inserted_user = collection.insert_one(user_data)

    # Convert inserted _id to string
    user_data["_id"] = str(inserted_user.inserted_id)

    return jsonify({"message": "Data submitted successfully!", "data": user_data}), 201

# 🔹 Retrieve All Users
@app.route("/get_users", methods=["GET"])
def get_users():
    users = collection.find({}, {"_id": 1, "name": 1, "email": 1})  # Fetch name & email only

    formatted_users = [{"_id": str(user["_id"]), "name": user["name"], "email": user["email"]} for user in users]

    return jsonify({"users": formatted_users}), 200

if __name__ == "__main__":
    app.run(debug=True)
