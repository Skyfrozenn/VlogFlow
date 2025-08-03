from sqlalchemy import create_engine, func, ForeignKey, select, desc
from sqlalchemy.orm import sessionmaker, mapped_column, Mapped, relationship, DeclarativeBase

from datetime import datetime

engine = create_engine("sqlite:///database.db", echo=True)
Session = sessionmaker(engine)

class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id : Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name:Mapped[str]
    photo : Mapped[str]
    uploaded_photo : Mapped[str] = mapped_column(nullable=True)
    password:Mapped[str]
    join : Mapped[datetime] = mapped_column(server_default=func.now()) # время когда юзер зарегался
    
    #связи
    articles : Mapped[list["Article"]] = relationship(
        back_populates = "author",
        lazy = "joined",
        cascade = "all, delete-orphan",  
        passive_deletes = True
    )
    coments : Mapped[list["Coment"]] = relationship(back_populates = "author", lazy = "joined")
         


class Category(Base):
    __tablename__ = "categories"

    id : Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]

    articles : Mapped[list["Article"]] = relationship(back_populates = "category", lazy = "joined", passive_deletes = True)






class Article(Base):
    __tablename__ = "articles"


    id:Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title : Mapped[str]
    avatar : Mapped[str] = mapped_column(nullable=True)
    description : Mapped[str]
    date_added : Mapped[datetime] = mapped_column(server_default = func.now())  

    #внешние ключи
    user_id : Mapped[int] = mapped_column(ForeignKey(User.id, ondelete = "CASCADE")) 
    category_id : Mapped[int] = mapped_column(ForeignKey(Category.id)) 

    
    #ебучие связи
    author : Mapped["User"] = relationship(back_populates = "articles", lazy = "joined")
    category : Mapped["Category"] = relationship(back_populates = "articles", lazy = "joined" )
    coments : Mapped[list["Coment"]] = relationship(back_populates = "articles", lazy = "joined", cascade="all, delete-orphan")




class Coment(Base):
    __tablename__ = "coments"
    id : Mapped[int] = mapped_column(primary_key=True, autoincrement = True )
    text : Mapped[str]

    user_id : Mapped[int] = mapped_column(ForeignKey(User.id, ondelete="CASCADE"))
    article_id : Mapped[int] = mapped_column(ForeignKey(Article.id, ondelete="CASCADE"))
    
    # связи
    articles : Mapped["Article"] = relationship(back_populates = "coments", lazy = "joined")
    author : Mapped["User"] = relationship(back_populates = "coments", lazy = "joined" )






#def up():
    #Base.metadata.create_all(engine)

#def drop():
    #Base.metadata.drop_all(engine)

#def migrate():
    #drop()
    #up()


