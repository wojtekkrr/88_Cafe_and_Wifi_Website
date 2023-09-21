from flask import Flask, render_template, url_for, redirect, request

app = Flask(__name__)


@app.route('/')
def home():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    if request.method == "POST":
        contact_data = request.form
        print(contact_data["demo-name"])
        # contact_data["email"], contact_data["message"])
        return redirect(url_for('home'))

@app.route("/register", methods=["POST"])
def register():
    return render_template("register.html")

if __name__ == "__main__":
    app.run(debug=True)