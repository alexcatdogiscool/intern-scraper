from flask import Flask, request, jsonify
from flask_cors import CORS
import database


app = Flask(__name__)
CORS(app)

@app.route("/jobs", methods=["GET", "POST"])
def jobs():
    if request.method == 'GET':
        all_jobs = database.load_all_jobs()
        return jsonify(all_jobs)
    
    if request.method == 'POST':
        data = request.get_json()
        job_name = data["job_name"]
        company_name = data["company"]
        new_status = data["new_status"]
        
        database.update_status(job_name, company_name, new_status)
        
        return jsonify({"success": True})