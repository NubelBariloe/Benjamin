from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase,Mapped, mapped_column, Session

class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)

# create the app
app = Flask(__name__)
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
# initialize the app with the extension
db.init_app(app)



class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str]
    name: Mapped[str]
    phone: Mapped[str]
    password: Mapped[str]
    course: Mapped[str]
    registration: Mapped[str] = mapped_column(unique=True)

with app.app_context():
    db.create_all()
    db.session.add(User(email="nubelbariloe0@gmail.com", id=1, name="nubelbariloe0",
                         password="123", course="robotics", registration="nubelbariloe0",
                        phone="09078243611"))
    db.session.commit()

    all_books = db.session.query(User).all()
    print(all_books)
