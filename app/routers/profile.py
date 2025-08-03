from flask import redirect, url_for, render_template, request, flash
from flask_login import login_required, current_user, logout_user

from werkzeug.utils import secure_filename # для удаления опасных символов
from argon2.exceptions import VerifyMismatchError

import magic # проверка майм типа
import base64

from .. import app
from ..database.models import Session,select, User, Coment
from .auth import ph

ALLOWED_MIME_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']

@app.get("/profile_page")
@login_required
def profile():
    user_id = request.args.get("user_id", default = current_user.id, type=int)
    with Session() as db_session:
        user = db_session.scalar(select(User).where(User.id == user_id))
        coments = db_session.scalars(select(Coment)).unique().all()

        is_own_profile = (user_id == current_user.id)

    return render_template("profile.html", user = user, coments = coments, is_own_profile = is_own_profile )


@app.post("/exit")
def exit_profile():
    logout_user()
    return redirect(url_for('home_page'))


@app.post("/update_photo")
@login_required
def update_photo():
    file = request.files["photo"]

    #1 проверка майм типа чтоб пидарас не хакнул меня черех фото пошел он нахуй выблядок

    mime = magic.Magic(mime = True)
    file_mime = mime.from_buffer(file.stream.read(1024)) 
    file.stream.seek(0)

    if file_mime not in ALLOWED_MIME_TYPES:
        flash("Неверный формат файла! только = 'image/jpeg', 'image/webp',  'image/png', 'image/gif'", "error")
        return redirect(url_for('profile'))
    

    #2 Очитска имени файла от хакерства а то уебок еще и может хуйню вставить и пиздец
    secure_filename(file.filename)

    #3 сохраняем в бд
    with Session.begin() as db_session:
        users = db_session.scalar(select(User).where(User.id == current_user.id))
        users.uploaded_photo = base64.b64encode(file.read()).decode("utf-8")
    
    return redirect(url_for('profile'))

@app.get("/update_profile_page")
@login_required
def update_page_profile():
    return render_template("update_profiile_page.html")



@app.post("/update_new_profie")
@login_required
def save_new_profile():
    new_username = request.form.get("new_name")
    password = request.form.get("password")
    new_password = request.form.get("new_password")

    try:
        with Session.begin() as db_session:
            user = db_session.scalar(select(User).where(User.id == current_user.id))

            try:
                if not ph.verify(user.password, password):
                    flash("Неверный текущий пароль", "error")
                    return redirect(url_for('update_page_profile'))
            except VerifyMismatchError:
                flash("Неверный текущий пароль", "error")
                return redirect(url_for('update_page_profile'))
            except Exception as e:
                flash("Ошибка при проверке пароля", "error")
                return redirect(url_for('update_page_profile'))

            if new_password:
                if len(new_password) < 6:
                    flash("Пароль должен содержать минимум 6 символов", "error")
                    return redirect(url_for('update_page_profile'))
                if not any(char.isupper() for char in new_password):
                    flash("Пароль должен содержать хотя бы одну заглавную букву", "error")
                    return redirect(url_for('update_page_profile'))
                if not any(char in '!@#$%^&*()_+-=[]{};:,.<>?/' for char in new_password):
                    flash("Пароль должен содержать хотя бы один спецсимвол", "error")
                    return redirect(url_for('update_page_profile'))

                try:
                    hash_password = ph.hash(new_password)
                    user.password = hash_password
                    flash("Пароль успешно изменен", "success")
                except Exception as e:
                    flash("Ошибка при хешировании пароля", "error")
                    return redirect(url_for('update_page_profile'))

            if new_username:
                user.name = new_username
                flash("Имя пользователя успешно изменено", "success")

    except Exception as e:
        flash("Произошла ошибка при обновлении профиля", "error")
        return redirect(url_for('update_page_profile'))

    return redirect(url_for('profile'))

 

         
