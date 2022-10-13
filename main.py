from flask import Flask, request, render_template, url_for, redirect
from flask_login import *
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from forms import NoteForm, CopyForm, LoginForm, RegisterForm
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import config
import os

# ===== Flask application, connect with database, login manager =====
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')  # local -> config.DB_SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL1') # local -> 'sqlite:///SNdb.sqlite3'
Bootstrap(app)

db = SQLAlchemy(app)

# ===== Login set up =====

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(100))
    password = db.Column(db.String(100))
    notes = db.relationship('Notes', backref='users')


login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)


# ====== SQLAlchemy class model =====
class Notes(db.Model):
    id = db.Column('note_id', db.Integer, primary_key=True)
    title = db.Column(db.String(30))
    content = db.Column(db.String(300))
    url = db.Column(db.String(6))
    recipient = db.Column(db.String(30))
    user_id = db.Column(db.ForeignKey('users.id'))


db.create_all()
#
# new_user = Users(
#     login='pawel',
#     password='pawel',
# )
# db.session.add(new_user)
# db.session.commit()


# ===== MAIN PAGE - SEND A MESSAGE =====
@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        url = secrets.token_urlsafe(6)

        new_note = Notes(
            title=title,
            content=content,
            url=url,
        )
        db.session.add(new_note)
        db.session.commit()

        return redirect(url_for('url_path', url=url))

    return render_template('message.html', show_addressee=0)


# ===== READ A MESSAGE =====
@app.route('/<url>')
def note(url):

    note_in_db = Notes.query.filter_by(url=url).first()
    if note_in_db is not None:
        my_note = [note_in_db.title, note_in_db.content]
        db.session.delete(note_in_db)
        db.session.commit()
        return render_template('note.html', data=my_note)

    return render_template('note.html', data=None)


@app.route('/copy_url/<url>', methods=['GET', 'POST'])
def url_path(url):
    path = request.host_url + url
    # copy = CopyForm()
    # if copy.is_submitted():
    #     pyperclip.copy(path)
    return render_template('url_path.html', path=path, correctly_shipped=0)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        user_name = request.form['username']
        user_password = request.form['password']
        user = Users.query.filter_by(login=user_name).first()
        if user is not None and check_password_hash(user.password, user_password):
            login_user(user)
            return redirect(url_for('main'))

        else:
            error = 'Invalid username or password'
            return render_template('log.html', error=error)

    return render_template('log.html', error=None)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        user_name = request.form['username']
        user_password = request.form['password']
        print(Users.query.filter_by(login=user_name).all())
        if not Users.query.filter_by(login=user_name).all():
            new_user = Users(
                login=user_name,
                password=generate_password_hash(user_password),
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)

            return redirect(url_for('main'))

        else:
            error = 'User with this login already exists.'
            return render_template('register.html', error=error)

    return render_template('register.html', error=None)


@app.route('/direct_msg', methods=['GET', 'POST'])
@login_required
def direct_msg():

    if request.method == "POST":
        addressee = Users.query.filter_by(login=request.form["addressee"]).first()
        if addressee is not None:
            title = request.form["title"]
            content = request.form["content"]
            url = secrets.token_urlsafe(6)

            new_note = Notes(
                title=title,
                content=content,
                url=url,
                recipient=current_user.login,
                user_id=addressee.id
            )

            db.session.add(new_note)
            db.session.commit()

            return render_template('url_path.html', correctly_shipped=1)

        else:
            error = 'Addressee doesn\'t exist. Your message has not been sent.'
            return render_template('message.html', show_addressee=1, error=error)

    return render_template('message.html', show_addressee=1)


@app.route('/mailbox')
@login_required
def mailbox():
    messages = Notes.query.filter_by(user_id=current_user.id).all()
    return render_template('mailbox.html', messages=messages)


@app.route('/info')
def info():
    return render_template('info.html')


if __name__ == '__main__':
    app.run(debug=True)
