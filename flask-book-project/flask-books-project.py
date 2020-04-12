from flask import Flask, render_template, flash, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__) # type:Flask

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:password@127.0.0.1/flask_books'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'programmer'

db = SQLAlchemy(app)

class Author(db.Model):
    __tablename__ = 'authors'

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(16), unique = True)

    books = db.relationship('Book', backref='author')

    # def __repr__(self):
        # return ('Author: %s' % self.name)

class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(16), unique = False)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'))

    # def __repr__(self):
        # return ('Book: %s %s' % (self.name, self.author_id))

class AuthorForm(FlaskForm):
    author = StringField('作者：', validators=[DataRequired()])
    book = StringField('书籍：', validators=[DataRequired()])
    submit = SubmitField('提交')

@app.route('/delete_author/<author_id>')
def delete_author(author_id):
    author = Author.query.get(author_id)
    if author:
        try:
            Book.query.filter_by(author_id= author.id).delete()
            db.session.delete(author)
            db.session.commit()
        except Exception as e:
            print(e)
            flash('删除作者失败')
            db.session.rollback()
    else:
        flash('作者不存在')
    return redirect(url_for('index'))

@app.route('/delete_book/<book_id>')
def delete_book(book_id):
    book = Book.query.get(book_id)
    if book:
        try:
            db.session.delete(book)
            db.session.commit()
        except Exception as e:
            print(e)
            flash('删除书籍失败')
            db.session.rollback()
    else:
        flash('书籍不存在')
    return redirect(url_for('index'))

@app.route('/', methods=['GET', 'POST'])
def index():
    author_form = AuthorForm()

    #验证表单输入信息  
    if author_form.validate_on_submit():
        #读取表单信息
        author_name = author_form.author.data
        book_name = author_form.book.data
    
    # 1，先判断作者是否存在，不存在的创建新的作者
    # 2，作者若存在，判断书籍是否存在，若书籍存在则打印已存在，若不存在则添加书籍
    # 3，作者不存在，添加新作者，添加书籍
    
        author = Author.query.filter_by(name=author_name).first()
        if author:
            book = Book.query.filter(and_(Book.name==book_name, Book.author_id==author.id)).first()
            if book:
                flash('书籍已存在')
            else:
                try:
                    new_book = Book(name = book_name, author_id = author.id)
                    db.session.add(new_book)
                    db.session.commit()
                except Exception as e:
                    print(e)
                    flash('添加书籍失败')
                    db.session.rollback()
        else:
            try:
                new_author = Author(name = author_name)
                db.session.add(new_author)
                db.session.commit()
                new_book = Book(name = book_name, author_id = new_author.id)
                db.session.add(new_book)
                db.session.commit()
            except Exception as e:
                print(e)
                flash('添加作者和书籍失败')
                db.session.rollback()

    authors = Author.query.all()

    return render_template('books.html', authors = authors, form = author_form)

if __name__ == '__main__':

    db.drop_all()
    db.create_all()

    au1 = Author(name = u'张三')
    au2 = Author(name = u'李四')
    au3 = Author(name = u'王五')
    db.session.add_all([au1, au2, au3])
    db.session.commit()

    bk1 = Book(name = u'Java入门', author_id = au1.id)
    bk2 = Book(name = u'python入门', author_id = au1.id)
    bk3 = Book(name = u'c语言程序设计', author_id = au2.id)
    bk4 = Book(name = u'c++程序设计', author_id = au2.id)
    bk5 = Book(name = u'计算机组成原理', author_id = au3.id)
    db.session.add_all([bk1, bk2, bk3, bk4, bk5])
    db.session.commit()
    
    app.run(port=5000)