from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, URL, Email, Length, EqualTo
from flask_ckeditor import CKEditorField


##WTForm


class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


class RegisterForm(FlaskForm):
    name = StringField(label="username", validators=[DataRequired(),
                                                     Length(min=1, max=20, message="Name too long max 20 characters")])
    email = StringField(label="email", validators=[DataRequired(), Email(message="Please enter a valid email address")])
    password = PasswordField(label="Password", validators=[Length(min=8, message="Too short")])
    confirm = PasswordField(label="Confirm password", validators=[EqualTo("password", message="password mismatch")])
    register = SubmitField(label="Register")


class LoginForm(FlaskForm):
    email = StringField(label="email", validators=[DataRequired(), Email(message="Please enter a valid email address")])
    password = PasswordField(label="password", validators=[Length(min=8, message="Too short")])
    submit = SubmitField(label="Login")


class CommentForm(FlaskForm):
    comment = CKEditorField(label="Comment", validators=[DataRequired()])
    submit = SubmitField("Submit comment")
