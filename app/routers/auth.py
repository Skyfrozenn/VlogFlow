from os import path
from flask import Blueprint, render_template, redirect, request, url_for, flash
from flask_login import UserMixin, LoginManager, login_user, current_user

from argon2 import PasswordHasher

from .. import app
from ..database.models import Session, User, select

DEFAULT_AVATAR = "images/guest.jpg"

login_manager = LoginManager() # главный файл 
login_manager.init_app(app)
login_manager.login_view = 'home_page'

ph = PasswordHasher(time_cost=3, memory_cost=66536, parallelism=4)


class Login(UserMixin):
    def __init__(self,id, name):
        self.id = id
        self.name = name
         
        

@login_manager.user_loader
def load_user(user_id):
    with Session() as db_session:
        user = db_session.scalar(select(User).where(User.id == user_id))
        if user:
            return Login(
                id=user.id,
                name=user.name
            )
    return None
        
@app.get("/")
def home_page():
    return render_template("home_page.html")


@app.post("/register")

def register():
    username = request.form.get("username")
    password = request.form.get("password")
    
    with Session.begin() as db_session:
        # Проверка существования пользователя
        if db_session.scalar(select(User).where(User.name == username)):
            flash("Юзер уже существует", "error")
            return redirect(url_for('home_page'))
        
        # Проверка пароля
        if len(password) < 6:
            flash("Слабый пароль! Нужно: 6+ символов", "error")
            return redirect(url_for('home_page'))
            
        if not any(c.isupper() for c in password):
            flash("Слабый пароль! Нужна хотя бы одна заглавная буква", "error")
            return redirect(url_for('home_page'))
            
        if all(c.isalnum() for c in password):
            flash("Слабый пароль! Нужен хотя бы один спецсимвол", "error")
            return redirect(url_for('home_page'))
        
        # Если все проверки пройдены
        hashed_password = ph.hash(password)
        new_user = User(
            name=username,
            photo=DEFAULT_AVATAR,
            password=hashed_password
        )
        db_session.add(new_user)
        db_session.flush()
        
        login_user_obj = Login(id=new_user.id, name=new_user.name)
        login_user(login_user_obj)
        
        
        return redirect(url_for('profile'))



            

        

    

    

