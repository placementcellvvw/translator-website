from flask import Flask, render_template, request, redirect, session
import requests
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "secret123"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    message = db.Column(db.Text)

with app.app_context():
    db.create_all()

@app.route("/", methods=["GET", "POST"])
def home():
    msg = ""
    translated_text = ""

    if request.method == "POST":

        # TEMP TRANSLATOR (no crash)
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

        # CONTACT FORM
        if request.form.get("name"):
            new_contact = Contact(
                name=request.form["name"],
                email=request.form["email"],
                phone=request.form["phone"],
                message=request.form["message"]
            )
            db.session.add(new_contact)
            db.session.commit()
            msg = "Data saved successfully!"

    return render_template("index.html", message=msg, translated=translated_text)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == "admin" and request.form["password"] == "1234":
            session["admin"] = True
            return redirect("/admin")
    return render_template("login.html")


@app.route("/admin")
def admin():
    if not session.get("admin"):
        return redirect("/login")
    data = Contact.query.all()
    return render_template("admin.html", data=data)


if __name__ == "__main__":
    app.run(debug=True)
