from flask import Flask, render_template, url_for, redirect, request, abort
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)

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

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


# User table for all your registered users
class User(db.Model):
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
        if current_user.id != 1:
            return abort(403)
        # Otherwise continue with the route function
        return f(*args, **kwargs)

    return decorated_function



@app.route('/')
def home():
    result = db.session.execute(db.select(Cafe))
    cafes = result.scalars().all()
    return render_template("index.html", all_cafes=cafes)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        contact_data = request.form
        # contact_data["email"], contact_data["message"])
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    return render_template("register.html")

# Add a POST method to be able to post comments
@app.route("/cafe/<int:cafe_id>", methods=["GET", "POST"])
def show_cafe(cafe_id):
    requested_cafe = db.get_or_404(Cafe, cafe_id)
    # # Add the CommentForm to the route
    # comment_form = CommentForm()
    # # Only allow logged-in users to comment on posts
    # if comment_form.validate_on_submit():
    #     if not current_user.is_authenticated:
    #         flash("You need to login or register to comment.")
    #         return redirect(url_for("login"))
    #
    #     new_comment = Comment(
    #         text=comment_form.comment_text.data,
    #         comment_author=current_user,
    #         parent_post=requested_post
    #     )
    #     db.session.add(new_comment)
    #     db.session.commit()
    return render_template("cafe.html", cafe=requested_cafe)#, current_user=current_user, form=comment_form)



if __name__ == "__main__":
    app.run(debug=True)