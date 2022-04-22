from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired,Length

class LoginForm(FlaskForm): 
    username = StringField(
        'Username', 
        validators=[
            DataRequired(message='⚠️ USERNAME CANNOT BE EMPTY')
        ],
        render_kw={'placeholder':'USERNAME'}
    )

    password = PasswordField(
        'Password', 
        validators=[
            DataRequired(message='⚠️ USERNAME CANNOT BE EMPTY'), 
            Length(8,100)
        ], 
        render_kw={'placeholder':'PASSWORD'}
    )

    submit = SubmitField('Log in')
