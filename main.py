from flask import Flask, render_template, request,redirect,url_for,flash
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from flask_login import UserMixin,login_user,login_required,current_user,logout_user,LoginManager


app = Flask(__name__)
bootstrap = Bootstrap5(app)
app.config["SECRET_KEY"]="heyitsme"

login_manager = LoginManager()
login_manager.init_app(app)


class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
app.config['SQLALCHEMY_DATABASE_URI']= "sqlite:///store.db"
db.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)

class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(),unique=True, nullable=False)
    email = db.Column(db.String(),unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)
    story =db.Column(db.String(200), nullable=True)

with app.app_context():
    db.create_all()

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        result = db.session.execute(db.Select(User).where(User.email==email)).scalar()
        if not result:
            flash('Login Unsuccessful. Please check email and password')
            return redirect(url_for('login'))
        elif not check_password_hash(result.password,password):
            flash('Wrong password.')
            return redirect(url_for('login'))
        else:
            login_user(result)
            return redirect(url_for('story'))
    return render_template('login.html',logged_in=current_user.is_authenticated)

@app.route('/home')
@login_required
def home():
    return render_template('home.html',logged_in=current_user.is_authenticated)

@app.route('/', methods=['GET','POST'])
def register():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        name = request.form['name']
        result = db.session.execute(db.Select(User).where(User.email==email)).scalar()
        if not result:
            hash_salted_password = generate_password_hash(password,method="pbkdf2:sha256",salt_length=8)
            new_user = User(name=name,email=email,password=hash_salted_password,story="")
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for("home"))
        else:
            flash('Your email has been register before')
            return redirect(url_for('register'))
    return render_template('register.html')

@app.route('/story', methods=['GET','POST'])
@login_required
def story():
    if request.method == "POST":
        story = request.form['story']
        return render_template('story.html',story=story,logged_in=True)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)