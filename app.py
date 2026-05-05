from flask import Flask, render_template, request, redirect, session
import requests
import os
app = Flask(__name__)
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    data = []

    try:
        url = "https://script.google.com/macros/s/AKfycbylaa4SdWhJmYsWOz1jnqWWyqu6QfFpCRsS6e5tDAdwDWAqW5DB9M-4IIHFwqO1bwia/exec"
        response = requests.get(url)
        data = response.json()
    except:
        data = ["Error loading data"]

    return render_template("dashboard.html", data=data)
app.secret_key = "secret123"
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("file")

    if file and file.filename != "":
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        return "File uploaded successfully!"

    return "No file selected"

@app.route("/", methods=["GET", "POST"])
def home():
    msg = ""
    translated_text = ""

    if request.method == "POST":

        # 🤖 AI TRANSLATOR
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

        # 📩 CONTACT FORM → GOOGLE SHEET
        if request.form.get("name"):
            data = {
                "name": request.form["name"],
                "email": request.form["email"],
                "phone": request.form["phone"],
                "message": request.form["message"]
            }

            try:
                requests.post("https://script.google.com/macros/s/AKfycbylaa4SdWhJmYsWOz1jnqWWyqu6QfFpCRsS6e5tDAdwDWAqW5DB9M-4IIHFwqO1bwia/exec", json=data)
                msg = "Data saved successfully!"
            except:
                msg = "Error saving data"

    return render_template("index.html", message=msg, translated=translated_text)

# 🔐 LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == "admin" and request.form["password"] == "1234":
            session["admin"] = True
            return redirect("/admin")
    return render_template("login.html")


# 📊 ADMIN (simple placeholder now)
@app.route("/admin")
def admin():
    if not session.get("admin"):
        return redirect("/login")
    return "<h2>Admin Panel (Data in Google Sheets)</h2>"


if __name__ == "__main__":
    app.run(debug=True)
