import random
import json
from flask import Flask, render_template, redirect, session, request
from flask_migrate import Migrate
from config import Config
from models import db, User, Meal, Category, Order
from forms import OrderForm
from authorization.views import authorization
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

app = Flask(__name__)
app.register_blueprint(authorization, url_prefix="/")
app.config.from_object(Config)
# Настраиваем соединение
db.init_app(app)

# Создаем объект поддержки миграций
migrate = Migrate(app, db)
admin = Admin(app)
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Order, db.session))
admin.add_view(ModelView(Category, db.session))
admin.add_view(ModelView(Meal, db.session))


@app.route('/')
def main_route():
    cats = random.sample(db.session.query(Category).all(), 4)
    is_auth = session.get("user_id", "")
    cat_meals = []
    for cat in cats:
        cat_meal = dict()
        cat_meal['meals'] = random.sample(db.session.query(Meal).filter(Meal.categories.any(id=cat.id)).all(), 3)
        cat_meal['cat'] = cat.title
        cat_meals.append(cat_meal)
    meals = []
    if is_auth:
        my_cart = session.get("cart", [])
        for id in my_cart:
            meal = db.session.query(Meal).get_or_404(int(id))
            meals.append(meal)
    return render_template("main.html", cat_meals=cat_meals, is_auth=is_auth, meals=meals)


@app.route('/addtocart/<id>/')
def addtocart(id):
    my_cart = session.get("cart", [])
    my_cart.append(int(id))
    session["cart"] = my_cart
    session["del_flag"] = False
    return redirect('/cart/')


@app.route('/del/<id>/')
def delete(id):
    my_cart = session.get("cart", [])
    print(my_cart)
    if int(id) in my_cart:
        my_cart.remove(int(id))
    session["cart"] = my_cart
    session["del_flag"] = True
    return redirect('/cart/')


@app.route('/cart/', methods=["GET", "POST"])
def cart():
    my_cart = session.get("cart", [])
    is_auth = session.get("user_id", "")
    meals = []
    form_errors = []
    del_flag = session.get("del_flag", False)
    for id in my_cart:
        meal = db.session.query(Meal).get_or_404(int(id))
        meals.append(meal)
    form = OrderForm(order_sum=sum([meal.price for meal in meals]), order_cart=my_cart)
    if request.method == "POST":
        name = form.name.data
        address = form.address.data
        mail = form.mail.data
        phone = form.phone.data
        order_sum = form.order_sum.data
        order_cart = form.order_cart.data
        if len(order_cart) == 2:
            form_errors.append("Корзина пуста")
            return render_template("cart.html", meals=meals, form=form, is_auth=is_auth, del_flag=del_flag,
                                   form_errors=form_errors)
        if mail != session["mail"]:
            form_errors.append("email не совпадает с email входа")
            return render_template("cart.html", meals=meals, form=form, is_auth=is_auth, del_flag=del_flag,
                                   form_errors=form_errors)
        user = db.session.query(User).filter(User.mail == mail).first()
        if user:
            order = Order(user=user, address=address, mail=mail, phone=phone,
                          sum=order_sum, meals=json.dumps(order_cart), status="Отправлен")
            db.session.add(order)
            db.session.commit()
            session["cart"] = []
            return redirect("/ordered/")
        else:
            form_errors.append("Email введен неверно")
            return render_template("cart.html", meals=meals, form=form, is_auth=is_auth, del_flag=del_flag,
                                   form_errors=form_errors)
    return render_template("cart.html", meals=meals, form=form, is_auth=is_auth, del_flag=del_flag,
                           form_errors=form_errors)


@app.route('/account/')
def account():
    mail = session.get("mail", "")
    user_id = session.get("user_id", "")
    orders = db.session.query(Order).order_by(Order.date.desc()).filter(Order.user_id == user_id).limit(5).all()
    my_cart = session.get("cart", [])
    meals = []
    orders_dict = []
    for id in my_cart:
        meal = db.session.query(Meal).get_or_404(int(id))
        meals.append(meal)
    for order in orders:
        meals_ids = json.loads(order.meals)
        meals_ids = meals_ids.strip('][').split(', ')
        all_meals = []
        for id in meals_ids:
            meal = db.session.query(Meal).get_or_404(int(id))
            all_meals.append(meal)
        orders_dict.append({"order": order, "all_meals": all_meals})
    return render_template("account.html", orders=orders_dict, mail=mail, meals=meals, is_auth=user_id)


@app.route('/ordered/')
def ordered():
    return render_template("ordered.html")


if __name__ == '__main__':
    app.run()
