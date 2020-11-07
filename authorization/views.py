from flask import Blueprint, session, redirect, render_template, request
from forms import LoginForm, RegistrationForm
from models import db, User

authorization = Blueprint("authorization", __name__)


@authorization.route("/login/", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect("/")
    # Создаем форму
    form = LoginForm()
    if request.method == "POST":
        # Если форма не валидна
        if not form.validate_on_submit():
            # показываем форму и не забываем передать форму в шаблон
            return render_template("login.html", form=form)
        # Информацию о пользователе берем из базы по введенной почте
        user = db.session.query(User).filter(User.mail == form.username.data).first()
        # Теперь пароль проверяется методом password_valid
        if user and user.password_valid(form.password.data):
            session["user_id"] = user.id
            session["mail"] = user.mail
            return redirect("/account/")
        else:
            form.username.errors.append("Не верное имя или пароль")
            return render_template("login.html", form=form)
    return render_template("login.html", form=form)


@authorization.route('/register/', methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if request.method == "POST":
        if not form.validate_on_submit():
            return render_template("register.html", form=form, error_msg="")
        username = form.username.data
        password = form.password.data
        #  Проверяем, есть ли такой юзернейм в базе
        user = User.query.filter_by(mail=username).first()
        # Если такой пользователь существует
        if user:
            # Не можем зарегистрировать, так как пользователь уже существует
            error_msg = "Пользователь с указанным именем уже существует"
            return render_template("register.html", error_msg=error_msg, form=form)
        user = User(mail=username)
        user.password = password
        db.session.add(user)
        db.session.commit()
        session["user_id"] = user.id
        session["mail"] = user.mail
        return redirect("/account/")
    return render_template("register.html", form=form, error_msg="")


@authorization.route('/logout/')
def logout():
    if session.get("user_id"):
        session.pop("user_id")
    if session.get("mail"):
        session.pop("mail")
    if session.get("cart"):
        session.pop("cart")
    if session.get("del_flag"):
        session.pop("del_flag")
    return redirect("/login/")
