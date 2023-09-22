from flask import Flask, render_template, url_for, redirect, request, abort, flash
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Flask_Key'

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


##CREATE DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy()
db.init_app(app)


##CREATE TABLE
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)


# User table for all your registered users
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)


with app.app_context():
    db.create_all()


# Create an admin-only decorator
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If id is not 1 then return abort with 403 error
        try:
            if current_user.id != 1:
                return abort(403)
        except AttributeError:
            return abort(403)
        # Otherwise continue with the route function
        return f(*args, **kwargs)

    return decorated_function


# Create an registered-user-only decorator
def registered_user_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If user is authenticated then return abort with 403 error
        if not current_user.is_authenticated:
            return abort(403)
        # Otherwise continue with the route function
        return f(*args, **kwargs)

    return decorated_function


# Create an unregistered-user-only decorator
def unregistered_user_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If user is not authenticated then return abort with 403 error
        if current_user.is_authenticated:
            return abort(403)
        # Otherwise continue with the route function
        return f(*args, **kwargs)

    return decorated_function


@app.route('/')
def home():
    result = db.session.execute(db.select(Cafe))
    cafes = result.scalars().all()
    return render_template("index.html", all_cafes=cafes, current_user=current_user)


@app.route("/login", methods=["GET", "POST"])
@unregistered_user_only
def login():
    if request.method == "POST":
        login_data = request.form
        result = db.session.execute(db.select(User).where(User.email == login_data["email"]))
        user = result.scalar()
        # Email doesn't exist
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        # Password incorrect
        elif not check_password_hash(user.password, login_data["password"]):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('home'))
    return render_template("login.html", current_user=current_user)


@app.route('/logout')
@registered_user_only
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/register", methods=["GET", "POST"])
@unregistered_user_only
def register():
    if request.method == "POST":
        data = request.form
        # Check if user email is already present in the database.
        result = db.session.execute(db.select(User).where(User.email == data["email"]))
        user = result.scalar()
        if user:
            # User already exists
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

        #Securing the password
        hash_and_salted_password = generate_password_hash(
            data["password"],
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            email=data["email"],
            name=data["name"],
            password=hash_and_salted_password,
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("home"))
    return render_template("register.html", current_user=current_user)



@app.route("/cafe/<int:cafe_id>")
def show_cafe(cafe_id):
    requested_cafe = db.get_or_404(Cafe, cafe_id)
    return render_template("cafe.html", cafe=requested_cafe, current_user=current_user)


# Use a decorator so only an admin user can delete a post
@app.route("/delete/<int:cafe_id>")
@admin_only
def delete_post(cafe_id):
    post_to_delete = db.get_or_404(Cafe, cafe_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


# Use a decorator so only an registered user can create new posts
@app.route("/new-post", methods=["GET", "POST"])
@registered_user_only
def add_new_post():
    if request.method == "POST":
        post_data = request.form
        #Obsługa specyficznego formularza
        try:
            if post_data["has_toilet"] == "on":
                toilets = True
        except KeyError:
            toilets = False

        try:
            if post_data["has_wifi"] == "on":
                wifi = True
        except KeyError:
            wifi = False

        try:
            if post_data["has_sockets"] == "on":
                sockets = True
        except KeyError:
            sockets = False

        try:
            if post_data["can_take_calls"] == "on":
                calls = True
        except KeyError:
            calls = False

        new_post = Cafe(
            name=post_data["name"],
            map_url=post_data["map_url"],
            img_url=post_data["img_url"],
            location=post_data["location"],
            seats=post_data["seats"],
            has_toilet=toilets,
            has_wifi=wifi,
            has_sockets=sockets,
            can_take_calls=calls,
            coffee_price=post_data["coffee_price"],
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("make-post.html", current_user=current_user)


if __name__ == "__main__":
    app.run(debug=True)