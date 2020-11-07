import pandas as pd
from models import db, Meal, Category
from app import app


def fill_data():
    categories = pd.read_csv("categories.csv", index_col=0)
    meals = pd.read_csv("meals.csv", index_col=0)
    for cat in categories.values:
        new_cat = Category(title=cat[0])
        db.session.add(new_cat)
    for meal in meals.values:
        new_meal = Meal(title=meal[0], price=meal[1], description=meal[2], picture=meal[3])
        cat = db.session.query(Category).filter(Category.id == meal[4]).first()
        new_meal.categories.append(cat)
        db.session.add(new_meal)
    db.session.commit()


with app.app_context():
    fill_data()
