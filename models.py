from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash

# Настройки соединения сделаем позже в модуле приложения
db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    mail = db.Column(db.String, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    orders = db.relationship("Order", back_populates="user")

    @property
    def password(self):
        # Запретим прямое обращение к паролю
        raise AttributeError("Вам не нужно знать пароль!")

    @password.setter
    def password(self, password):
        # Устанавливаем пароль через этот метод
        self.password_hash = generate_password_hash(password)

    def password_valid(self, password):
        # Проверяем пароль через этот метод
        # Функция check_password_hash превращает password в хеш и сравнивает с хранимым
        return check_password_hash(self.password_hash, password)


meals_categories_association = db.Table('meals_categories',
                                        db.Column('meal_id', db.Integer, db.ForeignKey('meals.id')),
                                        db.Column('category_id', db.Integer, db.ForeignKey('categories.id'))
                                        )


class Meal(db.Model):
    __tablename__ = 'meals'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String)
    picture = db.Column(db.String)
    categories = db.relationship('Category', secondary=meals_categories_association, back_populates='meals')


class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    meals = db.relationship('Meal', secondary=meals_categories_association, back_populates='categories')


class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime(timezone=True), server_default=func.now())
    sum = db.Column(db.Float, nullable=False)
    status = db.Column(db.String, nullable=False)
    mail = db.Column(db.String)
    phone = db.Column(db.String, nullable=False)
    address = db.Column(db.String)
    meals = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship("User", back_populates="orders")
