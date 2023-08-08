import os
from flask import Flask, render_template, redirect, url_for, flash, request, abort
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import CreatePostForm, RegisterForm, LoginForm, CommentForm
from flask_gravatar import Gravatar
from functools import wraps
import requests


""" QUOTE RESPONSE"""
RESPONSE = requests.get("https://zenquotes.io/api/random")
QUOTE_DATA = RESPONSE.json()

"""NEWS API RESPONSE"""
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")
NEWS_ENDPOINT = f" https://newsdata.io/api/1/news?apikey={NEWS_API_KEY}&country=be,fr,de,nl,gb&language=nl,en&category=technology"
tech_news_page_1 = requests.get(NEWS_ENDPOINT).json()
PAGE_2_ENDPOINT = f" https://newsdata.io/api/1/news?apikey={NEWS_API_KEY}&country=be,fr,de,nl,gb&language=nl,en&category=technology&page={tech_news_page_1['nextPage']}"
tech_news_page_2 = requests.get(PAGE_2_ENDPOINT).json()
PAGE_3_ENDPOINT = f" https://newsdata.io/api/1/news?apikey={NEWS_API_KEY}&country=be,fr,de,nl,gb&language=nl,en&category=technology&page={tech_news_page_2['nextPage']}"
tech_news_page_3 = requests.get(PAGE_3_ENDPOINT).json()
# PAGE_4_ENDPOINT = f" https://newsdata.io/api/1/news?apikey={NEWS_API_KEY}&country=be,fr,de,nl,gb&language=nl,en&category=technology&page={tech_news_page_3['nextPage']}"
# tech_news_page_4 = requests.get(PAGE_4_ENDPOINT).json()
# PAGE_5_ENDPOINT = f" https://newsdata.io/api/1/news?apikey={NEWS_API_KEY}&country=be,fr,de,nl,gb&language=nl,en&category=technology&page={tech_news_page_4['nextPage']}"
# tech_news_page_5 = requests.get(PAGE_5_ENDPOINT).json()

""" COPYRIGHT DATE"""
COPYRIGHT_DATE = date.today().strftime("%B %d, %Y")

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')
ckeditor = CKEditor(app)
Bootstrap5(app)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URI", "sqlite:///blog.db")
db = SQLAlchemy(app)


# Login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = "strong"


# initialize gravatar
gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None
                    )


# user loader callback
@login_manager.user_loader
def load_user(user_id):
    return User.query.get_or_404(user_id)


# Admin privileges
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.id != 1:
           return abort(403)
        return f(*args, **kwargs)
    return decorated_function


# CONFIGURE TABLES
class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    # This will act like a List of BlogPost objects attached to each User.
    # The "author" refers to the author property in the BlogPost class.
    posts = relationship("BlogPost", back_populates="author")
    # *******Add parent relationship*******#
    # "comment_author" refers to the comment_author property in the Comment class.
    comments = relationship("Comment", back_populates="comment_author")


class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    # Create a Foreign Key. "users.id" the users refers to the tablename of User
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    # Create reference to the User object, the "posts" refers to the posts property in the User class.
    author = relationship("User", back_populates="posts")

    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)

    # ***************Parent Relationship*************#
    comments = relationship("Comment", back_populates="parent_post")


class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    comment_author = relationship("User", back_populates="comments")

    # ***************Child Relationship*************#
    post_id = db.Column(db.Integer, db.ForeignKey("blog_posts.id"))
    parent_post = relationship("BlogPost", back_populates="comments")
    text = db.Column(db.String(500), nullable=False)


with app.app_context():
    db.create_all()


@app.route('/')
def get_all_posts():
    posts = BlogPost.query.all()
    return render_template("index.html", all_posts=posts, current_user=current_user, date=COPYRIGHT_DATE, data=QUOTE_DATA)


@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    error = None
    if form.validate_on_submit():
        new_user = User(
            name=form.name.data,
            email=form.email.data,
            password=generate_password_hash(form.password.data, method="pbkdf2:sha256:600000", salt_length=8)
        )
        #if User.query.get(User.email == form.email.data) == True:
          #  error = "That email already exists in our database please login"
           # return redirect(url_for("login", error=error))
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("get_all_posts"))
    return render_template("register.html", form=form, date=COPYRIGHT_DATE, current_user=current_user)


@app.route('/login', methods=["GET", "POST"])
def login():
    error = None
    if request.args.get("error"):
        error = request.args.get("error")
    form = LoginForm()
    if form.validate_on_submit():
        #user = db.session.execute(db.select(User).where(User.email == form.email.data)).scalar()
        user = User.query.filter_by(email=form.email.data).first()
        if not user:
            error = "User not found, please register"
        elif not check_password_hash(user.password, form.password.data):
            error = "Wrong password, please try again"
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for("get_all_posts"))
    return render_template("login.html", form=form, error=error, current_user=current_user, date=COPYRIGHT_DATE)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts', date=COPYRIGHT_DATE))


@login_required
@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    error = None
    form = CommentForm()
    requested_post = BlogPost.query.get(post_id)
    if not current_user and form.validate_on_submit():
        error = "Only authenticated users are allowed to leave comments, please login!"
        return redirect(url_for("login", error=error, logged_in=current_user, date=COPYRIGHT_DATE))
    if current_user and form.validate_on_submit():
        new_comment = Comment(
            text=form.comment.data,
            author_id=current_user.id,
            post_id=requested_post.id
        )
        db.session.add(new_comment)
        db.session.commit()
    return render_template("post.html", post=requested_post, current_user=current_user, form=form, date=COPYRIGHT_DATE)


@app.route("/about")
def about():
    return render_template("about.html", current_user=current_user, date=COPYRIGHT_DATE)


@app.route("/contact")
def contact():
    return render_template("contact.html", current_user=current_user, date=COPYRIGHT_DATE)


@login_required
@app.route("/new-post", methods=["GET", "POST"])
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form, current_user=current_user, date=COPYRIGHT_DATE)


@login_required
@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_only
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))

    return render_template("make-post.html", form=edit_form, logged_in=current_user, date=COPYRIGHT_DATE, is_edit=True)


@app.route("/delete/<int:post_id>")
@login_required
@admin_only
def delete_post(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts', current_user=current_user))


@app.route("/news/<int:page>")
def get_news(page):
    tech_news = tech_news_page_1
    if page == 2:
        tech_news = tech_news_page_2
    elif page == 3:
        tech_news = tech_news_page_3
    # elif page == 4:
    #     tech_news = tech_news_page_4
    # elif page == 5:
    #     tech_news = tech_news_page_5
    else:
         tech_news = tech_news_page_1
    return render_template("news.html", page1=tech_news, date=COPYRIGHT_DATE, num=page)



if __name__ == "__main__":
    app.run(debug=False)
