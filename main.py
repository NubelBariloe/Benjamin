from flask import Flask, render_template, redirect, url_for, session
from smtplib import SMTP_SSL
import os
from email.message import EmailMessage
from random import randint

from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy

from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


# =========================================================
# DATABASE SETUP
# =========================================================

class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


# =========================================================
# CREATE FLASK APP
# =========================================================

app = Flask(__name__, template_folder="html")

# Secret key
app.secret_key = os.environ.get("SECRET_KEY", "ben")

# Bootstrap
Bootstrap5(app)


# =========================================================
# DATABASE CONFIGURATION
# =========================================================

# Vercel:
#     DATABASE_URL should contain your PostgreSQL connection string.
#
# Local computer:
#     If DATABASE_URL does not exist, SQLite will be used.

database_url = os.environ.get("DATABASE_URL")

if database_url:
    # Some PostgreSQL providers may return postgres://
    # SQLAlchemy expects postgresql://
    if database_url.startswith("postgres://"):
        database_url = database_url.replace(
            "postgres://",
            "postgresql://",
            1
        )

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url

else:
    # Local development only
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///school.db"


app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize SQLAlchemy
db.init_app(app)


# =========================================================
# DATABASE MODEL
# =========================================================

class User(db.Model):
    registration: Mapped[int] = mapped_column(primary_key=True)

    email: Mapped[str]
    name: Mapped[str]
    phone: Mapped[str]
    password: Mapped[str]
    course: Mapped[str]

    username: Mapped[str] = mapped_column(unique=True)

    score: Mapped[str | None] = mapped_column(
        nullable=True
    )


# =========================================================
# CREATE DATABASE TABLES
# =========================================================

# This is useful for your current project.
# The database itself must be persistent in production.
with app.app_context():
    db.create_all()


# =========================================================
# REGISTRATION FORM
# =========================================================

class RegistrationForm(FlaskForm):

    name = StringField(
        "Name",
        validators=[DataRequired()]
    )

    number = StringField(
        "Phone Number",
        validators=[DataRequired()]
    )

    email = StringField(
        "Email",
        validators=[
            DataRequired(),
            Email()
        ]
    )

    username = StringField(
        "Username",
        validators=[DataRequired()]
    )

    course = SelectField(
        "Course",
        choices=[
            ("Data Analysis", "Data Analysis"),
            ("full-stack development", "Full-Stack Development"),
            ("project management", "Project Management"),
            ("robotics", "Robotics"),
            ("Web development", "Web Development"),
            ("cybersecurity", "Cybersecurity")
        ],
        validators=[DataRequired()]
    )

    password = PasswordField(
        "Password",
        validators=[DataRequired()]
    )

    confirm = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(),
            EqualTo("password")
        ]
    )

    submit = SubmitField("Register")


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/home.html")
def back():
    return render_template("home.html")


# =========================================================
# SERVICES
# =========================================================

@app.route("/service.html")
def service():
    return render_template("service.html")


# =========================================================
# COURSES
# =========================================================

@app.route("/courses.html")
def courses():
    return render_template("courses.html")


# =========================================================
# ABOUT
# =========================================================

@app.route("/about.html")
def about():
    return render_template("about.html")


# =========================================================
# REGISTRATION / CONTACT
# =========================================================

@app.route("/contacts.html", methods=["GET", "POST"])
def contact():

    form = RegistrationForm()

    if form.validate_on_submit():

        email = form.email.data
        course = form.course.data
        number = form.number.data
        password = form.password.data
        name = form.name.data
        username = form.username.data

        # -------------------------------------------------
        # CHECK IF USERNAME ALREADY EXISTS
        # -------------------------------------------------

        existing_user = User.query.filter_by(
            username=username
        ).first()

        if existing_user:

            message = "Username already exists."

            return render_template(
                "contacts.html",
                form=form,
                message=message
            )


        # -------------------------------------------------
        # GENERATE REGISTRATION NUMBER
        # -------------------------------------------------

        regnum = randint(11111, 99999)

        # Make sure registration number is unique
        while User.query.filter_by(
            registration=regnum
        ).first():

            regnum = randint(11111, 99999)


        # -------------------------------------------------
        # CREATE USER
        # -------------------------------------------------

        student = User(
            email=email,
            registration=regnum,
            name=name,
            password=password,
            course=course,
            username=username,
            phone=number
        )


        # -------------------------------------------------
        # SAVE USER TO DATABASE
        # -------------------------------------------------

        try:

            db.session.add(student)
            db.session.commit()

        except Exception as error:

            db.session.rollback()

            print("DATABASE ERROR:", error)

            message = (
                "Registration could not be completed. "
                "Please try again."
            )

            return render_template(
                "contacts.html",
                form=form,
                message=message
            )


        # -------------------------------------------------
        # SEND REGISTRATION EMAIL
        # -------------------------------------------------

        my_email = os.environ.get("MAIL_USERNAME")
        mail_password = os.environ.get("MAIL_PASSWORD")


        if my_email and mail_password:

            body = f"""
Thank you for registering for the {course} course
at Nubels Digital Academy.

Your registration number is: {regnum}

We're delighted to have you join us and look forward
to supporting you throughout your learning journey.

Get ready to learn, develop new skills, and make the
most of your training experience.

Thank you for choosing Nubels Digital Academy.

Welcome aboard! 🚀

Best regards,
Nubels Digital Academy
"""


            email_msg = EmailMessage()

            email_msg["Subject"] = "Registration Confirmation"
            email_msg["From"] = my_email
            email_msg["To"] = email

            email_msg.set_content(body)


            try:

                with SMTP_SSL(
                    "smtp.gmail.com",
                    465,
                    timeout=30
                ) as connection:

                    connection.login(
                        my_email,
                        mail_password
                    )

                    connection.send_message(
                        email_msg
                    )

            except Exception as error:

                # Don't delete the student's registration
                # just because the email failed.
                print("EMAIL ERROR:", error)


        # -------------------------------------------------
        # REGISTRATION SUCCESS
        # -------------------------------------------------

        return render_template(
            "home.html",
            message=(
                "Registration successful! "
                f"Your registration number is {regnum}."
            )
        )


    return render_template(
        "contacts.html",
        form=form
    )


# =========================================================
# LOGIN FORM
# =========================================================

class LoginForm(FlaskForm):

    email = StringField(
        "Email",
        validators=[
            DataRequired(),
            Email()
        ]
    )

    password = PasswordField(
        "Password",
        validators=[DataRequired()]
    )

    submit = SubmitField("Login")


# =========================================================
# LOGIN
# =========================================================

@app.route("/Logg.html", methods=["GET", "POST"])
def logg():

    form = LoginForm()

    if form.validate_on_submit():

        email = form.email.data
        password = form.password.data


        # -------------------------------------------------
        # ADMIN LOGIN
        # -------------------------------------------------

        admin_email = os.environ.get(
            "ADMIN_EMAIL",
            "nubelbariloe01@gmail.com"
        )

        admin_password = os.environ.get(
            "ADMIN_PASSWORD",
            "admin"
        )


        if (
            email == admin_email
            and password == admin_password
        ):

            session["name"] = "Admin"

            return redirect(
                url_for("admin")
            )


        # -------------------------------------------------
        # STUDENT LOGIN
        # -------------------------------------------------

        user = User.query.filter_by(
            email=email,
            password=password
        ).first()


        if user:

            session["name"] = user.name

            return redirect(
                url_for("user")
            )


        # -------------------------------------------------
        # WRONG LOGIN
        # -------------------------------------------------

        message = "Wrong email or password."

        return render_template(
            "Logg.html",
            form=form,
            message=message
        )


    return render_template(
        "Logg.html",
        form=form
    )


# =========================================================
# STUDENT PAGE
# =========================================================

@app.route("/user.html", methods=["GET", "POST"])
def user():

    if "name" not in session:

        return redirect(
            url_for("logg")
        )


    names = session.get("name")


    class ResultForm(FlaskForm):

        name = StringField(
            "Name",
            validators=[DataRequired()]
        )

        regnum = StringField(
            "Registration Number",
            validators=[DataRequired()]
        )

        submit = SubmitField(
            "Check My Result"
        )


    form = ResultForm()


    if form.validate_on_submit():

        regnum = form.regnum.data
        name = form.name.data


        student = User.query.filter_by(
            registration=regnum,
            name=name
        ).first()


        return render_template(
            "user.html",
            form=form,
            name=session["name"],
            student=student
        )


    return render_template(
        "user.html",
        form=form,
        name=names,
        student=None
    )


# =========================================================
# ADMIN PAGE
# =========================================================

@app.route("/admin.html", methods=["GET", "POST"])
def admin():

    if "name" not in session:

        return redirect(
            url_for("logg")
        )


    class ResultForm(FlaskForm):

        reg = StringField(
            "Registration Number",
            validators=[DataRequired()]
        )

        score = StringField(
            "Score",
            validators=[DataRequired()]
        )

        submit = SubmitField(
            "Update Result"
        )


    form = ResultForm()


    if form.validate_on_submit():

        reg = form.reg.data
        score = form.score.data


        student = User.query.filter_by(
            registration=reg
        ).first()


        if student:

            student.score = score

            try:

                db.session.commit()

            except Exception as error:

                db.session.rollback()

                print(
                    "RESULT UPDATE ERROR:",
                    error
                )


    students = User.query.all()


    return render_template(
        "admin.html",
        form=form,
        name=session["name"],
        students=students
    )


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )
