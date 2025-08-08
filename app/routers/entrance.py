from flask import redirect, url_for, render_template, Blueprint, request, flash
from flask_login import login_required, current_user

from .. import app
from ..database.models import User, Session, select
from .auth import ph, Login, login_user


@app.get("/login_page")
def login():
    return render_template("autorization.html")





@app.post("/login_to_profile")   
def authorization_profile():
    name = request.form.get("username")   
    password = request.form.get("password")
     
    
    with Session() as db_session:
        check_user = db_session.scalar(select(User).where(User.name == name))
        
        if not check_user:
            flash("Пользователь не найден", "error")
            return redirect(url_for('login'))   
        
        try:
             
            if ph.verify(check_user.password, password):
                # Создаем объект для Flask-Login
                login_user_obj = Login(id=check_user.id, name=check_user.name,role=check_user.role)
                login_user(login_user_obj)
                 
                return redirect(url_for('profile'))
            else:
                flash("Неверный пароль", "error")
                return redirect(url_for('login'))
        
        except Exception as e:
            flash(f"Ошибка авторизации: {str(e)}", "error")
            return redirect(url_for('login'))

 