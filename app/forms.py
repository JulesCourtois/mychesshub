from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, EqualTo, Email, NumberRange
from app.models import Federation


class LoginForm(FlaskForm):
    username = StringField('E-mail', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegisterForm(FlaskForm):
    full_name = StringField("Full Name", validators=[DataRequired()])
    email = StringField("E-mail", validators=[DataRequired(), Email()])
    birth = IntegerField("Birth Year", validators=[DataRequired(), NumberRange(min=1990)])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField('Register')


class CreateTournamentForm(FlaskForm):
    federations = Federation.query.all()
    choices = []
    for federation in federations:
        choice = (federation.id, federation.initials)
        choices.append(choice)

    name = StringField("Name", validators=[DataRequired()])
    place = StringField("Place", validators=[DataRequired()])
    federation = SelectField(coerce=int, label="Federation", validators=[DataRequired()], choices=choices)

    start_date = StringField("Start Date", validators=[DataRequired()])
    end_date = StringField("Start Date", validators=[DataRequired()])
    rounds = IntegerField("Rounds", validators=[DataRequired()])
    play_system = StringField("Play System")

    move_rate = StringField("Move Rate")
    chief_arbiter = StringField("Chief Arbiter")
    deputy_arbiter = StringField("Deputy Arbiter")
    categories = StringField("Categories")
    information = StringField("Extra Information")
    submit = SubmitField("Create")
