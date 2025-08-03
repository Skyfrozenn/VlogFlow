from flask import redirect, url_for, render_template, request, flash, abort
from flask_login import login_required, current_user

from werkzeug.utils import secure_filename

from .. import app
from ..database.models import (
    Article, Category, Session,
      select, User, desc, func, Coment)

from .profile import ALLOWED_MIME_TYPES

import magic # проверка майм типа
import base64


@app.post("/save_new_article")
@login_required
def save_name_vlog():
    file = request.files.get("photo")
    title = request.form.get("title")
    description = request.form.get("description")
    category_name = request.form.get("category")
    category_name = category_name.capitalize()

    if not all([title, description, category_name]):   
        return "Заполни все поля, уёбище!", 400

    with Session.begin() as db_session:
        try:
            author = db_session.scalar(select(User).where(User.id == current_user.id))
            
            # если категория 1 то мы просто ее передаем как обьект, а если нет создаем и флюш чтобы в черновик ебануть
            category = None
            if category_name:
                category = db_session.scalar(select(Category).where(Category.name == category_name))
                if not category:
                    category = Category(name=category_name)
                    db_session.add(category)
                    db_session.flush()

            if file and file.filename:
                # чтобы пидарас не хакнул
                mime = magic.Magic(mime=True)
                file_mime = mime.from_buffer(file.stream.read(1024)) 
                file.stream.seek(0)

                if file_mime not in ALLOWED_MIME_TYPES:
                    return flash("Только JPG/PNG/GIF, дебил!","error"), 400

                # а это чтобы пидарас не вставил чет
                secure_filename(file.filename)
                avatar = base64.b64encode(file.read()).decode("utf-8")
                
                new_vlogs = Article(
                    title=title,
                    avatar=avatar,
                    description=description,
                    author=author,
                    category=category
                )
            else:
                new_vlogs = Article(
                    title=title,
                    avatar=None,
                    description=description,
                    author=author,
                    category=category
                )
            
            db_session.add(new_vlogs)
            return redirect(url_for('profile'))

        except Exception as e:
            db_session.rollback()
            return f"Ошибка: {str(e)}", 500

            
# добавить коммент
@app.post("/add_coment")
@login_required
def add_coment():
    user_id = request.form.get("user_id")
    article_id = request.form.get("article_id")
    text = request.form.get("text")

    with Session.begin() as db_session:
        new_coment = Coment(text = text, user_id = user_id, article_id = article_id)
        db_session.add(new_coment)

    return redirect(url_for('profile'))
    
 


@app.post("/delete_coment")
@login_required
def del_com():
    coment_id = request.form.get("comment_id")

    with Session.begin() as db_session:
        coment = db_session.scalar(select(Coment).where(Coment.id == coment_id))
        if current_user.id == coment.user_id:
            db_session.delete(coment)
            return redirect(url_for('profile'))
        else:
            abort(403)
            



@app.post("/delete_vlog")
@login_required
def del_vlog():
    vlog_id = request.form.get("vlog_id")
    with Session.begin() as db_session:
        #наш обьект удаления 
        vlog = db_session.scalar(select(Article).where(Article.id == vlog_id))

        #айли категории статьи которая будет удалена
        category_id = vlog.category.id

        #удаляем
        db_session.delete(vlog)
         
         

        #считаем количество категории в статьях
        category_vlogs = db_session.scalar(select(func.count(Article.id)).where(Category.id == category_id))

        # если после удаления нет связанных обьектов с этой категории удаляем категорию
        if category_vlogs == 0:
            category = db_session.scalar(select(Category).where(Category.id == category_id))
            db_session.delete(category)

        
    return redirect(url_for('profile'))



        

    


    




