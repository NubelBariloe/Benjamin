from flask import Flask, render_template, redirect, url_for, session
import json
from smtplib import SMTP_SSL
from email.message import EmailMessage
from random import randint
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
import requests
from wtforms import StringField, PasswordField, SubmitField, SelectField, form
from wtforms.validators import DataRequired, Email, EqualTo, Length



app = Flask(__name__, template_folder='html')
app.secret_key = "ben"
Bootstrap5(app)


class RegistrationForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    number = StringField("Phone Number", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    course = SelectField(choices=([('Data Analysis', 'Data Analysis'), ('front-end development', 'Front-end Development')]), validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Login")


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/home.html')
def back():
    return render_template('home.html')

@app.route('/service.html')
def service():
    return render_template('service.html')

@app.route('/courses.html')
def courses():
    return render_template('courses.html')

@app.route('/about.html')
def about():
    return render_template('about.html')

@app.route('/contacts.html', methods=['GET', 'POST'])
def contact():
    passwords = "gxue dors rfbw fsdi"
    my_email = "nubelbariloe133@gmail.com"
    regnum = randint(11111, 99999)
    form = RegistrationForm()
    if form.validate_on_submit():
        email =form.email.data
        course = form.course.data
        number = form.number.data
        password = form.password.data
        name = form.name.data


        body = f"""
        Thank you for registering for the {course} course at Nubels Digital Academy.
        your registration number is {regnum}
        We're delighted to have you join us and look forward to supporting you throughout your learning journey. Get ready to learn, develop new skills, and make the most of your training experience.

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


        with SMTP_SSL("smtp.gmail.com", 465, timeout=30) as connection:
            connection.login(my_email, passwords)
            connection.send_message(email_msg)

            try:
                with open("ben.json", "r") as file:
                    data = json.load(file)
            except (FileNotFoundError, json.JSONDecodeError):
                data = []

            student = {
                "name": name,
                "course": course,
                "number": number,
                "email": email,
                "registration": regnum,
                "password": password
            }

            data.append(student)

            with open("ben.json", "w") as file:
                json.dump(data, file, indent=4)

            return render_template("home.html")

    return render_template("contacts.html", form=form)


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

@app.route('/Logg.html', methods=['GET', 'POST'])
def logg():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data


        with open("ben.json", "r") as file:
            data = json.load(file)
            for account in data:
                if account["email"].strip().lower() == email.strip().lower() and account["password"] == password:
                    session["name"] = account.get("name")
                    return redirect(url_for("user"))
                elif email == "nubelbariloe01@gmail.com" and password == "admin":
                    session["name"] = "Admin"
                    return redirect(url_for("admin"))

            message = "Wrong email or password"
            return render_template("Logg.html", form=form, message=message)
    return render_template("Logg.html", form=form)

@app.route('/user.html', methods=['GET', 'POST'])
def user():
    if "name" not in session:
        return redirect(url_for("logg"))


    class ResultForm(FlaskForm):
        name = StringField("Name", validators=[DataRequired()])
        regnum = StringField("Registration Number", validators=[DataRequired()])
        submit = SubmitField("Check My Result")

    form = ResultForm()

    name = ""
    student = None
    if form.validate_on_submit():
        name = form.name.data
        regnum = form.regnum.data

    with open("ben.json", "r") as file:
        data = json.load(file)


    for account in data:
        if account["name"] == name and account["registration"] == int(regnum):
            student = {
                "name": account["name"],
                "email": account["email"],
                "score": account["score"],
                "course": account["course"],
                "number": account["number"],
                "password": account["password"]
        }

    return render_template("user.html", form=form, name=session["name"], student=student)



    return render_template("user.html", form=form, name=session["name"])


@app.route('/admin.html', methods=['GET', 'POST'])
def admin():
    if "name" not in session:
        return redirect(url_for("logg"))

    class ResultForm(FlaskForm):
        reg = StringField("Registration Number", validators=[DataRequired()])
        score = StringField("Score", validators=[DataRequired()])
        submit = SubmitField("Update Result")

    form = ResultForm()

    if form.validate_on_submit():
        reg = form.reg.data
        score = form.score.data

        with open("ben.json", "r") as file:
            data = json.load(file)

        found = False

        for account in data:
            if account["registration"] == int(reg):
                account["score"] = score
                found = True
                break

        if found:
            with open("ben.json", "w") as file:
                json.dump(data, file, indent=4)
                message = "score added successfully"
                return redirect(url_for("admin", message=message))
        else:
            messg = "Registration number not found"
            return render_template("admin.html", form=form, message=messg)
    with open("ben.json", "r") as file:
        data = json.load(file)
    return render_template("admin.html", form=form, name=session["name"], students=data)




if __name__ == '__main__':
    app.run(debug=True)
