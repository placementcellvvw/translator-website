from flask import Flask, render_template, request, redirect, session
import requests
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename
app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
TRANSLATED_FOLDER = "translated"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TRANSLATED_FOLDER, exist_ok=True)
app.secret_key = "secret123"

# DATABASE (optional)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# MODEL
class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    message = db.Column(db.Text)

class TranslationFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200))
    translated_file = db.Column(db.String(200))
    customer_name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    paid = db.Column(db.Boolean, default=False)
with app.app_context():
    db.create_all()

# HOME PAGE
@app.route("/", methods=["GET", "POST"])
def home():
    msg = ""
    translated_text = ""

    if request.method == "POST":

        # 🔹 AI TRANSLATION
        text = request.form.get("translate_text")
        if text:
            try:
                url = "https://translate.googleapis.com/translate_a/single"
                params = {
                    "client": "gtx",
                    "sl": "en",
                    "tl": "hi",
                    "dt": "t",
                    "q": text
                }
                response = requests.get(url, params=params)
                result = response.json()
                translated_text = result[0][0][0]
            except:
                translated_text = "Translation error"

        # 🔹 CONTACT FORM + GOOGLE SHEET
        if request.form.get("name"):

            # (Optional DB Save)
            new_contact = Contact(
                name=request.form["name"],
                email=request.form["email"],
                phone=request.form["phone"],
                message=request.form["message"]
            )
            db.session.add(new_contact)
            db.session.commit()

            # 🔥 GOOGLE SHEET SEND
            data = {
                "name": request.form["name"],
                "email": request.form["email"],
                "phone": request.form["phone"],
                "message": request.form["message"]
            }

            response = requests.post(
                "https://script.google.com/macros/s/AKfycbwYO41lKGOvPvCCJj3456ERpLWV3hkGaDkM9Pse5wqwbNSrydveDKFfjYtrOM12Gopcwg/exec",
                json=data
            )

            print("RESPONSE:", response.text)

            msg = "Data saved successfully!"

    return render_template("index.html", message=msg, translated=translated_text)


# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == "admin" and request.form["password"] == "1234":
            session["admin"] = True
            return redirect("/admin")
    return render_template("login.html")


# ADMIN PANEL
@app.route("/admin")
def admin():
    if not session.get("admin"):
        return redirect("/login")
    data = Contact.query.all()
    return render_template("admin.html", data=data)

@app.route("/dashboard")
def dashboard():
    try:
        url = "https://script.google.com/macros/s/AKfycbwYO41lKGOvPvCCJj3456ERpLWV3hkGaDkM9Pse5wqwbNSrydveDKFfjYtrOM12Gopcwg/exec"

        response = requests.get(url)
        data = response.json()

        return render_template("dashboard.html", data=data)

    except Exception as e:
        return "Data load failed: " + str(e)

@app.route('/upload_translation', methods=['POST'])
def upload_translation():

    file = request.files['file']
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']

    if file:

        filename = secure_filename(file.filename)

        filepath = os.path.join(UPLOAD_FOLDER, filename)

        file.save(filepath)

        new_file = TranslationFile(
            filename=filename,
            customer_name=name,
            email=email,
            phone=phone,
            paid=False
        )

        db.session.add(new_file)
        db.session.commit()

        return "File Uploaded Successfully"

    return "Upload Failed"
     
if __name__ == "__main__":
    app.run(debug=True)
