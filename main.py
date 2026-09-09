from flask import Flask, render_template, request
import json
from smtplib import SMTP_SSL
from email.message import EmailMessage
from random import randint

app = Flask(__name__, template_folder='html')

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
    password = "gxue dors rfbw fsdi"
    my_email = "nubelbariloe133@gmail.com"
    regnum = randint(111, 999)

    if request.method == "POST":
        email = request.form.get("email")
        name = request.form.get("name")
        course = request.form.get("course")
        number = request.form.get("number")

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
            connection.login(my_email, password)
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
            }

            data.append(student)

            with open("ben.json", "w") as file:
                json.dump(data, file, indent=4)

            return render_template("home.html")

    return render_template("contacts.html")

if __name__ == '__main__':
    app.run(debug=True)
