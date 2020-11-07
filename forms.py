import re
from flask_wtf import FlaskForm
from wtforms import StringField, HiddenField, PasswordField
from wtforms.validators import Length, InputRequired, DataRequired, ValidationError, EqualTo


class OrderForm(FlaskForm):
    name = StringField('clientName', [InputRequired(), Length(min=1, max=50)])
    address = StringField('clientAddress', [InputRequired(), Length(min=1, max=400)])
    mail = StringField('clientMail', [InputRequired(), Length(min=1, max=400)])
    phone = StringField('clientPhone', [InputRequired(), Length(min=5, max=20)])
    order_sum = HiddenField('clientOrderSum', [InputRequired()])
    order_cart = HiddenField('clientOrderCart', [InputRequired()])


# Форма аутентификации
class LoginForm(FlaskForm):
    # Добавляем поле имени пользователя
    username = StringField("Имя:", validators=[DataRequired()])
    # Добавляем поле пароля
    password = PasswordField("Пароль:", validators=[DataRequired()])


# Наша функция валидации принимает форму и проверяемое поле
def password_check(form, field):
    msg = "Пароль должен содержать латинские сивмолы в верхнем и нижнем регистре и цифры"
    patern1 = re.compile('[a-z]+')
    patern2 = re.compile('[A-Z]+')
    patern3 = re.compile('\\d+')
    # Проверяем данные поля
    if (not patern1.search(field.data) or
            not patern2.search(field.data) or
            not patern3.search(field.data)):
        # Хоть одно правило не сработает, то вызываем исключение
        raise ValidationError(msg)


# Добавим нашу функцию валидации пароля в формы
class RegistrationForm(FlaskForm):
    # Добавляем поле имени пользователя
    username = StringField("Имя:", validators=[DataRequired()])
    # Добавляем поле пароля
    password = PasswordField("Пароль:", validators=[DataRequired(),
                                                    Length(min=8, message="Пароль должен быть не менее 8 символов"),
                                                    EqualTo('confirm_password', message="Пароли не одинаковые"),
                                                    password_check])
    confirm_password = PasswordField("Пароль еще раз:", validators=[DataRequired()])


class ChangePasswordForm(FlaskForm):
    password = PasswordField(
        "Пароль:",
        validators=[
            DataRequired(),
            # Пароль не менее 8 символов
            Length(min=8, message="Пароль должен быть не менее 8 символов"),
            EqualTo('confirm_password', message="Пароли не одинаковые"),
            password_check
        ]
    )


...
