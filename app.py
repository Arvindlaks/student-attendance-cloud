from flask import Flask, render_template, request, redirect
from google.cloud import firestore
from google.oauth2 import service_account
import os
import json
app = Flask(__name__)

service_account_info = json.loads(
    os.environ["GOOGLE_APPLICATION_CREDENTIALS_JSON"]
)

cred = service_account.Credentials.from_service_account_info(
    service_account_info
)

db = firestore.Client(credentials=cred, project=cred.project_id)
@app.route("/")
def home():
    return render_template("faculty.html")

@app.route("/add_student", methods=["POST"])
def add_student():
    roll = request.form["roll"]
    db.collection("students").document(roll).set({
        "rollNo": roll,
        "name": request.form["name"],
        "department": request.form["department"],
        "semester": int(request.form["semester"])
    })
    return redirect("/")

@app.route("/mark", methods=["POST"])
def mark():
    db.collection("attendance").add({
        "rollNo": request.form["roll"],
        "name": request.form["name"],
        "subject": request.form["subject"],
        "date": request.form["date"],
        "status": request.form["status"]
    })
    return redirect("/")

@app.route("/student/<roll>")
def student(roll):
    docs = db.collection("attendance").where("rollNo","==",roll).stream()

    records = []
    total = 0
    present = 0

    for d in docs:
        data = d.to_dict()
        records.append(data)
        total += 1
        if data["status"] == "Present":
            present += 1

    percentage = 0 if total == 0 else round((present/total)*100,2)

    return render_template(
        "student.html",
        roll=roll,
        records=records,
        percentage=percentage
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
