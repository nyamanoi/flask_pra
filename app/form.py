from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    ValidationError,
    RadioField,
    PasswordField,
    SelectMultipleField
)
from wtforms.validators import DataRequired, Email, Optional


class Form(FlaskForm):
    email = StringField(
        "メールアドレス",
        validators=[
            DataRequired(),
            Email(message="メールアドレスの形式で入力してください。"),
        ],
        render_kw={"placeholder": "xxx@xxx.com"},
    )
    name = StringField("名前", validators=[DataRequired()])
    password = PasswordField("パスワード", validators=[DataRequired()])
    gender = RadioField(
        "性別", choices=[("男", "男"), ("女", "女")], validators=[Optional()]
    )
    post_code = StringField(
        "郵便番号", validators=[Optional()], render_kw={"placeholder": "000-0000"}
    )
    address = StringField(
        "住所", validators=[Optional()], render_kw={"placeholder": "〇〇県〇〇市"}
    )
    phone_number = StringField(
        "電話番号", validators=[Optional()], render_kw={"placeholder": "000-000-0000"}
    )


        
    licenses = SelectMultipleField(
        "取得資格",
        choices=[],
        validators=[Optional()],
        validate_choice=False,
    )

    def validate_email(self, email):
        if len(email.data) > 30:
            raise ValidationError("30文字以内で入力してください。")




    def validate_name(self, name):
        if len(name.data) > 16:
            raise ValidationError("16文字以内で入力してください。")

    def validate_password(self, password):
        if len(password.data) < 8:
            raise ValidationError("8文字以上で入力してください。")

    def validate_post_code(self, post_code):
        if len(post_code.data) > 8:
            raise ValidationError("8文字以内で入力してください。")

    def validate_address(self, address):
        if len(address.data) > 50:
            raise ValidationError("50文字以内で入力してください。")

    def validate_phone_number(self, phone_number):
        if len(phone_number.data) > 12:
            raise ValidationError("12文字以内で入力してください。")
