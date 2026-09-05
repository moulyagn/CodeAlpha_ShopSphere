from flask_wtf import FlaskForm
from wtforms import BooleanField, IntegerField, PasswordField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, InputRequired, Length, NumberRange, Optional, ValidationError


class RegistrationForm(FlaskForm):
    first_name = StringField("First name", validators=[DataRequired(), Length(min=2, max=80)])
    last_name = StringField("Last name", validators=[DataRequired(), Length(min=2, max=80)])
    email = StringField("Email address", validators=[DataRequired(), Email(), Length(max=255)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8, max=128)])
    confirm_password = PasswordField(
        "Confirm password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Create account")

    def validate_email(self, email):
        from models import User

        if User.query.filter_by(email=email.data.strip().lower()).first():
            raise ValidationError("An account with this email already exists.")


class LoginForm(FlaskForm):
    email = StringField("Email address", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember me")
    submit = SubmitField("Sign in")


class ForgotPasswordForm(FlaskForm):
    email = StringField("Email address", validators=[DataRequired(), Email()])
    submit = SubmitField("Send reset link")


class AddressForm(FlaskForm):
    label = StringField("Address label", validators=[DataRequired(), Length(max=80)])
    line_one = StringField("Address line", validators=[DataRequired(), Length(max=255)])
    line_two = StringField("Apartment / landmark", validators=[Optional(), Length(max=255)])
    city = StringField("City", validators=[DataRequired(), Length(max=120)])
    state = StringField("State", validators=[DataRequired(), Length(max=120)])
    postal_code = StringField("PIN code", validators=[DataRequired(), Length(min=6, max=6)])
    phone = StringField("Phone", validators=[DataRequired(), Length(min=10, max=15)])
    is_default = BooleanField("Make this my default address")
    submit = SubmitField("Save address")


class CheckoutForm(FlaskForm):
    address_id = SelectField("Delivery address", coerce=int, validators=[InputRequired()])
    shipping_method = SelectField("Shipping method", choices=[("Standard", "Standard · 3-5 days · ₹99"), ("Express", "Express · 1-2 days · ₹199")], validators=[DataRequired()])
    payment_method = SelectField("Payment method", choices=[("UPI", "UPI"), ("COD", "Cash on Delivery"), ("Debit Card", "Debit Card"), ("Credit Card", "Credit Card"), ("Net Banking", "Net Banking")], validators=[DataRequired()])
    card_details = StringField("Card number (mock)", validators=[Optional(), Length(min=4, max=19)])
    coupon_code = StringField("Coupon code", validators=[Optional(), Length(max=40)])
    submit = SubmitField("Pay securely · Mock payment")


class ProfileForm(FlaskForm):
    first_name = StringField("First name", validators=[DataRequired(), Length(min=2, max=80)])
    last_name = StringField("Last name", validators=[DataRequired(), Length(min=2, max=80)])
    email = StringField("Email address", validators=[DataRequired(), Email(), Length(max=255)])
    submit = SubmitField("Save profile")


class ReviewForm(FlaskForm):
    rating = IntegerField("Rating", validators=[InputRequired(), NumberRange(min=1, max=5)])
    comment = TextAreaField("Review", validators=[DataRequired(), Length(min=10, max=1000)])
    submit = SubmitField("Publish review")
